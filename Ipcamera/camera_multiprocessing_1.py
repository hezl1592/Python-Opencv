# -*- coding: utf-8 -*-
# Time    : 2019/3/31 21:12
# Author  : zlich
# Filename: camera_multiprocessing_1.py
import multiprocessing
import cv2
import os


def CV_process(image):
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray_img, (7, 7), 1)

    gradX = cv2.Sobel(blurred, ddepth=cv2.CV_32F, dx=1, dy=0)
    gradY = cv2.Sobel(blurred, ddepth=cv2.CV_32F, dx=0, dy=1)
    # substract 相减计算
    gradient = cv2.subtract(gradX, gradY)
    # 取绝对值运算
    gradient = cv2.convertScaleAbs(gradient)

    blurred = cv2.GaussianBlur(gradient, (7, 7), 0)
    img = cv2.medianBlur(blurred, 3)

    return img


def cam_loop(source, queue, stopped):
    print("cam loop start")
    cap = cv2.VideoCapture(source)

    while True:
        # print('the read queue:', queue.qsize())
        ret, img = cap.read()
        if ret:
            queue.put(img)
        if stopped.value:
            break
    cap.release()
    print('cam_loop stopped')


def show_loop(queue, stopped):
    print('show loop start')
    while True:
        # print('the show queue:', queue.qsize())
        from_queue = queue.get()
        cv2.imshow('pepe', from_queue)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print('pause')
            stopped.value = 1
            break
        cv2.waitKey(10)
    cv2.destroyAllWindows()
    print('show_loop shut down')


if __name__ == '__main__':
    source = 0      # camera source

    stopped = multiprocessing.Value("l", 0)     # shared Variable for multi-process
    read_Queue = multiprocessing.Queue(10)      # Reading shared Queue for multi-process

    # create the cam_process
    cam_process = multiprocessing.Process(target=cam_loop, args=(source, read_Queue, stopped,))
    cam_process.start()

    show_Queue = multiprocessing.Queue(10)

    show_process = multiprocessing.Process(
        target=show_loop, args=(show_Queue, stopped,))
    show_process.start()

    frames_counts = 0
    while True:
        print(frames_counts)
        image_np = read_Queue.get()  # 读取视频帧
        # print(current_frame.shape)
        frames_counts += 1
        if frames_counts % 5 == 0:
            image_np = CV_process(image_np)

        show_Queue.put(image_np)
        if stopped.value:
            print(stopped.value)
            print('stop while.')
            break
    print('stopped')
    cv2.destroyAllWindows()
    cam_process.terminate()
    print("all done")
    show_process.terminate()
    os._exit(0)
