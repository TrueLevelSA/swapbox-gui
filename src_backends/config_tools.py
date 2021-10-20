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
import os

from src_backends.cashin_driver.cashin_driver_base import CashinDriver
from src_backends.custom_threads.zmq_subscriber import ZMQSubscriber
from src_backends.node_rpc.node_rpc import NodeRPC
from src_backends.qr_generator.qr_generator import QRGenerator


class CameraMethod(Enum):
    ZBARCAM = auto()
    OPENCV = auto()
    KIVY = auto()

    @staticmethod
    def elems() -> [str]:
        return [elem.name for elem in CameraMethod]


class RelayMethod(Enum):
    PIFACE = auto()
    GPIO = auto()
    NONE = auto()

    @staticmethod
    def elems() -> [str]:
        return [elem.name for elem in RelayMethod]


class Mock:
    def __init__(self, cfg):
        self.enabled: bool = cfg["enabled"]
        self.zmq_url: str = cfg["zmq_url"]


class Validator:
    def __init__(self, cfg):
        self.mock = Mock(cfg["mock"])
        self.port: str = cfg["port"]
        self.nv11: bool = cfg["nv11"]


class Camera:
    def __init__(self, cfg):
        self.method: CameraMethod = CameraMethod[cfg["method"]]
        self.device = cfg["device"]


class Zmq:
    def __init__(self, cfg):
        self.pricefeed = cfg["pricefeed"]
        self.rpc = cfg["rpc"]
        self.status = cfg["status"]


class Config(object):
    _schema = Map({
        "name": Str(),
        "debug": Bool(),
        "currency": Str(),

        "validator": Map({
            "mock": Map({
                "enabled": Bool(),
                "zmq_url": Str(),
            }),
            "port": Str(),
            "nv11": Bool(),
        }),
        "camera": Map({
            "method": strictyaml.Enum(CameraMethod.elems()),
            "device": Str()
        }),
        "zmq": Map({
            "pricefeed": Str(),
            "rpc": Str(),
            "status": Str(),
        }),
        "relay_method": strictyaml.Enum(RelayMethod.elems()),
        "admin_pin": Int(),
        "is_fullscreen": Bool(),
        "default_slippage": Float(),
        "buy_limit": Int()
    })
    _notes_schema = Map({"denominations": Seq(Int())})

    _folder_config = "machine_config"
    _folder_notes_config = "{}/{}".format(_folder_config, "notes_config")

    def __init__(self, config_name):
        # validate and parse config file
        with open("{}/{}.yaml".format(Config._folder_config, config_name)) as c:
            machine_config = strictyaml.load(c.read(), Config._schema).data

        # build self with parsed config
        self.operator_name = machine_config["name"]
        self.debug: bool = machine_config["debug"]
        self.base_currency = machine_config["currency"]
        self.validator = Validator(machine_config["validator"])
        self.camera = Camera(machine_config["camera"])
        self.zmq = Zmq(machine_config["zmq"])
        self.relay_method: RelayMethod = RelayMethod[machine_config["relay_method"]]
        self.is_fullscreen: bool = machine_config["is_fullscreen"]
        self.default_slippage: float = machine_config["default_slippage"]
        self.buy_limit: int = machine_config["buy_limit"]

        # validate and parse note config file
        with open("{}/{}.yaml".format(Config._folder_notes_config, machine_config["currency"])) as c:
            notes_config = strictyaml.load(c.read(), Config._notes_schema).data
        self.notes_values = notes_config["denominations"]

        if not os.uname()[4].startswith("arm"):
            self.RELAY_METHOD = RelayMethod.NONE

        # TODO: maybe drivers shouldn't live in the Config
        # setup drivers
        self.LED_DRIVER = Config._select_led_driver(self.RELAY_METHOD)
        self.QR_SCANNER = Config._select_qr_scanner(self.camera)
        self.QR_GENERATOR = QRGenerator()
        self.CASHOUT_DRIVER = Config._select_cashout_driver(self)
        self.NODE_RPC = NodeRPC(self.zmq.rpc)

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
        if config.validator.mock.enabled:
            from .cashout_driver.mock_cashout_driver import MockCashoutDriver
            return MockCashoutDriver()
        else:
            from .cashout_driver.essp_cashout_driver import EsspCashoutDriver
            return EsspCashoutDriver(config.VALIDATOR_PORT)

    @staticmethod
    def _select_qr_scanner(camera: Camera):
        if camera.method is CameraMethod.ZBARCAM:
            from .qr_scanner.zbar_qr_scanner import QrScannerZbar
            return QrScannerZbar(camera.device)
        elif camera.method is CameraMethod.OPENCV:
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
