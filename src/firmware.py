class FirmwareChecker(object):
    def init(self):
        pass

    def get_avaliable_versions(self, hardware_version):
        pass


class FirmwareUpdater(object):
    def init(self):
        pass

    def check_ready(self):
        pass

    def update(self, firmware_path):
        pass


class WindowsFirmwareUpdater(FirmwareUpdater):
    def init(self):
        pass

    def check_ready(self):
        pass

    def update(self, firmware_path):
        pass


def get_firmware_updater(self):
    return WindowsFirmwareUpdater()
