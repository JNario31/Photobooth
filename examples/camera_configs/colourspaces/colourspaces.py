from picamera2 import Picamera2, Preview
from libcamera import ColorSpace
import time

def helper(colour_space, picam2):
    return picam2.create_preview_configuration(colour_space=colour_space)

picam2 = Picamera2()
colorspaceslist = [ColorSpace.Sycc(), ColorSpace.Smpte170m(), ColorSpace.Rec709()]

picam2.start_preview(Preview.DRM)

for i,colourspace in enumerate(colorspaceslist, start=1):
    picam2.configure(helper(colourspace, picam2))
    picam2.start()
    time.sleep(2)
    picam2.capture_file(f"colourspace{i}.jpg")
    picam2.stop()

picam2.stop_preview()
picam2.stop()

# When testing these out i did not understand what colour spaces are, all images from the test look identical
# Colour spaces are essentially a unit to define how the colours of a pixel is defined by numbers,
# for example:
# Colour      sYCC (Y, Cb, Cr)  SMPTE 170M (Y, Cb, Cr)
# Black       0, 128, 128       16, 128, 128
# White       255, 128, 128     235, 128, 128
# Red         76, 85, 255       82, 90, 240
# sYCC (Full range) brightness (Y) and colour channels (Cb, Cr) uses a full range from 0-255 centered around 128
# SMPTE 170M (Limited range) brightness range of 16-23 and colour channel range of 16-240, because the margin was used
# for signal overshoot as this is used in broadcast TV