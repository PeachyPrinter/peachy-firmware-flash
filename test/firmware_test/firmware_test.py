import sys
import os
from mock import patch, MagicMock
import unittest
from usb.core import Device
from subprocess import PIPE

# sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import firmware
from firmware.firmware import FirmwareUpdater, MacFirmwareUpdater, LinuxFirmwareUpdater, WindowsFirmwareUpdater


@patch('firmware.sys')
class TestFirmwareInit(unittest.TestCase):

    def test_correct_class_for_mac_platform_is_provided(self, mock_sys):
        mock_sys.platform = 'darwin'
        result = firmware.get_firmware_updater()
        self.assertEquals(MacFirmwareUpdater, type(result))

    def test_correct_class_for_win32_platform_is_provided(self, mock_sys):
        mock_sys.platform = 'win32'
        result = firmware.get_firmware_updater()
        self.assertEquals(WindowsFirmwareUpdater, type(result))

    def test_correct_class_for_win64_platform_is_provided(self, mock_sys):
        mock_sys.platform = 'winamd64'
        result = firmware.get_firmware_updater()
        self.assertEquals(WindowsFirmwareUpdater, type(result))

    def test_correct_class_for_linux_platform_is_provided(self, mock_sys):
        mock_sys.platform = 'linux'
        result = firmware.get_firmware_updater()
        self.assertEquals(LinuxFirmwareUpdater, type(result))

    def test_exception_raised_if_not_supported(self, mock_sys):
        mock_sys.platform = 'sun'
        with self.assertRaises(Exception):
            firmware.get_firmware_updater()


