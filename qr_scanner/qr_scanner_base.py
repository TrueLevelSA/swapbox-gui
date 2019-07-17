from abc import ABC, abstractmethod
import pexpect

class QrScanner(ABC):

    def __init__(self):
        super().__init__()

    def scan(self):
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
        pass

    @abstractmethod
    def _is_qr_found(self, line):
        pass

    @abstractmethod
    def _get_qr_from_line(self, line):
        pass
