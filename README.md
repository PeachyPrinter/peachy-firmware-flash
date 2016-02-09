Peachy Printer Firmware Flash
==================

Status
-------------------------

Very Active Development (Unworking)

Support
--------------------------

All support for Peachy Printer Tools located at http://forum.peachyprinter.com/


Supported Environments
---------------------------
Windows 32bit, 64bit
Linux 64bit
Mac 64bit (future)


Usage
--------------------------

```import firmware
updater  = firmware.get_firmware_updater(logger=None, bootloader_idvendor=0x0483, bootloader_idproduct=0xdf11, peachy_idvendor=0x16d0, peachy_idproduct=0x0af3)
updater.check_ready()      #<---True if one Bootloader is ready, Flase if 1 Bootload is not ready, Raises for any exceptions
updater.update(path_to_firmware)       #<---True if Success, Flase if Failed, Rasies for unexpected behaviour
```


Known issues
--------------------------
Alpha Software, everything should be assumed broken


How toi help hit list
--------------------------
We need a mac version of dfu-utils with libusb linked statically


Contributing 
--------------------------

Yes please. 

Peachy Printer and its software are community driven, Please send us a pull request.

In order to be considered please ensure that:
+ Test Driven Design (TDD) write your tests first then write the code to make them work.
+ Respect the Single Responsibility Principal
+ Follow Onion Archetecture Principals
+ PEP8 formatting [Excpeting line length(E501) we are not programming on terminals anymore]

Please be aware that by contributing you agree to assignment of your copyrite to Peachy Printer INC. We do this for logistics and managment we will respect you freedoms and keep this source open.

Need help contributing? Please check out the forums: http://forum.peachyprinter.com/


Licence
---------------------------

Please see the LICENSE file

Note this software is a shell wrapper / user interface for included binaries that may haver thier own licenses

dfu-util is licensed under GPL version 2
http://dfu-util.sourceforge.net/
