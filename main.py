import argparse
import time

import cv2
import numpy as np
from PIL import Image


def read_gif(path):
    cap = cv2.VideoCapture(path)
    gif = []
    fps = cap.get(cv2.CAP_PROP_FPS)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gif.append(frame)

    return gif, 1.0/fps


class Handler:
    def __init__(self, gif, duration, window):
        self.gif = gif
        self.duration = duration
        self.time = 0.0
        self.window = window
        cv2.setMouseCallback(window, self.callback)
        self.frame = 0
        self.img = self.gif[self.frame]
        cv2.imshow(window, self.img)
        self.hold = False
        self.init_point = None
        self.end_point = None

    def callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.init_point = (x, y)
            self.hold = True
        elif event == cv2.EVENT_LBUTTONUP:
            self.hold = False

        elif event == cv2.EVENT_RBUTTONDOWN:
            self.init_point = None
            self.end_point = None

        if self.hold:
            self.end_point = (x, y)


        self.show_rect()

    def show_rect(self):
        if self.init_point is None:
            cv2.imshow(self.window, self.img)
        else:
            img = cv2.rectangle(
                self.img.copy(), self.init_point, self.end_point, (255, 0, 0))
            cv2.imshow(self.window, img)


    def play_gif(self):
        if (time.time() - self.time) >= self.duration:
            self.frame = (self.frame+1) % len(self.gif)
            self.img = self.gif[self.frame]
            self.show_rect()
            self.time = time.time()

    def get_rect(self):
        if self.init_point:
            return self.init_point, self.end_point
        else:
            return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', required=True, type=str)
    parser.add_argument('--output', '-o', required=False, type=str, default='output.gif')
    args = parser.parse_args()

    gif, duration = read_gif(args.input)
    cv2.namedWindow('window')
    handler = Handler(gif, duration, 'window')
    play_gif = False

    print('space key: play gif')
    print('mouse left button: select cropped area')
    print('s key: save gif')
    print('esc key: exit')
    while(1):
        key = cv2.waitKey(20) & 0xFF
        if key == 27:
            break
        if key == ord('s'):
            rect = handler.get_rect()
            if rect is None:
                print('Crop area is not selected.')
            else:
                x1, y1 = rect[0]
                x2, y2 = rect[1]
                x1, x2 = sorted([x1, x2])
                y1, y2 = sorted([y1, y2])
                gif_crop = list(np.array(gif)[:, int(y1):int(y2), int(x1):int(x2), :])
                gif_crop = [Image.fromarray(cv2.cvtColor(g, cv2.COLOR_BGR2RGB)) for g in gif_crop]
                gif_crop[0].save(args.output, save_all=True, append_images=gif_crop[1:], loop=0, duration=duration*1000)
                print('saved.')
        if key == ord(' '):
            play_gif = not play_gif

        if play_gif:
            handler.play_gif()

    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
