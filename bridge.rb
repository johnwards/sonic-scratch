# Local bridge between Scratch (TurboWarp) and Sonic Pi.
#
# Runs on the Ruby that ships inside Sonic Pi, so nothing else needs installing.
# Boots Sonic Pi's own daemon, reads the ports and auth token it prints, then
# serves a tiny HTTP API on localhost that the Scratch extension calls. Each
# POST /run becomes an OSC /run-code message to the Sonic Pi server.

require "socket"
require "json"
require "open3"
require "rbconfig"

HTTP_PORT = (ENV["PORT"] || 8000).to_i
EXT_FILE = File.join(__dir__, "sonic-pi-blocks.js")
EDITOR_URL = "https://turbowarp.org/editor?extension=http://localhost:#{HTTP_PORT}/sonic-pi-blocks.js"

def windows?
  RbConfig::CONFIG["host_os"] =~ /mswin|mingw|cygwin/
end

# ---------- find Sonic Pi ----------
def find_server_dir
  return ENV["SONIC_PI_SERVER"] if ENV["SONIC_PI_SERVER"]
  # If we're running on Sonic Pi's bundled Ruby, it lives at <server>/native/ruby/bin/ruby
  from_ruby = File.expand_path("../../../..", RbConfig.ruby)
  return from_ruby if File.exist?(File.join(from_ruby, "ruby", "bin", "daemon.rb"))
  candidates = [
    "/Applications/Sonic Pi.app/Contents/Resources/app/server",
    File.join(ENV["ProgramFiles"] || "C:/Program Files", "Sonic Pi", "app", "server"),
    File.join(ENV["LOCALAPPDATA"] || "", "Programs", "Sonic Pi", "app", "server"),
    "/opt/sonic-pi/app/server",
    "/usr/lib/sonic-pi/app/server",
  ]
  candidates.find { |c| File.exist?(File.join(c, "ruby", "bin", "daemon.rb")) }
end

SERVER = find_server_dir
unless SERVER
  warn "Can't find Sonic Pi. Install it from https://sonic-pi.net or set SONIC_PI_SERVER."
  exit 1
end

require File.join(SERVER, "ruby", "paths")
require File.join(SERVER, "ruby", "lib", "sonicpi", "osc", "osc")

# ---------- state ----------
$state = { ready: false, runs: 0, last_message: "", last_error: "" }
$ports = nil
$token = nil
$to_spider = nil
$lock = Mutex.new
# Beat cues from Sonic Pi (each live loop cues its own name every time round,
# and `cue :name` in user code). Scratch long-polls these to animate in time.
$events = []          # [seq, name, at_ms]
$seq = 0
$ev_lock = Mutex.new
$ev_cv = ConditionVariable.new
# Sonic Pi schedules audio this far ahead of the logical time it reports.
SCHED_AHEAD_MS = (ENV["SCHED_AHEAD_MS"] || 500).to_i

def log(msg)
  $stdout.puts msg
  $stdout.flush
end

def run_code(code)
  raise "Sonic Pi is still booting" unless $state[:ready]
  $lock.synchronize { $state[:runs] += 1; $state[:last_error] = "" }
  log "\n>> run #{$state[:runs]}\n#{code}"
  $to_spider.send("/run-code", $token, code)
end

def stop_all
  return unless $state[:ready]
  log ">> stop all"
  $to_spider.send("/stop-all-jobs", $token)
end

def open_browser(url)
  return if ENV["NO_OPEN"]
  if windows?
    system("cmd", "/c", "start", "", url)
  elsif RbConfig::CONFIG["host_os"] =~ /darwin/
    system("open", url)
  else
    system("xdg-open", url)
  end
rescue StandardError
end

def print_instructions
  log <<~TXT

    ==========================================================
     Scratch should now open in your browser. If it doesn't, go to:
       #{EDITOR_URL}
     The first time, your browser asks whether turbowarp.org may
     connect to devices on your local network. Click Allow.
     Keep this window open while you play. Close it to stop.
    ==========================================================
  TXT