@patch('firmware.firmware.Popen')
@patch('firmware.os.path.isfile')
@patch('firmware.os.stat')
@patch('firmware.os.chmod')
class TestLinuxFirmwareUpdater(unittest.TestCase):
    BOOTLOADER_IDVENDOR = 0x0483
    BOOTLOADER_IDPRODUCT = 0xdf11
    PEACHY_IDVENDOR = 0x16d0
    PEACHY_IDPRODUCT = 0x0af3

    def setUp(self):
        self.bin_path = os.path.join('some','binary', 'path')
        self.firmware_path = os.path.join('some', 'firmware', 'path.bin')

    def test_update_should_return_true_if_update_successfull(self, mock_chmod, mock_stat, mock_isfile, mock_Popen):
        mock_isfile.return_value = True
        mock_Popen.return_value.communicate.return_value = ('err', 'out')
        mock_Popen.return_value.wait.return_value = 0
        usb_addess = '{}:{}'.format('0483', 'df11')
        expected_command = [os.path.join(self.bin_path, 'dfu-util'), '-a', '0', '--dfuse-address', '0x08000000', '-D', self.firmware_path, '-d', usb_addess]

        l_fw_up = LinuxFirmwareUpdater(self.bin_path, self.BOOTLOADER_IDVENDOR, self.BOOTLOADER_IDPRODUCT, self.PEACHY_IDVENDOR, self.PEACHY_IDPRODUCT)
        result = l_fw_up.update(self.firmware_path)

        self.assertTrue(result)
        mock_Popen.assert_called_with(expected_command, stdout=PIPE, stderr=PIPE)
        mock_Popen.return_value.wait.assert_called_with()

    def test_update_should_return_false_if_update_not_successfull(self, mock_chmod, mock_stat, mock_isfile, mock_Popen):
        mock_isfile.return_value = True
        mock_Popen.return_value.communicate.return_value = ('err', 'out')
        mock_Popen.return_value.wait.return_value = 34
        usb_addess = '{}:{}'.format('0483', 'df11')
        expected_command = [os.path.join(self.bin_path, 'dfu-util'), '-a', '0', '--dfuse-address', '0x08000000', '-D', self.firmware_path, '-d', usb_addess]

        l_fw_up = LinuxFirmwareUpdater(self.bin_path, self.BOOTLOADER_IDVENDOR, self.BOOTLOADER_IDPRODUCT, self.PEACHY_IDVENDOR, self.PEACHY_IDPRODUCT)
        result = l_fw_up.update(self.firmware_path)

        self.assertFalse(result)
        mock_Popen.assert_called_with(expected_command, stdout=PIPE, stderr=PIPE)
        mock_Popen.return_value.wait.assert_called_with()

    def test_check_ready_should_return_true_if_1_bootloader(self, mock_chmod, mock_stat, mock_isfile, mock_Popen):

        mock_Popen.return_value.communicate.return_value = ('{:04x}:{:04x}'.format(self.BOOTLOADER_IDVENDOR, self.BOOTLOADER_IDPRODUCT), '')
        mock_Popen.return_value.wait.return_value = 0

        fw_up = LinuxFirmwareUpdater('somepath', self.BOOTLOADER_IDVENDOR, self.BOOTLOADER_IDPRODUCT, self.PEACHY_IDVENDOR, self.PEACHY_IDPRODUCT)
        result = fw_up.check_ready()

        self.assertTrue(result)
        mock_Popen.assert_called_with(['lsusb'], stdout=PIPE, stderr=PIPE)

    def test_check_ready_should_return_False_if_no_results(self, mock_chmod, mock_stat, mock_isfile, mock_Popen):
        mock_Popen.return_value.communicate.return_value = ('', '')
        mock_Popen.return_value.wait.return_value = 0

        fw_up = LinuxFirmwareUpdater('somepath', self.BOOTLOADER_IDVENDOR, self.BOOTLOADER_IDPRODUCT, self.PEACHY_IDVENDOR, self.PEACHY_IDPRODUCT)
        result = fw_up.check_ready()

        self.assertFalse(result)
        mock_Popen.assert_called_with(['lsusb'], stdout=PIPE, stderr=PIPE)

    def test_check_ready_should_return_False_if_only_peachy_results(self, mock_chmod, mock_stat, mock_isfile, mock_Popen):
        mock_Popen.return_value.communicate.return_value = ('{:04x}:{:04x}'.format(self.PEACHY_IDVENDOR, self.PEACHY_IDPRODUCT), '')
        mock_Popen.return_value.wait.return_value = 0

        fw_up = LinuxFirmwareUpdater('somepath', self.BOOTLOADER_IDVENDOR, self.BOOTLOADER_IDPRODUCT, self.PEACHY_IDVENDOR, self.PEACHY_IDPRODUCT)
        result = fw_up.check_ready()

        self.assertFalse(result)
        mock_Popen.assert_called_with(['lsusb'], stdout=PIPE, stderr=PIPE)

    def test_check_ready_should_raise_exception_if_peachy_and_bootloader(self, mock_chmod, mock_stat, mock_isfile, mock_Popen):
        mock_Popen.return_value.communicate.return_value = ('{:04x}:{:04x}\n{:04x}:{:04x}'.format(self.PEACHY_IDVENDOR, self.PEACHY_IDPRODUCT, self.BOOTLOADER_IDVENDOR, self.BOOTLOADER_IDPRODUCT), '')
        mock_Popen.return_value.wait.return_value = 0

        fw_up = LinuxFirmwareUpdater('somepath', self.BOOTLOADER_IDVENDOR, self.BOOTLOADER_IDPRODUCT, self.PEACHY_IDVENDOR, self.PEACHY_IDPRODUCT)

        with self.assertRaises(Exception):
            fw_up.check_ready()

        mock_Popen.assert_called_with(['lsusb'], stdout=PIPE, stderr=PIPE)

    def test_check_ready_should_raise_exception_if_multipule_peachys(self, mock_chmod, mock_stat, mock_isfile, mock_Popen):
        mock_Popen.return_value.communicate.return_value = ('{0:04x}:{1:04x}\n{0:04x}:{1:04x}'.format(self.PEACHY_IDVENDOR, self.PEACHY_IDPRODUCT), '')
        mock_Popen.return_value.wait.return_value = 0

        fw_up = LinuxFirmwareUpdater('somepath', self.BOOTLOADER_IDVENDOR, self.BOOTLOADER_IDPRODUCT, self.PEACHY_IDVENDOR, self.PEACHY_IDPRODUCT)
        with self.assertRaises(Exception):
            fw_up.check_ready()

        mock_Popen.assert_called_with(['lsusb'], stdout=PIPE, stderr=PIPE)

    def test_check_ready_should_raise_exception_if_multipule_bootloaders(self, mock_chmod, mock_stat, mock_isfile, mock_Popen):
        mock_Popen.return_value.communicate.return_value = ('{0:04x}:{1:04x}\n{0:04x}:{1:04x}'.format(self.BOOTLOADER_IDVENDOR, self.BOOTLOADER_IDPRODUCT), '')
        mock_Popen.return_value.wait.return_value = 0

        fw_up = LinuxFirmwareUpdater('somepath', self.BOOTLOADER_IDVENDOR, self.BOOTLOADER_IDPRODUCT, self.PEACHY_IDVENDOR, self.PEACHY_IDPRODUCT)
        with self.assertRaises(Exception):
            fw_up.check_ready()

        mock_Popen.assert_called_with(['lsusb'], stdout=PIPE, stderr=PIPE)


