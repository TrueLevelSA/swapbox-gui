[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

README
------

This is ALPHA software.  Here be dragons!  Use at your own risk.

Contributions very! welcome!  0x64C9988A6C6EF250074D9A2d5df73a59d0292dd8

Dependencies (Linux/mac)
------------

Python3
Pipenv
zbarcam (qr scanner)

### Install zbar
```
# on mac:
brew install zbar

# on ubuntu:
apt-get install zbar-tools

# on linux:
apt-get install zbar
```

Dependencies (RasPi)
------------

Python3
Pipenv
RaspberryPi camera module

Installation
------------
```
# Install python deps
pipenv install
# Install eSSP (until install with pipenv is fixed)
pipenv run pip3 install git+https://github.com/Minege/eSSP
```

Running
-------
```
pipenv run python template.py develop
```

### Simulating Note validator with develop config
```
pipenv run python mock_validator.py
```

### Simulating swap-box-web3 status with develop config
```
pipenv run python mock_status.py
```

### Simulating swap-box-web3 price feed with develop config
```
pipenv run python mock_pricefeed.py
```

### Simulating swap-box-web3 transactions with develop config
```
pipenv run python mock_web3.py
```

RaspberryPi Setup Instructions
------------------------------

*   RaspberryPi (4 B+ recommended)

Follow instructions in [clean_install.md](./clean_install.md)

For inverted screen (black machine)
-------------------

in /home/pi/.kivy/config.ini to invert touch x axis:

    [input]
    mouse = mouse
    %(name)s = probesysfs,provider=hidinput,param=invert_x=1

in /boot/config.txt to set resolution for shitty screen (480x848)

    hdmi_group=2
    hdmi_mode=14

in /boot/config.txt to rotate screen 180 deg:

    display_rotate=2

Running
-------
```
DISPLAY=:0 KIVY_GL_BACKEND=sdl2 KIVY_WINDOW=sdl2 pipenv run python template.py develop_pi
```

TO-DO
-----
- Helper function for price calculations (using Decimal+Quantize more accurate and cleaner in .kv)
- Get txid back from swap-box-web3 and show on final_buy_screen
- Admin interface??
- Multi token support
- Multi fiat currency support ?
