import sys
import os
import stat
from subprocess import Popen, PIPE


class FirmwareUpdater(object):
    def __init__(self, dependancy_path, bootloader_idvendor, bootloader_idproduct, peachy_idvendor, peachy_idproduct, logger=None):
        self._bootloader_idvendor = bootloader_idvendor
        self._bootloader_idproduct = bootloader_idproduct
        self._peachy_idvendor = peachy_idvendor
        self._peachy_idproduct = peachy_idproduct
        self._logger = logger

        self.dependancy_path = dependancy_path

    @property
    def bootloader_usb_address(self):
        return "{0:04x}:{1:04x}".format(self._bootloader_idvendor, self._bootloader_idproduct)

    @property
    def peachy_usb_address(self):
        return "{0:04x}:{1:04x}".format(self._peachy_idvendor, self._peachy_idproduct)

    @property
    def check_usb_command(self):
        raise NotImplementedError()

    def list_usb_devices(self):
        process = Popen(self.check_usb_command, stdout=PIPE, stderr=PIPE)
        (out, err) = process.communicate()
        exit_code = process.wait()
        if exit_code != 0:
            if self._logger:
                self._logger.error("Output: {}".format(out))
                self._logger.error("Error: {}".format(err))
                self._logger.error("Exit Code: {}".format(exit_code))
            raise Exception("Command failed")
        else:
            peachys = out.count(self.peachy_usb_address)
            bootloaders = out.count(self.bootloader_usb_address)
            return (bootloaders, peachys)

    def check_ready(self):
        bootloaders, peachy_printers = self.list_usb_devices()
        if (bootloaders == 1) and (peachy_printers == 0):
            return True
        elif (bootloaders == 0) and (peachy_printers <= 1):
            return False
        else:
            if self._logger:
                self._logger.error("{0} peachy printers and {1} bootloaders found".format(peachy_printers, bootloaders))
            raise Exception("{0} peachy printers and {1} bootloaders found".format(peachy_printers, bootloaders))

    def update(self, firmware_path):
        raise NotImplementedError()


class LinuxFirmwareUpdater(FirmwareUpdater):

    @property
    def check_usb_command(self):
        return ['lsusb']


    @property
    def dfu_bin(self):
        bin_file = os.path.join(self.dependancy_path, 'dfu-util')
        if os.path.isfile(bin_file):
            st = os.stat(bin_file)
            os.chmod(bin_file, st.st_mode | stat.S_IEXEC)
            return os.path.join(self.dependancy_path, 'dfu-util')
        else:
            if self._logger:
                self._logger.error("Binary at {} missing.".format(bin_file))
            raise Exception("Binary at {} missing.".format(bin_file))

    def update(self, firmware_path):
            process = Popen([
                self.dfu_bin,
                '-a', '0',
                '--dfuse-address', '0x08000000',
                '-D', firmware_path,
                '-d', self.bootloader_usb_address
            ], stdout=PIPE, stderr=PIPE)
            (out, err) = process.communicate()
            exit_code = process.wait()
            if exit_code != 0:
                if self._logger:
                    self._logger.error("Output: {}".format(out))
                    self._logger.error("Error: {}".format(err))
                    self._logger.error("Exit Code: {}".format(exit_code))
                return False
            else:
                return True

class MacFirmwareUpdater(LinuxFirmwareUpdater):

    @property
    def bootloader_usb_address(self):
        return "0x{0:04x}:0x{1:04x}".format(self._bootloader_idvendor, self._bootloader_idproduct)

    @property
    def peachy_usb_address(self):
        return "0x{0:04x}:0x{1:04x}".format(self._peachy_idvendor, self._peachy_idproduct)

    @property
    def check_usb_command(self):
        command = [os.path.join(self.dependancy_path, 'check_usb.sh')]
        print command
        return [os.path.join(self.dependancy_path, 'check_usb.sh')]


class WindowsFirmwareUpdater(FirmwareUpdater):

    @property
    def bootloader_usb_address(self):
        return '"USB\\VID_{0:04X}&PID_{1:04X}"'.format(self._bootloader_idvendor, self._bootloader_idproduct)

    @property
    def peachy_usb_address(self):
        return '"USB\\VID_{0:04X}&PID_{1:04X}"'.format(self._peachy_idvendor, self._peachy_idproduct)

    @property
    def check_usb_command(self):
        return '''wmic.exe path WIN32_PnPEntity where "DeviceID like 'USB\\\\VID_%'" get HardwareID'''

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
        process.wait()

        returned_lines = out.split('\n')
        for line in returned_lines:
            split_line = line.split(', ')
            if (len(split_line) == 2) and ("RETURN" in split_line[0]):
                driver_code = split_line[0].split(':')[1]
        driver_code_message = split_line[1]

        if driver_code:
            self._logger.error("Driver Output: {0}".format(out))
            self._logger.error("Driver Error Code: {0}, {1}".format(driver_code, driver_code_message))
        return driver_code

    def update(self, firmware_path):
        driver_return = self.switch_driver()
        if driver_return == 0:
            process = Popen([
                self.dfu_bin,
                '-a', '0',
                '--dfuse-address', '0x08000000',
                '-D', firmware_path,
                '-d', self.bootloader_usb_address
                ], stdout=PIPE, stderr=PIPE)
            (out, err) = process.communicate()
            exit_code = process.wait()
            if exit_code != 0:
                if self._logger:
                    self._logger.error("Output: {}".format(out))
                    self._logger.error("Error: {}".format(err))
                    self._logger.error("Exit Code: {}".format(exit_code))
                return False
            else:
                return True
        else:
            raise Exception('Failed to switch driver')


def get_firmware_updater(logger=None, bootloader_idvendor=0x0483, bootloader_idproduct=0xdf11, peachy_idvendor=0x16d0, peachy_idproduct=0x0af3):
    if logger:
        logger.info("Firmware Flash Is Frozen: {}".format(str(getattr(sys, 'frozen', False))))
    if 'darwin' in sys.platform:
        if getattr(sys, 'frozen', False):
            dependancies_path = sys._MEIPASS
        else:
            dependancies_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dependancies', 'mac')
        if logger:
            logger.info("Firmware Flash Dependancies Path: {}".format(dependancies_path))
        return MacFirmwareUpdater(dependancies_path, bootloader_idvendor, bootloader_idproduct, peachy_idvendor, peachy_idproduct, logger)
    elif 'win' in sys.platform:
        if getattr(sys, 'frozen', False):
            dependancies_path = sys._MEIPASS
        else:
            dependancies_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dependancies', 'windows')
        return WindowsFirmwareUpdater(dependancies_path, bootloader_idvendor, bootloader_idproduct, peachy_idvendor, peachy_idproduct, logger)
    elif 'linux' in sys.platform:
        if getattr(sys, 'frozen', False):
            dependancies_path = sys._MEIPASS
        else:
            dependancies_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dependancies', 'linux')
        return LinuxFirmwareUpdater(dependancies_path, bootloader_idvendor, bootloader_idproduct, peachy_idvendor, peachy_idproduct, logger)
    else:
        if logger:
            logger.error("Platform {} is unsupported for firmware updates".format(sys.platform))
        raise Exception("Unsupported Platform")
