from enum import auto, Enum
import argument
import strictyaml
from path import Path
import os

class CameraMethod(Enum):
    ZBARCAM = auto()
    OPENCV = auto()
    KIVY = auto()

class RelayMethod(Enum):
    PIFACE = auto()
    GPIO = auto()
    NONE = auto()


class Config(object):

    def __init__(self):
        self.DEBUG = None
        self.CAMERA_METHOD= None
        self.ZBAR_VIDEO_DEVICE = None
        self.RELAY_METHOD = None
        self.MOCK_VALIDATOR = None
        self.MOCKPORT = None
        self.NOTE_VALIDATOR_NV11 = None
        self.VALIDATOR_PORT = None
        self.ZMQ_PORT = None
        self.NOTES_VALUES = None


def parse_args():
    # Get config file as required arguemnt and load
    f = argument.Arguments()
    f.always("config", help="Machine Config file name")
    arguments, errors = f.parse()

    if arguments.get("config") is not None:
        machine_config = strictyaml.load(Path("machine_config/%s.yaml" % arguments.get("config")).bytes().decode('utf8')).data
    else:
        print("Config file must be specified")
        exit(0)

    config = Config()
    config.DEBUG = machine_config.get("debug")
    config.CAMERA_METHOD = machine_config.get("camera_method")
    config.ZBAR_VIDEO_DEVICE = machine_config.get("camera_device")
    config.RELAY_METHOD = machine_config.get("relay_method")
    config.MOCK_VALIDATOR = machine_config.get("mock_validator")
    config.MOCKPORT = machine_config.get("mock_port")
    config.NOTE_VALIDATOR_NV11 = machine_config.get("validator_nv11")
    config.VALIDATOR_PORT = machine_config.get("validator_port")
    config.ZMQ_PORT = machine_config.get("zmq_port")
    config.NOTES_VALUES = ["10", "20", "50", "100", "200"]


    # For pifacedigital relay
    if os.uname()[4].startswith("arm"):
        if RelayMethod[config.RELAY_METHOD] is RelayMethod.PIFACE:
            import pifacedigitalio
        elif RelayMethod[config.RELAY_METHOD] is RelayMethod.GPIO:
            import RPi.GPIO as GPIO
            GPIO.cleanup()
    else:
        config.RELAY_METHOD = None

    return config

