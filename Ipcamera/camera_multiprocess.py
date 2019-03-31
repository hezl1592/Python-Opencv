# -*- coding: utf-8 -*-
# Time    : 2019/3/31 20:12
# Author  : zlich
# Filename: camera_multiprocess.py
import multiprocessing
import cv2


def cam_loop(queue, stopped):
    cap = cv2.VideoCapture(0)

    while True:
        print(queue.qsize())
        ret, img = cap.read()
        if ret:
            queue.put(img)
        print('stop value: ', stopped.value)
        if stopped.value:
            break
    cap.release()
    print('cam_loop stopped')


if __name__ == '__main__':
    stopped = multiprocessing.Value("l", 0)
    read_Queue = multiprocessing.Queue(2)

    cam_process = multiprocessing.Process(target=cam_loop, args=(read_Queue, stopped,))

    cam_process.start()

    while True:
        frame = read_Queue.get()
        cv2.imshow('pepe', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print('pause')
            break
        cv2.waitKey(20)
    cam_process.terminate()
    print("all done")
