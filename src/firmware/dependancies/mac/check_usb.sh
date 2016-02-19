#!/bin/bash

system_profiler SPUSBDataType | awk '/Product ID:/{p=$3}/Vendor ID:/{v=$3; printf("%s:%s\n",v,p)};'
