import sys
import os
import stat
from subprocess import Popen, PIPE
import logging

logger = logging.getLogger('peachy')


class FirmwareUpdater(object):
    def __init__(self, dependancy_path, bootloader_idvendor, bootloader_idproduct, peachy_idvendor, peachy_idproduct):
        self._bootloader_idvendor = bootloader_idvendor
        self._bootloader_idproduct = bootloader_idproduct
        self._peachy_idvendor = peachy_idvendor
        self._peachy_idproduct = peachy_idproduct

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
            logger.error("Output: {}".format(out))
            logger.error("Error: {}".format(err))
            logger.error("Exit Code: {}".format(exit_code))
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
            logger.error("{0} peachy printers and {1} bootloaders found".format(peachy_printers, bootloaders))
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
                logger.error("Output: {}".format(out))
                logger.error("Error: {}".format(err))
                logger.error("Exit Code: {}".format(exit_code))
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
        logger.info("Check usb command: {}".format(command))
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
    def dfu_bin(self):
        return os.path.join(self.dependancy_path, 'DfuSeCommand.exe')

    def update(self, firmware_path):
        process = Popen([
            self.dfu_bin,
            '-c', '-u', '--fn', firmware_path], stdout=PIPE, stderr=PIPE)
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



