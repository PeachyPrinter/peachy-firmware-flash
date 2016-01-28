import sys


class FirmwareUpdater(object):
    def init(self, logger=None):
        pass

    def check_ready(self):
        pass

    def update(self, firmware_path):
        pass


class MacFirmwareUpdater(FirmwareUpdater):
    def init(self, logger=None):
        pass

    def check_ready(self):
        pass

    def update(self, firmware_path):
        pass


class LinuxFirmwareUpdater(FirmwareUpdater):
    def init(self, logger=None):
        pass

    def check_ready(self):
        pass

    def update(self, firmware_path):
        pass


class WindowsFirmwareUpdater(FirmwareUpdater):
    def init(self, logger=None):
        pass

    def check_ready(self):
        pass

    def update(self, firmware_version):
        pass


def get_firmware_updater(self, logger=None):
    if 'win' in sys.platform:
        return WindowsFirmwareUpdater(logger)
    elif 'linux' in sys.platform:
        return LinuxFirmwareUpdater(logger)
    elif 'darwin' in sys.platform:
        return MacFirmwareUpdater(logger)
    else:
        if logger:
            logger.error("Platform {} is unsupported for firmware updates".format(sys.platform))
        raise Exception("Unsupported Platform")
