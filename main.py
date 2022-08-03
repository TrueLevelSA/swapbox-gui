# Swap-box
# Copyright (C) 2019  TrueLevel SA
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import kivy
from kivy.config import Config as KivyConfig
from kivy.core.window import Window

from src.app.app import TemplateApp
from src.config import Config
from src.config import parse_args as parse_args

kivy.require("2.0.0")


def set_kivy_log_level(debug: bool):
    if debug:
        KivyConfig.set('kivy', 'log_level', 'debug')
    else:
        KivyConfig.set('kivy', 'log_level', 'warning')
    KivyConfig.write()


def set_window(fullscreen: bool):
    Window.size = (1280, 720)
    if fullscreen:
        Window.fullscreen = True
        Window.show_cursor = False


def main():
    args = parse_args()
    config = Config(args.config)

    set_kivy_log_level(config.debug)
    set_window(config.is_fullscreen)

    app = TemplateApp(config)
    app.run()


if __name__ == '__main__':
    main()
