# i installed each package globally through pip3
# also, opencv was installed using apt
sudo apt install python3-opencv --fix-missing
# to launch: (might need reboot?)
DISPLAY=:0 KIVY_GL_BACKEND=sdl2 KIVY_WINDOW=sdl2 python3 template.py develop
# comment @lxpanel line in /etc/xdg/lxsession/LXDE-pi/autostart
# add gpu_mem=512 in /boot/config.txt
# add ",param=invert_y=0" to the "%(name)s = probesysfs,provider=hidinput" line under [input]
# in ~/.kivy/config.ini
# install opencv, zbar, uv4l, and compile our custom zbar following instructions in qr_scanner/zbar_c

# to be merged to Minege's repo and added back to pipfile
pipenv run python -m pip install git+https://github.com/ymaktepi/eSSP@upgrades
# to map any note validator to port /dev/note_validator, see config/99-essp.rules
