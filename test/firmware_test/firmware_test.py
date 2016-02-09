import unittest
import sys
import os
from mock import patch
import unittest

# sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import firmware
from firmware import MacFirmwareUpdater, LinuxFirmwareUpdater, WindowsFirmwareUpdater

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



if __name__ == '__main__':
    unittest.main()
