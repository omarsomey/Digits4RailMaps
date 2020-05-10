#!/bin/bash
rmmod uvcvideo
modprobe uvcvideo nodrop=1 timeout=6000 quirks=0x80