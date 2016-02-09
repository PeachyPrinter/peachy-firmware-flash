import sys
import os
from mock import patch, MagicMock
import unittest
from usb.core import Device

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

@patch('firmware.firmware.usbcore')
class TestFirmwareUpdater(unittest.TestCase):
    BOOTLOADER_IDVENDOR = 0x0483
    BOOTLOADER_IDPRODUCT = 0xdf11
    PEACHY_IDVENDOR = 0x16d0
    PEACHY_IDPRODUCT = 0x0af3

    def test_check_ready_should_return_true_if_1_bootloader(self, mock_usb):
        mock_bootloader_device = MagicMock()
        mock_bootloader_device.idVendor = self.BOOTLOADER_IDVENDOR
        mock_bootloader_device.idProduct = self.BOOTLOADER_IDPRODUCT
        mock_usb.find.return_value = iter([mock_bootloader_device])

        fw_up = FirmwareUpdater('somepath', self.BOOTLOADER_IDVENDOR, self.BOOTLOADER_IDPRODUCT, self.PEACHY_IDVENDOR, self.PEACHY_IDPRODUCT)
        result = fw_up.check_ready()

        self.assertTrue(result)
        mock_usb.find.assert_called_with(find_all=True)

    def test_check_ready_should_return_False_if_no_results(self, mock_usb):
        mock_usb.find.return_value = iter([])

        fw_up = FirmwareUpdater('somepath', self.BOOTLOADER_IDVENDOR, self.BOOTLOADER_IDPRODUCT, self.PEACHY_IDVENDOR, self.PEACHY_IDPRODUCT)
        result = fw_up.check_ready()

        self.assertFalse(result)
        mock_usb.find.assert_called_with(find_all=True)

    def test_check_ready_should_return_False_if_only_peachy_results(self, mock_usb):
        mock_peachy = MagicMock()
        mock_peachy.idVendor = self.PEACHY_IDVENDOR
        mock_peachy.idProduct = self.PEACHY_IDPRODUCT
        mock_usb.find.return_value = iter([mock_peachy])

        fw_up = FirmwareUpdater('somepath', self.BOOTLOADER_IDVENDOR, self.BOOTLOADER_IDPRODUCT, self.PEACHY_IDVENDOR, self.PEACHY_IDPRODUCT)
        result = fw_up.check_ready()

        self.assertFalse(result)
        mock_usb.find.assert_called_with(find_all=True)

    def test_check_ready_should_raise_exception_if_peachy_and_bootloader(self, mock_usb):
        mock_peachy = MagicMock()
        mock_peachy.idVendor = self.PEACHY_IDVENDOR
        mock_peachy.idProduct = self.PEACHY_IDPRODUCT
        mock_bootloader = MagicMock()
        mock_bootloader.idVendor = self.BOOTLOADER_IDVENDOR
        mock_bootloader.idProduct = self.BOOTLOADER_IDPRODUCT
        mock_usb.find.return_value = iter([mock_peachy, mock_bootloader])

        fw_up = FirmwareUpdater('somepath', self.BOOTLOADER_IDVENDOR, self.BOOTLOADER_IDPRODUCT, self.PEACHY_IDVENDOR, self.PEACHY_IDPRODUCT)
        with self.assertRaises(Exception):
            fw_up.check_ready()

        mock_usb.find.assert_called_with(find_all=True)

    def test_check_ready_should_raise_exception_if_multipule_peachys(self, mock_usb):
        mock_peachy1 = MagicMock()
        mock_peachy1.idVendor = self.PEACHY_IDVENDOR
        mock_peachy1.idProduct = self.PEACHY_IDPRODUCT
        mock_peachy2 = MagicMock()
        mock_peachy2.idVendor = self.PEACHY_IDVENDOR
        mock_peachy2.idProduct = self.PEACHY_IDPRODUCT
        mock_usb.find.return_value = iter([mock_peachy1, mock_peachy2])

        fw_up = FirmwareUpdater('somepath', self.BOOTLOADER_IDVENDOR, self.BOOTLOADER_IDPRODUCT, self.PEACHY_IDVENDOR, self.PEACHY_IDPRODUCT)
        with self.assertRaises(Exception):
            fw_up.check_ready()

        mock_usb.find.assert_called_with(find_all=True)

    def test_check_ready_should_raise_exception_if_multipule_bootloaders(self, mock_usb):
        mock_bootloader1 = MagicMock()
        mock_bootloader1.idVendor = self.BOOTLOADER_IDVENDOR
        mock_bootloader1.idProduct = self.BOOTLOADER_IDPRODUCT
        mock_bootloader2 = MagicMock()
        mock_bootloader2.idVendor = self.BOOTLOADER_IDVENDOR
        mock_bootloader2.idProduct = self.BOOTLOADER_IDPRODUCT

        mock_usb.find.return_value = iter([mock_bootloader1, mock_bootloader2])

        fw_up = FirmwareUpdater('somepath', self.BOOTLOADER_IDVENDOR, self.BOOTLOADER_IDPRODUCT, self.PEACHY_IDVENDOR, self.PEACHY_IDPRODUCT)
        with self.assertRaises(Exception):
            fw_up.check_ready()

        mock_usb.find.assert_called_with(find_all=True)


if __name__ == '__main__':
    unittest.main()

