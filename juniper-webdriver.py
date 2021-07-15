#!/usr/bin/python

import argparse
import signal
import subprocess
import sys
import time

from selenium import webdriver

parser = argparse.ArgumentParser()
parser.add_argument('gateway', help='URL of the (web-based) authentication page')
parser.add_argument('server', help='Server name for the (post-authentication) VPN connection')
parser.add_argument('--print-cookie', help='Whether to print the authentication cookie',
  action='store_true')
parser.add_argument('--sudo', help='command used to run `sudo`',
  default='sudo')
parser.add_argument('--openconnect', help='command used to run `openconnect`',
  default='openconnect')
args = parser.parse_args()

try:
  driver = webdriver.Firefox()
  driver.get(args.gateway)
  dsid = None
  while True:
    for cookie in driver.get_cookies():
      if cookie['name'] == 'DSID':
        dsid = cookie['value']
        if args.print_cookie:
          print(f'DSID={dsid}')
        break
    if dsid is not None:
      break
    time.sleep(0.2)

  time.sleep(1)

  driver.quit()
except:
  print(f'Exception while interacting with the browser.  The exception was:')
  raise

subprocess.run(['sudo', 'true']) # Ensure sudo doesn't grab stdin of the next command
proc = subprocess.Popen(
  [args.sudo,
    args.openconnect,
    '--protocol=nc', # Juniper Network Connect
    '--cookie-on-stdin', # Use stdin to avoid cookie leaking to the process arguments
    args.server],
  stdin=subprocess.PIPE,
  universal_newlines=True)

proc.stdin.write(f'DSID={dsid}')
proc.stdin.close()

# Pass-through the signals that `openconnect` understands
def handler(signum, frame):
  proc.send_signal(signum)
for sig in [signal.SIGINT, signal.SIGTERM, signal.SIGHUP, signal.SIGUSR2]:
  signal.signal(sig, handler)

while True:
  returncode = proc.poll()
  if returncode is not None:
    break
  time.sleep(0.1)

sys.exit(returncode)
