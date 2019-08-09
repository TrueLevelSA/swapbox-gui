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
        self.ZMQ_URL_MOCK_VALIDATOR = None
        self.NOTE_VALIDATOR_NV11 = None
        self.VALIDATOR_PORT = None
        self.ZMQ_URL_PRICEFEED = None
        self.NOTES_VALUES = None
        self.ZMQ_URL_RPC = None
        self.LED_DRIVER = None
        self.CASHIN_THREAD = None
        self.QR_SCANNER = None
        self.PRICEFEED = None
        self.NODE_RPC = None
        self.IS_FULLSCREEN = None
        self.ZMQ_URL_STATUS = None
        self.STATUS = None

    @staticmethod
    def _select_led_driver(config):
        if config.RELAY_METHOD is RelayMethod.PIFACE:
            from led_driver.piface_led_driver import LedDriverPiFace
            return LedDriverPiFace()
        elif config.RELAY_METHOD is RelayMethod.GPIO:
            from led_driver.gpio_led_driver import LedDriverGPIO
            return LedDriverGPIO()
        else:
            from led_driver.no_led_driver import LedDriverNone
            return LedDriverNone()

    @staticmethod
    def _select_cashin_thread(config, callback):
        if config.MOCK_VALIDATOR is True:
            from cashin_driver.mock_cashin_driver import MockCashinDriver
            return MockCashinDriver(callback, config.ZMQ_URL_MOCK_VALIDATOR)
        else:
            from cashin_driver.essp_cashin_driver import EsspCashinDriver
            return EsspCashinDriver(callback, config.VALIDATOR_PORT)

    @staticmethod
    def _select_qr_scanner(config):
        if CameraMethod[config.CAMERA_METHOD] is CameraMethod.ZBARCAM:
            from qr_scanner.zbar_qr_scanner import QrScannerZbar
            return QrScannerZbar(config.ZBAR_VIDEO_DEVICE)
        elif CameraMethod[config.CAMERA_METHOD] is CameraMethod.OPENCV:
            from qr_scanner.opencv_qr_scanner import QrScannerOpenCV
            return QrScannerOpenCV()
        else:
            from qr_scanner.none_qr_scanner import QrScannerNone
            return QrScannerNone()

    @staticmethod
    def _select_pricefeed(config, callback_pricefeed):
        from custom_threads.zmq_pricefeed import ZMQPriceFeed
        return ZMQPriceFeed(callback_pricefeed, config.ZMQ_URL_PRICEFEED)

    @staticmethod
    def _select_status(config, callback_status):
        from custom_threads.zmq_status import ZMQStatus
        return ZMQStatus(callback_status, config.ZMQ_URL_STATUS)

    @staticmethod
    def _select_node_rpc(config):
        from node_rpc.node_rpc import NodeRPC
        return NodeRPC(config.ZMQ_URL_RPC)

    @staticmethod
    def _select_all_drivers(config, callback_cashin, callback_pricefeed, callback_status):
        config.LED_DRIVER = Config._select_led_driver(config)
        config.QR_SCANNER = Config._select_qr_scanner(config)
        config.CASHIN_THREAD = Config._select_cashin_thread(config, callback_cashin)
        config.PRICEFEED = Config._select_pricefeed(config, callback_pricefeed)
        config.NODE_RPC = Config._select_node_rpc(config)
        config.STATUS = Config._select_status(config, callback_status)

def print_debug(*args, **kwargs):
    print("PLEASE USE Logger.debug/Logger.info/...")
    print(*args, **kwargs)


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
    valid_true_values = ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly']
    config = Config()
    config.DEBUG = machine_config.get("debug").lower() in valid_true_values
    config.CAMERA_METHOD = machine_config.get("camera_method")
    config.ZBAR_VIDEO_DEVICE = machine_config.get("camera_device")
    config.RELAY_METHOD = machine_config.get("relay_method")
    config.MOCK_VALIDATOR = machine_config.get("mock_validator").lower() in valid_true_values
    config.ZMQ_URL_MOCK_VALIDATOR = machine_config.get("zmq_url_mock_validator")
    config.NOTE_VALIDATOR_NV11 = machine_config.get("validator_nv11").lower() in valid_true_values
    config.VALIDATOR_PORT = machine_config.get("validator_port")
    config.ZMQ_URL_PRICEFEED = machine_config.get("zmq_url_pricefeed")
    config.NOTES_VALUES = ["10", "20", "50", "100", "200"]
    config.ZMQ_URL_RPC = machine_config.get("zmq_url_rpc")
    config.ZMQ_URL_STATUS = machine_config.get("zmq_url_status")
    config.IS_FULLSCREEN = machine_config.get("is_fullscreen").lower in valid_true_values

    if not os.uname()[4].startswith("arm"):
        config.RELAY_METHOD = RelayMethod.NONE

    return config

