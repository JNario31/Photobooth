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


