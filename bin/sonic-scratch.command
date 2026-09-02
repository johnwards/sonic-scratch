#!/bin/bash
# Starts the Sonic Scratch bridge in this Terminal window.
printf '\033]0;Sonic Scratch\a'
cd "$(dirname "$0")/.."

RUBY="/Applications/Sonic Pi.app/Contents/Resources/app/server/native/ruby/bin/ruby"
if [ ! -x "$RUBY" ]; then
  echo "Sonic Pi was not found in /Applications."
  echo "Install it from https://sonic-pi.net and try again."
  read -r -n1 -p "Press any key to close."
  exit 1
fi

# Host gem settings would make Sonic Pi's Ruby look in the wrong place.
unset GEM_PATH GEM_HOME
"$RUBY" bridge.rb
status=$?
if [ $status -ne 0 ]; then
  echo
  read -r -n1 -p "Something went wrong (exit $status). Press any key to close."
fi
