# SPDX-FileCopyrightText: 2023-present anjomro <py@anjomro.de>
#
# SPDX-License-Identifier: EUPL-1.2

import cv2
import easyocr
from PIL import Image


def id_scanner(cam: int = 0):
    reader = easyocr.Reader(['de'])
    # Loop endlessly until q or ESC is pressed
    while True:
        # Wait for keypress
        k = input("Press enter to take image, press q and enter to quit")
        # if space bar is pressed take image and use with easyocr
        if k == '':
            # Read frame, open cam with HD
            cam = cv2.VideoCapture(2)

            cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

            ret, frame = cam.read()
            cam.release()
            print("Image taken, calculating...")
            # Display image
            # cv2.imshow('image', frame)
            # load into easyocr
            result = reader.readtext(frame, paragraph=True)
            # print result
            print(result)
            print("")
            # Loop through results, display line by line
            for i in range(len(result)):
                print(result[i][1])
            # Load image in PIL
            img = Image.fromarray(frame)
            # Display image
            img.show()
        # if q or ESC is pressed exit
        elif k == "q":
            break
    # Release the camera