end

# ---------- boot the daemon ----------
log "Booting Sonic Pi from #{SERVER} ..."
# Host gem settings would make the bundled Ruby look in the wrong place.
daemon_env = { "GEM_PATH" => nil, "GEM_HOME" => nil }
daemon_in, daemon_out, daemon_thr = Open3.popen2e(daemon_env, SonicPi::Paths.ruby_path, SonicPi::Paths.daemon_path, "--no-scsynth-inputs")

first_line = daemon_out.gets
nums = first_line.to_s.split.map { |s| Integer(s, exception: false) }
if nums.size < 6 || nums.any?(&:nil?)
  warn "Unexpected output from the Sonic Pi daemon: #{first_line.inspect}"
  warn daemon_out.read
  exit 1
end
$ports = { daemon: nums[0], listen: nums[1], send: nums[2], scsynth: nums[3], cues: nums[4] }
$token = nums[5]
log "Daemon up. Ports: #{$ports}"

Thread.new do
  daemon_out.each_line { |l| $stderr.puts "[daemon] #{l}" }
  log "Sonic Pi daemon exited. Stopping bridge."
  exit 1
end

to_daemon = SonicPi::OSC::UDPClient.new("127.0.0.1", $ports[:daemon])
$to_spider = SonicPi::OSC::UDPClient.new("127.0.0.1", $ports[:send])

# The daemon shuts everything down if it stops hearing from us.
Thread.new { loop { to_daemon.send("/daemon/keep-alive", $token); sleep 4 } }

def shutdown(to_daemon)
  log "\nShutting down Sonic Pi..."
  to_daemon.send("/daemon/exit", $token) rescue nil
  sleep 0.5
  exit 0
end
trap("INT") { shutdown(to_daemon) }
trap("TERM") { shutdown(to_daemon) } unless windows?

# Listen where the GUI would, so we see /ack, log lines and errors.
from_spider = SonicPi::OSC::UDPServer.new($ports[:listen], name: "scratch-bridge") do |address, args, _sender|
  log "[osc] #{address} #{args.inspect}" if ENV["DEBUG"]
end
from_spider.add_method("/ack") do |_|
  unless $state[:ready]
    $state[:ready] = true
    log "Sonic Pi is ready. Open Scratch and make some noise!"
    $to_spider.send("/mixer-output-volume", $token, 0.6, 1)
    print_instructions
    open_browser(EDITOR_URL)
  end
end
from_spider.add_method("/log/info") do |args|
  $state[:last_message] = args[1].to_s
  log "[sonic pi] #{args[1]}"
end
from_spider.add_method("/log/multi_message") do |args|
  # [job_id, thread_name, time, size, colour, msg, colour, msg, ...]
  args[4..].to_a.each_slice(2) do |_colour, msg|
    $state[:last_message] = msg.to_s
    log "[sonic pi] #{msg}"
  end
end
from_spider.add_method("/incoming/osc") do |args|
  time_str, _id, path, _osc_args = args
  next unless path.is_a?(String) && path =~ %r{\A/(live_loop|cue)/(.+)}
  name = $2
  at_ms = (Rational(time_str) * 1000).to_f + SCHED_AHEAD_MS rescue (Time.now.to_f * 1000)
  log "[cue] #{name} in #{(at_ms - Time.now.to_f * 1000).round}ms" if ENV["DEBUG"]
  $ev_lock.synchronize do
    $seq += 1
    $events << [$seq, name, at_ms]
    $events.shift while $events.size > 500
    $ev_cv.broadcast
  end
end
["/error", "/syntax_error"].each do |addr|
  from_spider.add_method(addr) do |args|
    $state[:last_error] = "#{args[1]} (line #{args[3]})"
    log "[sonic pi ERROR] #{$state[:last_error]}"
  end
end

Thread.new do
  until $state[:ready]
    $to_spider.send("/ping", $token, "hello from scratch bridge") rescue nil
    sleep 0.5
  end
