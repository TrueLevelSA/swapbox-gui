[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

README
------

This is ALPHA software.  Here be dragons!  Use at your own risk.

Contributions very! welcome!  0x64C9988A6C6EF250074D9A2d5df73a59d0292dd8
or @ [Gitcoin](https://gitcoin.co/grants/403/swap-box)

Dependencies
------------

- Python3
- [Pipenv](https://github.com/pypa/pipenv#installation)

For local development:
- [Zbarcam](doc/install-zbarcam.md)

On RasperryPI:
- [RaspberryPi camera module](https://www.raspberrypi.org/documentation/accessories/camera.html#installing-a-raspberry-pi-camera)


Installation
------------
```
# Install python deps
pipenv install
# Install eSSP (until install with pipenv is fixed)
pipenv run pip3 install git+https://github.com/TrueLevelSA/eSSP
```
For RaspberryPi see [clean_install.md](doc/clean_install.md) and [setup-notes.md](doc/setup-notes.md)


Running (development)
-------
- In a terminal run:
```
./mock_all.sh
```
*This will allow you to control simulated note validator & dispenser*

- In another terminal run:
```
pipenv run python template.py develop
```

Running (RaspberryPi)
-------
```
DISPLAY=:0 KIVY_GL_BACKEND=sdl2 KIVY_WINDOW=sdl2 pipenv run python template.py develop_pi
```


Licence
-------

[License: AGPL v3](/LICENCE.md)
Copyright &copy; TrueLevel SA


Contributors
------------

@tshabs
@samouraid3
@Minege
@megaturbo
@ymaktepi
@0xjac
@roflolilolmao


Similar Projects
----------------

- [LightningATM](https://github.com/21isenough/LightningATM)
- [Skyhook](https://github.com/mythril/skyhook/)