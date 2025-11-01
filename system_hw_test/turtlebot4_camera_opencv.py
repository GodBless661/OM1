import sys
import time

import cv2
import numpy as np

sys.path.insert(0, "../src")
from zenoh_msgs import open_zenoh_session


# Parameter
HEADER_SIZE = 76
WIDTH = 250
HEIGHT = 250
CHANNELS = 3
EXPECTED_IMAGE_BYTES = WIDTH * HEIGHT * CHANNELS  # 187500
EXPECTED_TOTAL = HEADER_SIZE + EXPECTED_IMAGE_BYTES


def listener(sample):
    bytesI = sample.payload.to_bytes()
    print(f"Received {len(sample.payload)}")
    X = np.frombuffer(bytesI, dtype=np.uint8)
    # for some reason the first 76 numbers are trash?
    # some sort of metadata header?
    Xc = X[HEADER_SIZE:HEADER_SIZE + EXPECTED_IMAGE_BYTES]
    rgb = np.reshape(Xc, (HEIGHT, WIDTH, CHANNELS))
    cv2.imwrite("front_image.jpg", rgb)


if __name__ == "__main__":

    with open_zenoh_session() as session:
        camera = session.declare_subscriber("pi/oakd/rgb/preview/image_raw", listener)
        print("Zenoh is open")
        while True:
            print("Waiting for camera messages")
            time.sleep(1)