end

# ---------- HTTP API for the Scratch extension ----------
CORS = {
  "Access-Control-Allow-Origin" => "*",
  "Access-Control-Allow-Headers" => "Content-Type",
  "Access-Control-Allow-Methods" => "GET, POST, OPTIONS",
  "Access-Control-Allow-Private-Network" => "true",
}

def respond(sock, status, type, body, extra = {})
  body = body.to_s
  headers = CORS.merge("Content-Type" => type, "Content-Length" => body.bytesize.to_s, "Connection" => "close").merge(extra)
  sock.write "HTTP/1.1 #{status}\r\n"
  headers.each { |k, v| sock.write "#{k}: #{v}\r\n" }
  sock.write "\r\n"
  sock.write body
end

def handle(sock)
  request = sock.gets or return
  method, target = request.split(" ")
  path = target.to_s.split("?").first
  headers = {}
  while (line = sock.gets) && line.strip != ""
    k, v = line.split(":", 2)
    headers[k.downcase] = v.strip if v
  end
  body = headers["content-length"] ? sock.read(headers["content-length"].to_i) : ""

  case [method, path]
  when ["OPTIONS", path]
    respond(sock, "204 No Content", "text/plain", "")
  when ["GET", "/sonic-pi-blocks.js"]
    respond(sock, "200 OK", "text/javascript", File.read(EXT_FILE), "Cache-Control" => "no-store")
  when ["GET", "/status"]
    respond(sock, "200 OK", "application/json", JSON.generate(
      ready: $state[:ready], booting: !$state[:ready], runs: $state[:runs],
      lastMessage: $state[:last_message], lastError: $state[:last_error]
    ))
  when ["GET", "/events"]
    # Long-poll: returns cues with seq > since, waiting up to a second for new ones.
    # since=-1 means "just tell me the current seq".
    since = (target.to_s[/since=(-?\d+)/, 1] || "0").to_i
    evs = []
    $ev_lock.synchronize do
      if since >= 0
        $ev_cv.wait($ev_lock, 1.0) if $events.empty? || $events.last[0] <= since
        evs = $events.select { |e| e[0] > since }
      end
      respond(sock, "200 OK", "application/json", JSON.generate(
        seq: $seq, now: (Time.now.to_f * 1000).round,
        events: evs.map { |sq, name, at| { seq: sq, name: name, at: at.round } }
      ))
    end
  when ["POST", "/run"]
    code = (JSON.parse(body) rescue {})["code"]
    if code.is_a?(String) && !code.strip.empty?
      run_code(code)
      respond(sock, "200 OK", "application/json", '{"ok":true}')
    else
      respond(sock, "400 Bad Request", "application/json", '{"error":"no code"}')
    end
  when ["POST", "/stop"]
    stop_all
    respond(sock, "200 OK", "application/json", '{"ok":true}')
  else
    respond(sock, "404 Not Found", "application/json", '{"error":"not found"}')
  end
rescue StandardError => e
  respond(sock, "500 Internal Server Error", "application/json", JSON.generate(error: e.message)) rescue nil
ensure
  sock.close rescue nil
end

servers = []
# Browsers may try ::1 before 127.0.0.1 for "localhost", so listen on both where possible.
["127.0.0.1", "::1"].each do |host|
  begin
    servers << TCPServer.new(host, HTTP_PORT)
  rescue StandardError => e
    warn "Could not listen on #{host}:#{HTTP_PORT} (#{e.message})" if host == "127.0.0.1"
  end
end
if servers.empty?
  warn "Port #{HTTP_PORT} is busy. Is another copy of the bridge already running?"
  shutdown(to_daemon)
end
log "Bridge listening on http://localhost:#{HTTP_PORT}"

servers.each do |server|
  Thread.new do
    loop do
      sock = server.accept
      Thread.new(sock) { |s| handle(s) }
    end
  end
end

sleep
