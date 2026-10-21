from picamera2 import Picamera2, Preview
from libcamera import ColorSpace
from PIL import Image, ImageOps, ImageDraw, ImageFont
import time
import numpy as np
import math

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

# PREVIEW
PREV_H, PREV_W = 450, 800
CROP_W = PREV_H * 3 // 2
SIDE = (PREV_W - CROP_W) // 2
COUNTDOWN_S = 3


def blend(frame, overlay):
    arr, box = overlay
    if box is None:
        return frame
    x0, y0, x1, y1 = box
    f = frame[y0:y1, x0:x1, :3].astype(np.uint16)
    o = arr[y0:y1, x0:x1, :3].astype(np.uint16)
    a = arr[y0:y1, x0:x1, 3:4].astype(np.uint16)
    frame[y0:y1, x0:x1, :3] = ((o * a + f * (255 - a)) // 255).astype(np.uint8)
    return frame

def build_overlays():
    big = ImageFont.load_default(size=200)
    small = ImageFont.load_default(size=36)
    white, black = (255, 255, 255, 255), (0, 0, 0, 255)

    countdown = {
        n: make_overlay(lambda d, n=n: d.text((PREV_W // 2, PREV_H // 2), str(n), font=big, fill=white, anchor="mm", stroke_width=6, stroke_fill=black))
        for n in range(1, COUNTDOWN_S + 1)
    }
    counter = {
        i: make_overlay(lambda d, i=i: d.text((PREV_W - SIDE - 10,10),f"{i} / 4", font=small, fill=white, anchor="ra", stroke_width=3, stroke_fill=black))
        for i in range(1, 5)
    }
    return countdown, counter

def dim_sides(frame):
    frame[:, :SIDE, :3] //= 2
    frame[:, PREV_W - SIDE:, :3] //= 2

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

def live_preview(picam2, seconds, countdown=None, counter=None):
    end = time.monotonic() + seconds
    while True:
        remaining = end - time.monotonic()
        if remaining <= 0:
            break
        frame = picam2.capture_array()
        dim_sides(frame)
        if counter is not None:
            blend(frame, counter)
        if countdown is not None:
            digit = math.ceil(remaining)       # 3, 2, 1
            if digit in countdown:
                blend(frame, countdown[digit])
        write_frame(frame)

def taking_pics(picam2, capture_config, preview_config, countdown, counter):
    pics = []
    picam2.configure(preview_config)
    picam2.start()

    # Uncomment if you want to see picture take
    # picam2.capture_file("test.jpg")
    for i in range(4):
        live_preview(picam2, COUNTDOWN_S, countdown, counter[i + 1])
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

def make_overlay(draw_fn, size=(800,450)):
    img = Image.new("RGBA", size,(0,0,0,0))
    draw_fn(ImageDraw.Draw(img))
    arr = np.array(img)[..., [2,1,0,3]] # Pillows RGBA to BGRA to match camera frames
    return arr, img.getbbox()

countdown, counter = build_overlays()
picam2, capture_config, preview_config = camera_init()
pics = taking_pics(picam2, capture_config, preview_config, countdown, counter)
image_processing(pics)




