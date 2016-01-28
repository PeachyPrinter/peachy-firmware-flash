import sys
import os
from subprocess import Popen, PIPE


class FirmwareUpdater(object):
    def init(self, logger=None, peachy_printer_address='0483:df11'):
        raise NotImplementedError()

    def check_ready(self):
        raise NotImplementedError()

    def update(self, firmware_path):
        raise NotImplementedError()


class MacFirmwareUpdater(FirmwareUpdater):
    def init(self, logger=None, peachy_printer_address='0483:df11'):
        pass

    def check_ready(self):
        pass

    def update(self, firmware_path):
        pass


class LinuxFirmwareUpdater(FirmwareUpdater):
    def init(self, logger=None, peachy_printer_address='0483:df11'):
        pass

    def check_ready(self):
        pass

    def update(self, firmware_path):
        pass


class WindowsFirmwareUpdater(FirmwareUpdater):
    def __init__(self, logger, dependancy_path, peachy_printer_address='0483:df11'):
        self.logger = logger
        self.dependancy_path = dependancy_path
        self.usb_address = peachy_printer_address
        self.dfu_exe = os.path.join(self.dependancy_path, 'dfu-util-static.exe')

    def check_ready(self):
        process = Popen([self.dfu_exe, '-l'], stdout=PIPE, stderr=PIPE)
        (out, err) = process.communicate()
        process.wait()
        return self.usb_address in err

    def update(self, firmware_path):
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


def get_firmware_updater(self, logger=None, peachy_printer_address='0483:df11'):
    dependancies_path = os.path.join('dependancies', 'windows')  #This wont work one installed via sdist
    if 'win' in sys.platform:
        return WindowsFirmwareUpdater(logger, dependancies_path)
    elif 'linux' in sys.platform:
        return LinuxFirmwareUpdater(logger, dependancies_path)
    elif 'darwin' in sys.platform:
        return MacFirmwareUpdater(logger, dependancies_path)
    else:
        if logger:
            logger.error("Platform {} is unsupported for firmware updates".format(sys.platform))
        raise Exception("Unsupported Platform")
