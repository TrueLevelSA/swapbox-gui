#!/bin/bash

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
cd $SCRIPTPATH
while true
do
	DISPLAY=:0 KIVY_GL_BACKEND=sdl2 KIVY_WINDOW=sdl2 pipenv run python template.py develop_pi > ./log.log
	sleep 1
done
