import sys
import os
import usb
from subprocess import Popen, PIPE


class FirmwareUpdater(object):
    def __init__(self, dependancy_path, bootloader_idvendor, bootloader_idproduct, peachy_idvendor, peachy_idproduct, logger=None):
        self._bootloader_idvendor = bootloader_idvendor
        self._bootloader_idproduct = bootloader_idproduct
        self._peachy_idvendor = peachy_idvendor
        self._peachy_idproduct = peachy_idproduct
        self._logger = logger

        self.dependancy_path = dependancy_path
        self.usb_address = "{0:x}:{1:x}".format(bootloader_idvendor, bootloader_idproduct)

    def _list_usb_devices(self):
        self._bootloaders = []
        self._peachyPrinters = []
        for dev in usb.core.find(find_all=True):
            if (dev.idVendor == self._bootloader_idvendor) and (dev.idProduct == self._bootloader_idproduct):
                self._bootloaders.append(dev)
            elif (dev.idVendor == self._peachy_idvendor) and (dev.idProduct == self._peachy_idproduct):
                self._peachyPrinters.append(dev)

    def check_ready(self):
        self._list_usb_devices()
        num_bootloaders = len(self._bootloaders)
        num_peachyPrinters = len(self._peachyPrinters)
        if (num_peachyPrinters == 1) and (num_peachyPrinters == 0):
            return True
        elif (num_peachyPrinters == 0) and (num_peachyPrinters <= 1):
            return False
        else:
            if self._logger:
                self._logger.error("{0} peachy printers and {1} bootloaders found".format(num_peachyPrinters, num_bootloaders))
            raise Exception("{0} peachy printers and {1} bootloaders found".format(num_peachyPrinters, num_bootloaders))

    def update(self, firmware_path, complete_call_back=None):
        raise NotImplementedError()


class MacFirmwareUpdater(FirmwareUpdater):

    @property
    def dfu_bin(self):
        pass

    def update(self, firmware_path, complete_call_back=None):
        raise NotImplementedError()


class LinuxFirmwareUpdater(FirmwareUpdater):

    @property
    def dfu_bin(self):
        return os.path.join(self.dependancy_path, 'dfu-util')

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
                if self._logger:
                    self._logger.error("Output: {}".format(out))
                    self._logger.error("Error: {}".format(err))
                    self._logger.error("Exit Code: {}".format(exit_code))
                raise Exception('Failed to update device')


class WindowsFirmwareUpdater(FirmwareUpdater):

    @property
    def driver_bin(self):
        return os.path.join(self.dependancy_path, 'wdi-simple.exe')

    @property
    def dfu_bin(self):
        return os.path.join(self.dependancy_path, 'dfu-util-static.exe')

    def switch_driver(self):
        process = Popen(
            [self.driver_bin, '-b'],
            stdout=PIPE, stderr=PIPE)
        (out, err) = process.communicate()
        exit_code = process.wait()

        returned_lines = out.split('\n')
        for line in returned_lines:
            split_line = line.split(',')
            if (len(split_line) == 2) and ("RETURN" in split_line[0]):
                driver_code = split_line[0].split(':')[1]
        driver_code_message = split_line[1]

        if driver_code:
            self._logger.error("Driver Output: {0}".format(out))
            self._logger.error("Driver Error Code: {0}, {1}".format(driver_code, driver_code_message))
        return driver_code

    def update(self, firmware_path, complete_call_back=None):
        if self._test_mode:
            return True
        else:
            driver_return = self.switch_driver()
            if driver_return == 0:
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
                    if self._logger:
                        self._logger.error("Output: {}".format(out))
                        self._logger.error("Error: {}".format(err))
                        self._logger.error("Exit Code: {}".format(exit_code))
                    raise Exception('Failed to update device')
            else:
                raise Exception('Failed to switch driver')


def get_firmware_updater(logger=None, bootloader_idvendor=0x0483, bootloader_idproduct=0xdf11, peachy_idvendor=0x16d0, peachy_idproduct=0x0af3):
    path = os.path.dirname(os.path.abspath(__file__))
    dependancies_path = os.path.join(path, 'dependancies', 'windows')
    if 'win' in sys.platform:
        dependancies_path = os.path.join(path, 'dependancies', 'windows')
        return WindowsFirmwareUpdater(dependancies_path, bootloader_idvendor, bootloader_idproduct, peachy_idvendor, peachy_idproduct, logger)
    elif 'linux' in sys.platform:
        dependancies_path = os.path.join(path, 'dependancies', 'linux')
        return LinuxFirmwareUpdater(dependancies_path, bootloader_idvendor, bootloader_idproduct, peachy_idvendor, peachy_idproduct, logger)
    elif 'darwin' in sys.platform:
        dependancies_path = os.path.join(path, 'dependancies', 'mac')
        return MacFirmwareUpdater(dependancies_path, bootloader_idvendor, bootloader_idproduct, peachy_idvendor, peachy_idproduct, logger)
    else:
        if logger:
            logger.error("Platform {} is unsupported for firmware updates".format(sys.platform))
        raise Exception("Unsupported Platform")
