from kivy.graphics import Color, Rectangle
from kivy.properties import ColorProperty
from kivy.uix.boxlayout import BoxLayout


class BoxLayoutBackground(BoxLayout):
    background_color = ColorProperty([0.0, 0.0, 0.0, 0.0])

    """
    Everything like a BoxLayout but manages to set its background color when this
    one same property is set.
    """

    def __init__(self, **kwargs):
        super(BoxLayoutBackground, self).__init__(**kwargs)

        with self.canvas.before:
            Color(self.background_color)
            Color(1.0, 0.0, 0.0, 1.0)
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
