from picamera2 import Picamera2, Preview
from libcamera import ColorSpace
import time

picam2 = Picamera2()
preview_config = picam2.create_preview_configuration({"size":(1280,720)})
capture_config = picam2.create_still_configuration()
picam2.configure(preview_config)
picam2.start(show_preview=True)

time.sleep(1)
picam2.switch_mode(capture_config)
picam2.capture_file("test.jpg")
picam2.stop()