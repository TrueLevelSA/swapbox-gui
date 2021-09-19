### Simulating Note validator with develop config
```
pipenv run python mock_services/mock_validator.py
```

### Simulating swap-box-web3 status with develop config
```
pipenv run python mock_services/mock_status.py [--verbose]
```

### Simulating swap-box-web3 price feed with develop config
```
pipenv run python mock_services/mock_pricefeed.py [--verbose]
```

### Simulating swap-box-web3 transactions with develop config
```
pipenv run python mock_services/mock_web3.py
```


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