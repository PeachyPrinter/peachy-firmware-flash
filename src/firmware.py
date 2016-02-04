import sys
import os
import usb
from subprocess import Popen, PIPE

BOOTLOADER_IDVENDOR=0x0483
BOOTLOADER_IDPRODUCT=0xdf11
PEACHY_IDVENDOR=0x16d0
PEACHY_IDPRODUCT=0x0af3

class FirmwareUpdater(object):
    def __init__(self, logger=None, peachy_printer_address='0483:df11'):
        self._bootloaders = []
        self._peachyPrinters = []

    def list_usb_devices(self):
        # Clear these each time so we can use this function a whole bunch
        self._bootloaders = []
        self._peachyPrinters = []
        for dev in usb.core.find(find_all=True):
            if (dev.idVendor == BOOTLOADER_IDVENDOR) and (dev.idProduct == BOOTLOADER_IDPRODUCT):
                self._bootloaders.append(dev)
            elif (dev.idVendor == PEACHY_IDVENDOR) and (dev.idProduct == PEACHY_IDPRODUCT):
                self._peachyPrinters.append(dev)

    def check_ready(self):
        self.list_usb_devices()
        # Asserting we have a single bootloader and no peachys plugged in. This should catch most error cases
        # including a peachy board failing to switch to bootloader and there being a bootloader device already plugged in.
        if (len(self._bootloaders) == 1) and (len(self._peachyPrinters) == 0):
            return True
        else:
            return False

    def update(self, firmware_path, complete_call_back=None):
        raise NotImplementedError()


class MacFirmwareUpdater(FirmwareUpdater):
    def __init__(self, logger=None, peachy_printer_address='0483:df11', test_mode=True):
        self._test_mode = test_mode
        if self._test_mode:
            return True
        else:
            pass

    def update(self, firmware_path, complete_call_back=None):
        pass


class LinuxFirmwareUpdater(FirmwareUpdater):
    def __init__(self, dependancy_path, logger=None, peachy_printer_address='0483:df11', test_mode=True):
        self._test_mode = test_mode
        if self._test_mode:
            pass
        else:
            self.logger = logger
            self.dependancy_path = dependancy_path
            self.usb_address = peachy_printer_address
            self.dfu_bin = os.path.join(self.dependancy_path, 'dfu-util')

    def update(self, firmware_path, complete_call_back=None):
        if self._test_mode:
            return True
        else:
            process = Popen([
                self.dfu_bin,
                '-a', '0',
                '--dfuse-address', '0x08000000',
                '-D', firmware_path,
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
            self.driver_exe = os.path.join(self.dependancy_path, 'wdi-simple.exe')

    def switch_driver(self):
        # This is a one way force, it will only change the driver if it needs to be changed.
        process = Popen(
            [self.driver_exe, '-b'],
            stdout=PIPE, stderr=PIPE)
        (out, err) = process.communicate()
        exit_code = process.wait()

        # I'm recording these parsed states here for now, in case we need them for debug later
        board_state = []
        driver = []
        driver_version = []

        returned_lines = out.split('\n')  # Split by each message line
        for line in returned_lines:
            split_line = line.split(',')
            if (len(split_line) == 3) and ("DRIVER" in split_line[1]):  # DRIVER info line
                board_state.append(split_line[0])
                driver.append(split_line[1].split(':')[1])
                driver_version.append(split_line[2].split(':')[1])
            elif (len(split_line) == 1) and ("RETURN" in split_line[0]):  # RETURN code for the flashing
                driver_code = split_line[0].split(':')[1]
        if driver_code:
            self.logger.error("Driver Output: {0}".format(out))
            self.logger.error("Driver Error Code: {0}".format(driver_code))
        return driver_code

    def update(self, firmware_path, complete_call_back=None):
        if self._test_mode:
            return True
        else:
            driver_return=self.switch_driver()
            if driver_return == 0:
                process = Popen([
                    self.dfu_exe,
                    '-a', '0',
                    '--dfuse-address', '0x08000000',
                    '-D', firmware_path,
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
            else:
                raise Exception('Failed to switch driver')


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
