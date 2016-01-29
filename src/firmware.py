import sys
import os
from subprocess import Popen, PIPE


class FirmwareUpdater(object):
    def __init__(self, logger=None, peachy_printer_address='0483:df11'):
        raise NotImplementedError()

    def check_ready(self):
        raise NotImplementedError()

    def update(self, firmware_path, complete_call_back=None):
        raise NotImplementedError()


class MacFirmwareUpdater(FirmwareUpdater):
    def __init__(self, logger=None, peachy_printer_address='0483:df11', test_mode=True):
        self._test_mode = test_mode
        if self._test_mode:
            return True
        else:
            pass

    def check_ready(self):
        pass

    def update(self, firmware_path, complete_call_back=None):
        pass


class LinuxFirmwareUpdater(FirmwareUpdater):
    def __init__(self, logger=None, peachy_printer_address='0483:df11', test_mode=True):
        self._test_mode = test_mode
        if self._test_mode:
            pass
        else:
            pass

    def check_ready(self):
        if self._test_mode:
            return True
        else:
            pass

    def update(self, firmware_path, complete_call_back=None):
        if self._test_mode:
            return True
        else:
            pass


class WindowsFirmwareUpdater(FirmwareUpdater):
    def __init__(self, logger, dependancy_path, peachy_printer_address='0483:df11', test_mode=True):
        self._test_mode = test_mode
        if self._test_mode:
            pass
        else:
            self.logger = logger
            self.dependancy_path = dependancy_path
            self.usb_address = peachy_printer_address
            self.dfu_exe = os.path.join(self.dependancy_path, 'dfu-util-static.exe')

    def check_ready(self):
        if self._test_mode:
            return True
        else:
            process = Popen([self.dfu_exe, '-l'], stdout=PIPE, stderr=PIPE)
            (out, err) = process.communicate()
            process.wait()
            return self.usb_address in err

    def update(self, firmware_path, complete_call_back=None):
        if self._test_mode:
            return True
        else:
            process = Popen([
                self.dfu_exe,
                '-a', '0',
                '--dfuse-address', '0x08000000',
                '-D', firmware_path,
                '-v',
                '-d', self.usb_address
                ], stdout=PIPE, stderr=PIPE)
            (out, err) = process.communicate()
            exit_code = process.wait()
            if exit_code != 0:
                if self.logger:
                    self.logger.error("Output: {}".format(out))
                    self.logger.error("Error: {}".format(err))
                    self.logger.error("Exit Code: {}".format(exit_code))
                raise Exception('Failed to update device')


def get_firmware_updater(logger=None, peachy_printer_address='0483:df11'):
    path = os.path.dirname(os.path.abspath(__file__))
    dependancies_path = os.path.join(path, 'dependancies', 'windows')
    if 'win' in sys.platform:
        dependancies_path = os.path.join(path, 'dependancies', 'windows')
        return WindowsFirmwareUpdater(logger, dependancies_path)
    elif 'linux' in sys.platform:
        dependancies_path = os.path.join(path, 'dependancies', 'linux')
        return LinuxFirmwareUpdater(logger, dependancies_path)
    elif 'darwin' in sys.platform:
        dependancies_path = os.path.join(path, 'dependancies', 'mac')
        return MacFirmwareUpdater(logger, dependancies_path)
    else:
        if logger:
            logger.error("Platform {} is unsupported for firmware updates".format(sys.platform))
        raise Exception("Unsupported Platform")
