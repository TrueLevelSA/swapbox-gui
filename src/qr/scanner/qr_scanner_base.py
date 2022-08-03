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

import threading
from abc import ABC, abstractmethod

import pexpect


class QrScanner(ABC):

    def __init__(self, cmd_to_execute):
        ''' cmd: the command to execute to start a process that returns a QRcode on the std output'''
        super().__init__()
        self._scanning = threading.Event()
        self._cmd_to_execute = cmd_to_execute
        self._execute = None

    def scan(self):
        ''' scans the interface for a QR-Code
        returns None if no code was found, or a string representing the whole QR '''

        self._start_locally()

        self._scanning.clear()

        self._execute = pexpect.spawn(self._cmd_to_execute, [], 300)

        while not self._scanning.is_set():
            try:
                self._execute.expect('\n')
                # Get last line from expect
                line = self._execute.before
                if self._is_qr_found(line):
                    qr = self._get_qr_from_line(line)
                    self._close_executor()
                    return qr.decode('ascii').strip() if qr is not None else None
            except pexpect.EOF:
                self._close_executor()
                break
            except pexpect.TIMEOUT:
                self._close_executor()
                break

        self._close_executor()
        return None

    def _close_executor(self):
        self._stop_locally()
        if self._execute is not None:
            self._execute.close(True)
            self._execute = None

    def stop_scan(self):
        self._scanning.set()
        self._close_executor()

    @abstractmethod
    def _is_qr_found(self, line):
        ''' parse the line to check if a QR code was found
        the line is the output of a process running the _cmd command'''
        pass

    @abstractmethod
    def _get_qr_from_line(self, line):
        ''' parse the line to return the content of the QR code,
        the line has already passed the check in _is_qr_found
        the line is the output of a process running the _cmd command'''
        pass

    @abstractmethod
    def _start_locally(self):
        ''' qr_scanning is going to be started '''
        pass

    @abstractmethod
    def _stop_locally(self):
        ''' qr_scanning is going to be stopped, close stuff gracefully '''
        pass
