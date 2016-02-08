import unittest
import sys
import os
from mock import patch
import unittest

# sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import firmware
from firmware import MacFirmwareUpdater, LinuxFirmwareUpdater, WindowsFirmwareUpdater

class TestFirmware(unittest.TestCase):

    @patch('firmware.sys')
    def test_correct_class_for_platform_is_provided(self, mock_sys):
        mock_sys.platform = 'darwin'
        result = firmware.get_firmware_updater()
        self.assertEquals(MacFirmwareUpdater, type(result))


if __name__ == '__main__':
    unittest.main()
