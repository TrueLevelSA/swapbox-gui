README
------

This project provides a lovely kivy interface for ATM4COIN

Dependencies
------------

Kivy >= 1.8.0
zbarcam (qr scanner)
devilspie2

# Install zbar
    on mac:
    $ brew install zbar

    on ubuntu:
    $ apt-get install zbar-tools


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
