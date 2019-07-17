from abc import ABC, abstractmethod
import pexpect

class QrScanner(ABC):

    def __init__(self):
        super().__init__()

    def scan(self):
        ''' scans the interface for a QR-Code
        returns None if no code was found, or a string representing the whole QR '''
        cmd = self._cmd()

        execute = pexpect.spawn(cmd, [], 300)

        while True:
            try:
                execute.expect('\n')
                # Get last line from expect
                line = execute.before
                if self._is_qr_found(line):
                    qr = self._get_qr_from_line(line)
                    execute.close(True)
                    return qr.decode('ascii') if qr is not None else None
            except pexpect.EOF:
                break
            except pexpect.TIMEOUT:
                break

        return None

    @abstractmethod
    def _cmd(self):
        ''' the command to execute to start a process that returns a QRcode on the std output'''
        pass

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
