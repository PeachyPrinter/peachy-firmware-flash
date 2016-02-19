from setuptools import setup
from setuptools.command.install import install as _Install
from VERSION import version

setup(
    name='PeachyPrinterFirmwareAPI',
    version=version,
    description='Tool for updating the firmware of peachyprinter',
    options={},
    url="http://www.peachyprinter.com",
    author="Peachy Printer",
    author_email="software+peachyprintertools@peachyprinter.com",
    install_requires=[],
    packages=['firmware', ],
    py_modules=['VERSION'],
    include_package_data=True
      )


class install(_Install):
    def run(self):
        super(install, self).run(self)
        print "BADA-BADA-KABONG"
