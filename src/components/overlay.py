#  Swap-box
#  Copyright (c) 2022 TrueLevel SA
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from kivy.lang import Builder
from kivy.uix.modalview import ModalView

Builder.load_string('''
<OverlayNotSync>:
    LabelSB:
        text_id: "not_sync"
        font_size: 40
        font_name: 'SpaceGrotesk'

''')


class OverlayNotSync(ModalView):
    def __init__(self, **kwargs):
        super(OverlayNotSync, self).__init__(**kwargs)

        # adds a boolean to easily check it's current state
        self.visible = False

    def open(self, *largs, **kwargs):
        if not self.visible:
            super(OverlayNotSync, self).open(*largs, **kwargs)
        self.visible = True

    def dismiss(self, *largs, **kwargs):
        if self.visible:
            super(OverlayNotSync, self).dismiss(*largs, **kwargs)
        self.visible = False
