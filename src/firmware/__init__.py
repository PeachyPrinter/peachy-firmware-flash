import os
import sys
import logging

from firmware import MacFirmwareUpdater, LinuxFirmwareUpdater, WindowsFirmwareUpdater


logger = logging.getLogger('peachy')

def get_firmware_updater(bootloader_idvendor=0x0483, bootloader_idproduct=0xdf11, peachy_idvendor=0x16d0, peachy_idproduct=0x0af3):
    print("Firmware Flash Is Frozen: {}".format(str(getattr(sys, 'frozen', False))))
    if 'darwin' in sys.platform:
        if getattr(sys, 'frozen', False):
            dependancies_path = sys._MEIPASS
        else:
            dependancies_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dependancies', 'mac')
        print("Firmware Flash Dependancies Path: {}".format(dependancies_path))
        return MacFirmwareUpdater(dependancies_path, bootloader_idvendor, bootloader_idproduct, peachy_idvendor, peachy_idproduct)
    elif 'win' in sys.platform:
        if getattr(sys, 'frozen', False):
            dependancies_path = sys._MEIPASS
        else:
            dependancies_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dependancies', 'windows')
        return WindowsFirmwareUpdater(dependancies_path, bootloader_idvendor, bootloader_idproduct, peachy_idvendor, peachy_idproduct)
    elif 'linux' in sys.platform:
        if getattr(sys, 'frozen', False):
            dependancies_path = sys._MEIPASS
        else:
            dependancies_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dependancies', 'linux')
        return LinuxFirmwareUpdater(dependancies_path, bootloader_idvendor, bootloader_idproduct, peachy_idvendor, peachy_idproduct)
    else:
        logger.error("Platform {} is unsupported for firmware updates".format(sys.platform))
        raise Exception("Unsupported Platform")