from picamera2 import Picamera2, Preview
from libcamera import ColorSpace
from PIL import Image, ImageOps
import time

# Layout in pixels (Selphy postcard at 300 dpi)
PAGE_W, PAGE_H = 1181, 1748
STRIP_W = 590
MARGIN = 40
GAP = 20

# Crop photo and resize
# 510, 340 
# 1181 / 2 = 590 - 80 = 510
# Giving 40px on each side
# Aspect Ratio of 3:2 
# 510 x 2/3 = 340px
PHOTO_W = STRIP_W - 2 * MARGIN                 # 510
PHOTO_H = PHOTO_W * 2 // 3                     # 340 (3:2)

ORIGIN_LEFT = MARGIN                           # 40
ORIGIN_RIGHT = (PAGE_W - STRIP_W) + MARGIN     # 631

def camera_init():
    picam2 = Picamera2()
    preview_config = picam2.create_preview_configuration({"size":(1280,720)})
    capture_config = picam2.create_still_configuration()
    return picam2, capture_config, preview_config
    

def taking_pics(picam2, capture_config, preview_config,):
    pics = []
    picam2.configure(preview_config)
    picam2.start(show_preview=True)
    time.sleep(1)

    # Uncomment if you want to see picture take
    # picam2.capture_file("test.jpg")
    for i in range(4):
        time.sleep(3)
        pics.append(picam2.switch_mode_and_capture_image(capture_config))
     
    picam2.stop()
    return pics

def image_processing(pics):
    # Blank page ~1181x1748px for a canon selphy postcard page
    page = Image.new("RGB", (PAGE_W, PAGE_H), "white")
    y = MARGIN
    for pic in pics:
       
        photo = ImageOps.fit(pic, (PHOTO_W,PHOTO_H))
        page.paste(pic, (ORIGIN_LEFT, y))
        page.paste(pic, (ORIGIN_RIGHT, y))
        y += PHOTO_H + GAP
    page.save("print.jpg", quality=95)

picam2, capture_config, preview_config = camera_init()
pics = taking_pics(picam2, capture_config, preview_config)
image_processing(pics)




