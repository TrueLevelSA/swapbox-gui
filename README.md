README
------

This project provides a lovely kivy interface for ATM4COIN

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
```

Dependencies (RasPi)
------------

Python3
Pipenv

Installation
------------
```
# Install python deps
pipenv install
```

Running
-------
```
pipenv run python main.py develop
```

### Simulating Note validator with develop config
```
pipenv run python mock_validator.py
```


Setup Instructions
------------------

*   RaspberryPi (2 B+ recommended)
*   Olimex (A20 Micro recommended)


Performance stuff
-----------------

in /boot/config.txt set:

    gpu_mem=256

in /etc/uv4l/uv4l-raspicam.conf To adjust raspberry preview window size and location:



For inverted screen (bblack machine)
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

Run (with logfile)
------------------

    python main.py > logoutput.txt


TO-DO
-----
- Helper function for price calculations (using Decimal+Quantize more accurate and cleaner in .kv)
- Get txid back from swap-box-web3 and show on final_buy_screen
- Admin interface??
- Multi token support
- Multi fiat currency support ?