@patch('firmware.firmware.Popen')
@patch('firmware.os.path.isfile')
@patch('firmware.os.stat')
@patch('firmware.os.chmod')
class TestWindowsFirmwareUpdater(unittest.TestCase):
    BOOTLOADER_IDVENDOR = 0x0483
    BOOTLOADER_IDPRODUCT = 0xdf11
    PEACHY_IDVENDOR = 0x16d0
    PEACHY_IDPRODUCT = 0x0af3

    def setUp(self):
        self.bin_path = os.path.join('some','binary', 'path')
        self.firmware_path = os.path.join('some', 'firmware', 'path.bin')

    # def test_update_should_return_true_if_update_successfull(self, mock_chmod, mock_stat, mock_isfile, mock_Popen):
    #     mock_isfile.return_value = True
    #     mock_Popen.return_value.communicate.return_value = ('err', 'out')
    #     mock_Popen.return_value.wait.return_value = 0
    #     usb_addess = '{}:{}'.format('0483', 'df11')
    #     expected_command = [os.path.join(self.bin_path, 'dfu-util'), '-a', '0', '--dfuse-address', '0x08000000', '-D', self.firmware_path, '-d', usb_addess]

    #     l_fw_up = LinuxFirmwareUpdater(self.bin_path, self.BOOTLOADER_IDVENDOR, self.BOOTLOADER_IDPRODUCT, self.PEACHY_IDVENDOR, self.PEACHY_IDPRODUCT)
    #     result = l_fw_up.update(self.firmware_path)

    #     self.assertTrue(result)
    #     mock_Popen.assert_called_with(expected_command, stdout=PIPE, stderr=PIPE)
    #     mock_Popen.return_value.wait.assert_called_with()

    # def test_update_should_return_false_if_update_not_successfull(self, mock_chmod, mock_stat, mock_isfile, mock_Popen):
    #     mock_isfile.return_value = True
    #     mock_Popen.return_value.communicate.return_value = ('err', 'out')
    #     mock_Popen.return_value.wait.return_value = 34
    #     usb_addess = '{}:{}'.format('0483', 'df11')
    #     expected_command = [os.path.join(self.bin_path, 'dfu-util'), '-a', '0', '--dfuse-address', '0x08000000', '-D', self.firmware_path, '-d', usb_addess]

    #     l_fw_up = LinuxFirmwareUpdater(self.bin_path, self.BOOTLOADER_IDVENDOR, self.BOOTLOADER_IDPRODUCT, self.PEACHY_IDVENDOR, self.PEACHY_IDPRODUCT)
    #     result = l_fw_up.update(self.firmware_path)

    #     self.assertFalse(result)
    #     mock_Popen.assert_called_with(expected_command, stdout=PIPE, stderr=PIPE)
    #     mock_Popen.return_value.wait.assert_called_with()

    def test_check_ready_should_return_true_if_1_bootloader(self, mock_chmod, mock_stat, mock_isfile, mock_Popen):

        mock_Popen.return_value.communicate.return_value = ('"USB\VID_{:04X}&PID_{:04X}"'.format(self.BOOTLOADER_IDVENDOR, self.BOOTLOADER_IDPRODUCT), '')
        mock_Popen.return_value.wait.return_value = 0

        fw_up = WindowsFirmwareUpdater('somepath', self.BOOTLOADER_IDVENDOR, self.BOOTLOADER_IDPRODUCT, self.PEACHY_IDVENDOR, self.PEACHY_IDPRODUCT)
        result = fw_up.check_ready()

        self.assertTrue(result)
        mock_Popen.assert_called_with('''wmic.exe path WIN32_PnPEntity where "DeviceID like 'USB\\\\VID_%'" get HardwareID''', stdout=PIPE, stderr=PIPE)

    def test_check_ready_should_return_False_if_no_results(self, mock_chmod, mock_stat, mock_isfile, mock_Popen):
        mock_Popen.return_value.communicate.return_value = ('', '')
        mock_Popen.return_value.wait.return_value = 0

        fw_up = WindowsFirmwareUpdater('somepath', self.BOOTLOADER_IDVENDOR, self.BOOTLOADER_IDPRODUCT, self.PEACHY_IDVENDOR, self.PEACHY_IDPRODUCT)
        result = fw_up.check_ready()

        self.assertFalse(result)
        mock_Popen.assert_called_with('''wmic.exe path WIN32_PnPEntity where "DeviceID like 'USB\\\\VID_%'" get HardwareID''', stdout=PIPE, stderr=PIPE)

    def test_check_ready_should_return_False_if_only_peachy_results(self, mock_chmod, mock_stat, mock_isfile, mock_Popen):
        mock_Popen.return_value.communicate.return_value = ('"USB\VID_{:04X}&PID_{:04X}"'.format(self.PEACHY_IDVENDOR, self.PEACHY_IDPRODUCT), '')
        mock_Popen.return_value.wait.return_value = 0

        fw_up = WindowsFirmwareUpdater('somepath', self.BOOTLOADER_IDVENDOR, self.BOOTLOADER_IDPRODUCT, self.PEACHY_IDVENDOR, self.PEACHY_IDPRODUCT)
        result = fw_up.check_ready()

        self.assertFalse(result)
        mock_Popen.assert_called_with('''wmic.exe path WIN32_PnPEntity where "DeviceID like 'USB\\\\VID_%'" get HardwareID''', stdout=PIPE, stderr=PIPE)

    def test_check_ready_should_raise_exception_if_peachy_and_bootloader(self, mock_chmod, mock_stat, mock_isfile, mock_Popen):
        mock_Popen.return_value.communicate.return_value = ('"USB\VID_{:04X}&PID_{:04X}"\n"USB\VID_{:04X}&PID_{:04X}"'.format(self.PEACHY_IDVENDOR, self.PEACHY_IDPRODUCT, self.BOOTLOADER_IDVENDOR, self.BOOTLOADER_IDPRODUCT), '')
        mock_Popen.return_value.wait.return_value = 0

        fw_up = WindowsFirmwareUpdater('somepath', self.BOOTLOADER_IDVENDOR, self.BOOTLOADER_IDPRODUCT, self.PEACHY_IDVENDOR, self.PEACHY_IDPRODUCT)

        with self.assertRaises(Exception):
            fw_up.check_ready()

        mock_Popen.assert_called_with('''wmic.exe path WIN32_PnPEntity where "DeviceID like 'USB\\\\VID_%'" get HardwareID''', stdout=PIPE, stderr=PIPE)

    def test_check_ready_should_raise_exception_if_multipule_peachys(self, mock_chmod, mock_stat, mock_isfile, mock_Popen):
        mock_Popen.return_value.communicate.return_value = ('"USB\VID_{0:04X}&PID_{1:04X}"\n"USB\VID_{0:04X}&PID_{1:04X}"'.format(self.PEACHY_IDVENDOR, self.PEACHY_IDPRODUCT), '')
        mock_Popen.return_value.wait.return_value = 0

        fw_up = WindowsFirmwareUpdater('somepath', self.BOOTLOADER_IDVENDOR, self.BOOTLOADER_IDPRODUCT, self.PEACHY_IDVENDOR, self.PEACHY_IDPRODUCT)
        with self.assertRaises(Exception):
            fw_up.check_ready()

        mock_Popen.assert_called_with('''wmic.exe path WIN32_PnPEntity where "DeviceID like 'USB\\\\VID_%'" get HardwareID''', stdout=PIPE, stderr=PIPE)

    def test_check_ready_should_raise_exception_if_multipule_bootloaders(self, mock_chmod, mock_stat, mock_isfile, mock_Popen):
        mock_Popen.return_value.communicate.return_value = ('"USB\VID_{0:04X}&PID_{1:04X}"\n"USB\VID_{0:04X}&PID_{1:04X}"'.format(self.BOOTLOADER_IDVENDOR, self.BOOTLOADER_IDPRODUCT), '')
        mock_Popen.return_value.wait.return_value = 0

        fw_up = WindowsFirmwareUpdater('somepath', self.BOOTLOADER_IDVENDOR, self.BOOTLOADER_IDPRODUCT, self.PEACHY_IDVENDOR, self.PEACHY_IDPRODUCT)
        with self.assertRaises(Exception):
            fw_up.check_ready()

        mock_Popen.assert_called_with('''wmic.exe path WIN32_PnPEntity where "DeviceID like 'USB\\\\VID_%'" get HardwareID''', stdout=PIPE, stderr=PIPE)

if __name__ == '__main__':
    unittest.main()
