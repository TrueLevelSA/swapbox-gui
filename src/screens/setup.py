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
