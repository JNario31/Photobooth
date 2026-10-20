from picamera2 import Picamera2, Preview
from libcamera import ColorSpace
from PIL import Image, ImageOps
import time
import numpy as np

# Framebuffer (values from /sys/class/graphics/fb0)
FB_H, STRIDE = 480, 3200

# Screen 800x480px
# 32 bits per pixel = 4 bytes per pixel
# 800px * 4 bytes = Stride of 3200
# Maps screen memory (480 rows of 3200 bytes)
# Rows follow one after the other so byte address of pixe (x,y)
# y * 3200 + x * 4
fb = np.memmap("/dev/fb0", dtype=np.uint8, mode="r+", shape=(FB_H, STRIDE))

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

COUNTDOWN_S = 10

def camera_init():
    picam2 = Picamera2()
    preview_config = picam2.create_preview_configuration({"size":(800,450), "format": "XRGB8888"})
    capture_config = picam2.create_still_configuration()
    return picam2, capture_config, preview_config
    
def write_frame(frame):
    # frame.shape = (400,800,4), take only first two [:2] h and w
    h,w = frame.shape[:2]

    # height of the screen is 480, but the frame is only 450
    # divide the remaining 30px evenly
    y0 = (FB_H - h) // 2

    # reshape the frame to match the frame buffer
    # Select rows 15 to 464 and bytes 0 to 3199
    fb[y0:y0 + h, :w * 4] = frame.reshape(h, w * 4)

def live_preview(picam2, seconds):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        write_frame(picam2.capture_array())

def taking_pics(picam2, capture_config, preview_config,):
    pics = []
    picam2.configure(preview_config)
    picam2.start(show_preview=True)

    # Uncomment if you want to see picture take
    # picam2.capture_file("test.jpg")
    for i in range(4):
        live_preview(picam2, COUNTDOWN_S)
        fb[:] = 255                         # Load frame buffer with white flash while photo is taken
        pics.append(picam2.switch_mode_and_capture_image(capture_config))
     
    picam2.stop()
    fb[:] = 0                               # Clear screen
    return pics

def image_processing(pics):
    # Blank page ~1181x1748px for a canon selphy postcard page
    page = Image.new("RGB", (PAGE_W, PAGE_H), "white")
    y = MARGIN
    for pic in pics:
       
        photo = ImageOps.fit(pic, (PHOTO_W,PHOTO_H))
        page.paste(photo, (ORIGIN_LEFT, y))
        page.paste(photo, (ORIGIN_RIGHT, y))
        y += PHOTO_H + GAP
    page.save("print.jpg", quality=95)

picam2, capture_config, preview_config = camera_init()
pics = taking_pics(picam2, capture_config, preview_config)
image_processing(pics)




