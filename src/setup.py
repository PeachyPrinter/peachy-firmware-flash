from setuptools import setup, find_packages
from setuptools.command.install import install as _Install
from firmware.VERSION import version

setup(
    name='PeachyPrinterFirmwareAPI',
    version=version,
    description='Tool for updating the firmware of peachyprinter',
    options={},
    url="http://www.peachyprinter.com",
    author="Peachy Printer",
    author_email="software+peachyprintertools@peachyprinter.com",
    package_data={'': ['*', 'firmware/dependancies/windows/*'],
                  # '': ['*', 'firmware/dependancies/mac/*'],
                  '': ['*', 'firmware/dependancies/linux/*'],
                  },
    install_requires=['pyusb==1.0.0b2'],
    packages=find_packages(),
    py_modules=['firmware'],
    include_package_data=True
      )


class install(_Install):
    def run(self):
        super(install, self).run(self)
        print "BADA-BADA-KABONG"
