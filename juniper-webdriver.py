#!/usr/bin/env python3

"""Connect to a Pulse AnyConnect VPN using `openconnect`."""

import argparse
import signal
import subprocess
import sys
import textwrap
import time

from selenium import webdriver

################################################################################
# Command line argument parsing
################################################################################

webdrivers = {
  'android': webdriver.android.webdriver.WebDriver,
  'blackberry': webdriver.blackberry.webdriver.WebDriver,
  'chrome': webdriver.chrome.webdriver.WebDriver,
  'edge': webdriver.edge.webdriver.WebDriver,
  'firefox': webdriver.firefox.webdriver.WebDriver,
  'ie': webdriver.ie.webdriver.WebDriver,
  'opera': webdriver.opera.webdriver.WebDriver,
  'phantomjs': webdriver.phantomjs.webdriver.WebDriver,
  'safari': webdriver.safari.webdriver.WebDriver,
  'webkitgtk': webdriver.webkitgtk.webdriver.WebDriver,
}

parser = argparse.ArgumentParser(
  description=textwrap.dedent('''\
    Connect to a Pulse AnyConnect VPN using `openconnect`.

    Usage example:

        %(prog)s firefox https://webvpn.example.com/stf webvpn.example.com
    '''),
  fromfile_prefix_chars='@',
  formatter_class=argparse.RawDescriptionHelpFormatter)

parser.add_argument('webdriver',
  help=f'''which WebDriver implementation to use (choose from \
    {', '.join([f"'{x}'" for x in sorted(webdrivers)])})''',
  metavar='WEBDRIVER',
  choices=sorted(webdrivers))
parser.add_argument('gateway',
  help='URL of the authentication web page',
  metavar='GATEWAY',)
parser.add_argument('server',
  metavar='SERVER',
  help='server name of the post-authentication VPN server')

parser.add_argument('--sudo',
  help='program used to run `sudo` (default: %(default)s)',
  metavar='FILE',
  default='sudo')
parser.add_argument('--openconnect',
  help='program used to run `openconnect (default: %(default)s)`',
  metavar='FILE',
  default='openconnect')

debugging = parser.add_argument_group('debugging')
debugging.add_argument('--print-cookie',
  help='print the authentication cookie',
  action='store_true')
debugging.add_argument('--webdriver-log',
  help='file to use for the webdriver log (default: %(default)s)',
  metavar='FILE',
  default='/dev/null')

args = parser.parse_args()

print()
print('########################################################')
print('## Please login using the browser window that appears ##')
print('########################################################')
print()

try:
  driver = webdrivers[args.webdriver](service_log_path=args.webdriver_log)
  driver.get(args.gateway)
  dsid = None
  while True:
    for cookie in driver.get_cookies():
      if cookie['name'] == 'DSID':
        dsid = cookie['value']
        if args.print_cookie:
          print()
          print('###########################################')
          print('## Got authentication token: DSID={dsid} ##')
          print('###########################################')
          print()
          print(f'DSID={dsid}')
          print()
        break
    if dsid is not None:
      break
    time.sleep(0.2)

  time.sleep(1)

  driver.quit()
except BaseException:
  print()
  print('##################################################')
  print('## Exception while interacting with the browser ##')
  print('##################################################')
  print()
  raise

print()
print('####################################################')
print('## Connecting to the VPN                          ##')
print('##                                                ##')
print('## Please enter your `sudo` password if prompted. ##')
print('## Press Ctrl-C to close the connection.          ##')
print('####################################################')
print()

proc = subprocess.Popen(  # nosec: B603
  [args.sudo,
    args.openconnect,
    '--protocol=nc',  # Juniper Network Connect (also works for Pulse AnyConnect)
    '--cookie-on-stdin',  # Use stdin so the authentication token doesn't leak through the process arguments
    args.server],
  stdin=subprocess.PIPE,
  universal_newlines=True)

# Send the authentication token
if proc.stdin is None:
  raise RuntimeError('Failed to open pipe to stdin of `openconnect`')
proc.stdin.write(f'DSID={dsid}')
proc.stdin.close()


# Forward signals that `openconnect` understands
for sig in [signal.SIGINT, signal.SIGTERM, signal.SIGHUP, signal.SIGUSR2]:
  def handler(signum, frame):
    """Forward a signal to `openconnect`."""
    proc.send_signal(signum)
  signal.signal(sig, handler)

# Wait for `openconnect` to exit
while True:
  returncode = proc.poll()
  if returncode is not None:
    break
  time.sleep(0.1)

# Return with the exit code from `openconnect`
sys.exit(returncode)
