# Juniper WebDriver

A script for connecting to a Pulse AnyConnect VPN using `openconnect`.

## License

[MIT License](./LICENSE)

## Requirements

Installed programs:

- [`openconnect`](https://www.infradead.org/openconnect/)
- a WebDriver implementation such as
  - [geckodriver](https://github.com/mozilla/geckodriver) for Firefox or
  - [chromedriver](https://chromedriver.chromium.org/) for Chrome.

Required Python packages:

- [Selenium](https://pypi.org/project/selenium/) (Install with `pip install selenium`)

## Usage

Run `juniper-webdriver.py` with appropriate arguments specifying:

- the WebDriver implementation,
- the VPN login page, and
- the VPN server.

For example, you might run:

    juniper-webdriver.py firefox https://webvpn.example.com/stf webvpn.example.com

This will launch `https://webvpn.example.com/stf` in a new Firefox browser
window.

You should then log into your VPN account using that browser.

Once you are successfully logged in, the script will automatically extract your
credentials from the browser and close the browser window.

The script will then connect to the VPN server (`webvpn.example.com`) using
`openconnect` and the credentials from the browser window.  Note that
`openconnect` is run under `sudo`, it may prompt you for your `sudo` password.

At this point, your VPN connection will be open and available for you to use.

When you want to close your VPN connection, just press Ctrl-C in the terminal
where you launched the script.
