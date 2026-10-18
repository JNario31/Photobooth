from picamera2 import Picamera2, Preview
from libcamera import ColorSpace
from PIL import Image, ImageOps
import time


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
    picam2.switch_mode(capture_config)

    # Uncomment if you want to see picture take
    # picam2.capture_file("test.jpg")
    for i in range(4):
        time.sleep(3)
        pics.append(picam2.capture_image())
     
    picam2.stop()
    return pics

def image_processing(pics):
    ORIGIN_LEFT = 40;
    ORIGIN_RIGHT = 631;
    # Crop photo and resize
    # 510, 340 
    # 1181 / 2 = 590 - 80 = 510
    # Giving 40px on each side
    # Aspect Ratio of 3:2 
    # 510 x 2/3 = 340px
    for pic in pics:
        ImageOps.fit(pic, (510,340))

    # Blank page ~1181x1748px for a canon selphy postcard page
    page = Image.new("RGB", (1181, 1748), "white")

    i = 0
    for pic in pics:
        page.paste(pic, (ORIGIN_LEFT, 40))
        page.paste(pic, (ORIGIN_RIGHT, 40))
        i =+ 360
    page.save("print.jpg", quality=95)

picam2, capture_config, preview_config = camera_init()
pics = taking_pics(picam2, capture_config, preview_config)
image_processing(pics)




