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
import argparse
from enum import auto, Enum
import strictyaml
from strictyaml import Seq, Str, Map, Bool, Int, Float
from path import Path
import os

from src_backends.custom_threads.zmq_subscriber import ZMQSubscriber
from src_backends.node_rpc.node_rpc import NodeRPC
from src_backends.qr_generator.qr_generator import QRGenerator


class CameraMethod(Enum):
    ZBARCAM = auto()
    OPENCV = auto()
    KIVY = auto()


class RelayMethod(Enum):
    PIFACE = auto()
    GPIO = auto()
    NONE = auto()


class Config(object):
    _schema = Map({
        "name": Str(),
        "debug": Bool(),
        "currency": Str(),
        "mock_validator": Bool(),
        "zmq_url_mock_validator": Str(),
        "validator_port": Str(),
        "validator_nv11": Bool(),
        "camera_method": Str(),
        "camera_device": Str(),
        "zmq_url_pricefeed": Str(),
        "zmq_url_rpc": Str(),
        "zmq_url_status": Str(),
        "relay_method": Str(),
        "admin_pin": Int(),
        "is_fullscreen": Bool(),
        "default_slippage": Float(),
        "buy_limit": Int()
    })
    _notes_schema = Map({"denominations": Seq(Str())})

    _folder_config = "machine_config"
    _folder_notes_config = "{}/{}".format(_folder_config, "notes_config")

    def __init__(self, config_name):
        # validate and parse config file
        with open("{}/{}.yaml".format(Config._folder_config, config_name)) as c:
            machine_config = strictyaml.load(c.read(), Config._schema).data

        # validate and parse note config file
        with open("{}/{}.yaml".format(Config._folder_notes_config, machine_config["currency"])) as c:
            notes_config = strictyaml.load(c.read(), Config._notes_schema).data

        self.NAME = machine_config["name"]
        self.BASE_CURRENCY = machine_config["currency"]
        self.DEBUG = bool(machine_config["debug"])
        self.CAMERA_METHOD = machine_config["camera_method"]
        self.CAMERA_DEVICE = machine_config["camera_device"]
        self.RELAY_METHOD = machine_config["relay_method"]
        self.MOCK_VALIDATOR = machine_config["mock_validator"]
        self.ZMQ_URL_MOCK_VALIDATOR = machine_config["zmq_url_mock_validator"]
        self.NOTE_VALIDATOR_NV11 = machine_config["validator_nv11"]
        self.VALIDATOR_PORT = machine_config["validator_port"]
        self.ZMQ_URL_PRICEFEED = machine_config["zmq_url_pricefeed"]
        self.NOTES_VALUES = notes_config["denominations"]
        self.ZMQ_URL_RPC = machine_config["zmq_url_rpc"]
        self.ZMQ_URL_STATUS = machine_config["zmq_url_status"]
        self.IS_FULLSCREEN = machine_config["is_fullscreen"]
        self.DEFAULT_SLIPPAGE = machine_config["default_slippage"]
        self.BUY_LIMIT = machine_config["buy_limit"]

        if not os.uname()[4].startswith("arm"):
            self.RELAY_METHOD = RelayMethod.NONE

        # setup drivers
        self.LED_DRIVER = Config._select_led_driver(self.RELAY_METHOD)
        self.QR_SCANNER = Config._select_qr_scanner(self.CAMERA_METHOD, self.CAMERA_DEVICE)
        self.QR_GENERATOR = QRGenerator()
        self.CASHOUT_DRIVER = Config._select_cashout_driver(self)
        self.NODE_RPC = NodeRPC(self.ZMQ_URL_RPC)

        self.CASHIN_THREAD = None
        self.PRICEFEED = None
        self.STATUS = None

    def start_all_threads(self, callback_cashin, callback_pricefeed, callback_status):
        self.CASHIN_THREAD = self._select_cashin_thread(
            self.MOCK_VALIDATOR,
            self.ZMQ_URL_MOCK_VALIDATOR,
            self.VALIDATOR_PORT,
            callback_cashin
        )
        self.PRICEFEED = ZMQSubscriber(callback_pricefeed, self.ZMQ_URL_PRICEFEED, ZMQSubscriber.TOPIC_PRICEFEED)
        self.STATUS = ZMQSubscriber(callback_status, self.ZMQ_URL_STATUS, ZMQSubscriber.TOPIC_STATUS)

    @staticmethod
    def _select_cashin_thread(mock_validator, mock_validator_url, validator_port, callback):
        if mock_validator is True:
            from .cashin_driver.mock_cashin_driver import MockCashinDriver
            return MockCashinDriver(callback, mock_validator_url)
        else:
            from .cashin_driver.essp_cashin_driver import EsspCashinDriver
            return EsspCashinDriver(callback, validator_port)

    @staticmethod
    def _select_led_driver(relay_method):
        if relay_method is RelayMethod.PIFACE:
            from .led_driver.piface_led_driver import LedDriverPiFace
            return LedDriverPiFace()
        elif relay_method is RelayMethod.GPIO:
            from .led_driver.gpio_led_driver import LedDriverGPIO
            return LedDriverGPIO()
        else:
            from .led_driver.no_led_driver import LedDriverNone
            return LedDriverNone()

    @staticmethod
    def _select_cashout_driver(config):
        if config.MOCK_VALIDATOR is True:
            from .cashout_driver.mock_cashout_driver import MockCashoutDriver
            return MockCashoutDriver()
        else:
            from .cashout_driver.essp_cashout_driver import EsspCashoutDriver
            return EsspCashoutDriver(config.VALIDATOR_PORT)

    @staticmethod
    def _select_qr_scanner(camera_method, camera_device):
        if CameraMethod[camera_method] is CameraMethod.ZBARCAM:
            from .qr_scanner.zbar_qr_scanner import QrScannerZbar
            return QrScannerZbar(camera_device)
        elif CameraMethod[camera_method] is CameraMethod.OPENCV:
            from .qr_scanner.opencv_qr_scanner import QrScannerOpenCV
            return QrScannerOpenCV()
        else:
            from .qr_scanner.none_qr_scanner import QrScannerNone
            return QrScannerNone()


def print_debug(*args, **kwargs):
    print("PLEASE USE Logger.debug/Logger.info/...")
    print(*args, **kwargs)


def parse_args() -> argparse.Namespace:
    """
    Parse CLI arguments.

    Raises an argparse.ArgumentError if the config is missing.

    :return: Config attributes in an argparse Namespace
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('config', help="configuration file name (located in machine_config/ folder)")
    return parser.parse_args()
