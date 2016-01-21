import os
from subprocess import Popen, PIPE
import logging
logger = logging.getLogger('peachy')


class FirmwareUpdater(object):
    def init(self):
        pass

    def check_ready(self):
        pass

    def update(self, firmware_path):
        pass


class WindowsFirmwareUpdater(FirmwareUpdater):
    def __init__(self, dependancy_path, peachy_printer_address='0483:df11'):
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
            logger.error("Output: {}".format(out))
            logger.error("Error: {}".format(err))
            logger.error("Exit Code: {}".format(exit_code))
            raise Exception('Failed to update device')


def get_firmware_updater(self):
    return WindowsFirmwareUpdater()


logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='INFO')
path = os.path.join('dependancies', 'windows')
wfu = WindowsFirmwareUpdater(path)

firmware = '..\\peachyprinter-firmware-0.1.180.bin'
if wfu.check_ready():
    wfu.update(firmware)

