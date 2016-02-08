import os
import sys
from firmware import MacFirmwareUpdater, LinuxFirmwareUpdater, WindowsFirmwareUpdater


def get_firmware_updater(logger=None, bootloader_idvendor=0x0483, bootloader_idproduct=0xdf11, peachy_idvendor=0x16d0, peachy_idproduct=0x0af3):
    path = os.path.dirname(os.path.abspath(__file__))
    if 'darwin' in sys.platform:
        dependancies_path = os.path.join(path, 'dependancies', 'mac')
        return MacFirmwareUpdater(dependancies_path, bootloader_idvendor, bootloader_idproduct, peachy_idvendor, peachy_idproduct, logger)
    elif 'win' in sys.platform:
        dependancies_path = os.path.join(path, 'dependancies', 'windows')
        return WindowsFirmwareUpdater(dependancies_path, bootloader_idvendor, bootloader_idproduct, peachy_idvendor, peachy_idproduct, logger)
    elif 'linux' in sys.platform:
        dependancies_path = os.path.join(path, 'dependancies', 'linux')
        return LinuxFirmwareUpdater(dependancies_path, bootloader_idvendor, bootloader_idproduct, peachy_idvendor, peachy_idproduct, logger)
    else:
        if logger:
            logger.error("Platform {} is unsupported for firmware updates".format(sys.platform))
        raise Exception("Unsupported Platform")
