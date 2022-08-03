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

from kivy.uix.screenmanager import Screen


class ScreenSetup(Screen):
    def cancel(self):
        self.manager.transition.direction = "up"
        self.manager.current = "menu"


class ScreenSetup1(ScreenSetup):
    def next(self):
        self.manager.transition.direction = "left"
        self.manager.current = "setup_2"

    @staticmethod
    def generate_key():
        # TODO: should probably check with the node if key exist
        # TODO: if not, send an instruction to the node to generate a key
        print("NotImplemented: GENERATE KEY")

    @staticmethod
    def import_key():
        print("NotImplemented: IMPORT KEY")


class ScreenSetup2(ScreenSetup):
    def back(self):
        self.manager.transition.direction = "right"
        self.manager.current = "setup_1"

    def next(self):
        self.manager.transition.direction = "left"
        self.manager.current = "setup_3"

    @staticmethod
    def scan_address():
        print("NotImplemented: SCAN ADDRESS QR")


class ScreenSetup3(ScreenSetup):
    def back(self):
        self.manager.transition.direction = "right"
        self.manager.current = "setup_2"

    def finish(self):
        print("NotImplemented: Finish setup")
        super().cancel()
