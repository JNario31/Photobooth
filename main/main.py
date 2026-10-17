from picamera2 import Picamera2, Preview
from libcamera import ColorSpace
from PIL import Image, ImageOps
import time

picam2 = Picamera2()
preview_config = picam2.create_preview_configuration({"size":(1280,720)})
capture_config = picam2.create_still_configuration()
picam2.configure(preview_config)
picam2.start(show_preview=True)

time.sleep(1)
picam2.switch_mode(capture_config)

# Uncomment if you want to see picture take
# picam2.capture_file("test.jpg")

img = picam2.capture_image()
picam2.stop()

# Crop photo and resize
# 510, 340 
# 1181 / 2 = 590 - 80 = 510
# Giving 40px on each side
# Aspect Ratio of 3:2 
# 510 x 2/3 = 340px
photo = ImageOps.fit(img, (510,340))

# Blank page ~1181x1748px for a canon selphy postcard page
page = Image.new("RGB", (1181, 1748), "white")
page.paste(photo, (40, 40))
page.save("print.jpg", quality=95)
