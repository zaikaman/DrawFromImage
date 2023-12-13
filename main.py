# -*- coding: utf-8 -*-
# Tác giả: zaikaman
# Giấy phép: GNU GPLv3
# Thời gian: 13/12/2023

import turtle as te
from bs4 import BeautifulSoup
import argparse
import sys
import numpy as np
import cv2
import os
from win32.win32api import GetSystemMetrics
from PIL import ImageGrab
import pygame
from pygame import mixer

WriteStep = 15  # Số lần lấy mẫu cho hàm Bézier
Speed = 1000
Width = 600  # Chiều rộng màn hình
Height = 600  # Chiều cao màn hình
Xh = 0  # Lưu trữ tay cầm của hàm Bézier trước đó
Yh = 0
scale = (1, 1)
first = True
K = 32


def Bezier(p1, p2, t):  # Hàm Bézier bậc 1
    return p1 * (1 - t) + p2 * t


def Bezier_2(x1, y1, x2, y2, x3, y3):  # Hàm Bézier bậc 2
    te.goto(x1, y1)
    te.pendown()
    for t in range(0, WriteStep + 1):
        x = Bezier(Bezier(x1, x2, t / WriteStep),
                   Bezier(x2, x3, t / WriteStep), t / WriteStep)
        y = Bezier(Bezier(y1, y2, t / WriteStep),
                   Bezier(y2, y3, t / WriteStep), t / WriteStep)
        te.goto(x, y)
    te.penup()


def Bezier_3(x1, y1, x2, y2, x3, y3, x4, y4):  # Hàm Bézier bậc 3
    x1 = -Width / 2 + x1
    y1 = Height / 2 - y1
    x2 = -Width / 2 + x2
    y2 = Height / 2 - y2
    x3 = -Width / 2 + x3
    y3 = Height / 2 - y3
    x4 = -Width / 2 + x4
    y4 = Height / 2 - y4  # Biến đổi tọa độ
    te.goto(x1, y1)
    te.pendown()
    for t in range(0, WriteStep + 1):
        x = Bezier(Bezier(Bezier(x1, x2, t / WriteStep), Bezier(x2, x3, t / WriteStep), t / WriteStep),
                   Bezier(Bezier(x2, x3, t / WriteStep), Bezier(x3, x4, t / WriteStep), t / WriteStep), t / WriteStep)
        y = Bezier(Bezier(Bezier(y1, y2, t / WriteStep), Bezier(y2, y3, t / WriteStep), t / WriteStep),
                   Bezier(Bezier(y2, y3, t / WriteStep), Bezier(y3, y4, t / WriteStep), t / WriteStep), t / WriteStep)
        te.goto(x, y)
    te.penup()


def Moveto(x, y):  # Di chuyển đến tọa độ svg (x, y)
    te.penup()
    te.goto(-Width / 2 + x, Height / 2 - y)
    te.pendown()


def Moveto_r(dx, dy):
    te.penup()
    te.goto(te.xcor() + dx, te.ycor() - dy)
    te.pendown()


def line(x1, y1, x2, y2):  # Nối hai điểm dưới tọa độ svg
    te.penup()
    te.goto(-Width / 2 + x1, Height / 2 - y1)
    te.pendown()
    te.goto(-Width / 2 + x2, Height / 2 - y2)
    te.penup()


def Lineto_r(dx, dy):  # Nối điểm hiện tại với điểm có tọa độ tương đối (dx, dy)
    te.pendown()
    te.goto(te.xcor() + dx, te.ycor() - dy)
    te.penup()


def Lineto(x, y):  # Nối điểm hiện tại với tọa độ svg (x, y)
    te.pendown()
    te.goto(-Width / 2 + x, Height / 2 - y)
    te.penup()


def Curveto(x1, y1, x2, y2, x, y):  # Đường cong Bézier bậc 3 đến (x, y)
    te.penup()
    X_now = te.xcor() + Width / 2
    Y_now = Height / 2 - te.ycor()
    Bezier_3(X_now, Y_now, x1, y1, x2, y2, x, y)
    global Xh
    global Yh
    Xh = x - x2
    Yh = y - y2


def Curveto_r(x1, y1, x2, y2, x, y):  # Đường cong Bézier bậc 3 đến tọa độ tương đối (x, y)
    te.penup()
    X_now = te.xcor() + Width / 2
    Y_now = Height / 2 - te.ycor()
    Bezier_3(X_now, Y_now, X_now + x1, Y_now + y1,
             X_now + x2, Y_now + y2, X_now + x, Y_now + y)
    global Xh
    global Yh
    Xh = x - x2
    Yh = y - y2


def transform(w_attr):
    funcs = w_attr.split(' ')
    for func in funcs:
        func_name = func[0: func.find('(')]
        if func_name == 'scale':
            global scale
            scale = (float(func[func.find('(') + 1: -1].split(',')[0]),
                     -float(func[func.find('(') + 1: -1].split(',')[1]))


def readPathAttrD(w_attr):
    ulist = w_attr.split(' ')
    for i in ulist:
        # print("now cmd:", i)
        if i.isdigit() or i.isalpha():
            yield float(i)
        elif i[0].isalpha():
            yield i[0]
            yield float(i[1:])
        elif i[-1].isalpha():
            yield float(i[0: -1])
        elif i[0] == '-':
            yield float(i)


def drawSVG(filename, w_color):
    global first
    SVGFile = open(filename, 'r')
    SVG = BeautifulSoup(SVGFile.read(), 'lxml-xml')
    Height = float(SVG.svg.attrs['height'][0: -2])
    Width = float(SVG.svg.attrs['width'][0: -2])
    transform(SVG.g.attrs['transform'])
    if first:
        te.setup(height=Height, width=Width)
        te.setworldcoordinates(-Width / 2, 300, Width -
                               Width / 2, -Height + 300)
        first = False
    te.tracer(100)
    te.pensize(1)
    te.speed(Speed)
    te.penup()
    te.color(w_color)

    for i in SVG.find_all('path'):
        attr = i.attrs['d'].replace('\n', ' ')
        f = readPathAttrD(attr)
        lastI = ''
        for i in f:
            if i == 'M':
                te.end_fill()
                Moveto(next(f) * scale[0], next(f) * scale[1])
                te.begin_fill()
            elif i == 'm':
                te.end_fill()
                Moveto_r(next(f) * scale[0], next(f) * scale[1])
                te.begin_fill()
            elif i == 'C':
                Curveto(next(f) * scale[0], next(f) * scale[1],
                        next(f) * scale[0], next(f) * scale[1],
                        next(f) * scale[0], next(f) * scale[1])
                lastI = i
            elif i == 'c':
                Curveto_r(next(f) * scale[0], next(f) * scale[1],
                          next(f) * scale[0], next(f) * scale[1],
                          next(f) * scale[0], next(f) * scale[1])
                lastI = i
            elif i == 'L':
                Lineto(next(f) * scale[0], next(f) * scale[1])
            elif i == 'l':
                Lineto_r(next(f) * scale[0], next(f) * scale[1])
                lastI = i
            elif lastI == 'C':
                Curveto(i * scale[0], next(f) * scale[1],
                        next(f) * scale[0], next(f) * scale[1],
                        next(f) * scale[0], next(f) * scale[1])
            elif lastI == 'c':
                Curveto_r(i * scale[0], next(f) * scale[1],
                          next(f) * scale[0], next(f) * scale[1],
                          next(f) * scale[0], next(f) * scale[1])
            elif lastI == 'L':
                Lineto(i * scale[0], next(f) * scale[1])
            elif lastI == 'l':
                Lineto_r(i * scale[0], next(f) * scale[1])
    te.penup()
    te.hideturtle()
    te.update()
    SVGFile.close()


def drawBitmap(w_image):
    # Khởi tạo và phát nhạc
    pygame.init()
    mixer.init()
    mixer.music.load('music.mp3')  # Thay 'ten_file_nhac.mp3' bằng tên tệp nhạc của bạn
    mixer.music.play()
    
    print('Đang giảm số màu...')
    Z = w_image.reshape((-1, 3))

    # Chuyển đổi sang np.float32
    Z = np.float32(Z)

    # Định nghĩa tiêu chí, số cụm (K) và áp dụng kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS, 10, 1.0)
    global K
    ret, label, center = cv2.kmeans(
        Z, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    # Chuyển đổi lại thành uint8, và tạo ảnh gốc
    center = np.uint8(center)
    res = center[label.flatten()]
    res = res.reshape(w_image.shape)
    no = 1
    for i in center:
        sys.stdout.write('\rĐang vẽ: %.2f%% [' % (
            no / K * 100) + '#' * no + ' ' * (K - no) + ']')
        no += 1
        res2 = cv2.inRange(res, i, i)
        res2 = cv2.bitwise_not(res2)
        cv2.imwrite('.tmp.bmp', res2)
        os.system('potrace.exe .tmp.bmp -s --flat')
        drawSVG('.tmp.svg', '#%02x%02x%02x' % (i[2], i[1], i[0]))
    os.remove('.tmp.bmp')
    os.remove('.tmp.svg')
    print('\n\rHoàn tất, đóng cửa sổ để thoát.')
    te.done()


if __name__ == '__main__':
    paser = argparse.ArgumentParser(
        description="Chuyển đổi ảnh bitmap thành SVG và sử dụng thư viện turtle để vẽ nó.")
    paser.add_argument('filename', type=str, nargs='?', default='tuanhuyen.png',
                        help='Tên tệp (* .jpg, * .png, * .bmp) của tệp bạn muốn chuyển đổi. Mặc định là tuanhuyen.png')
    paser.add_argument(
        "-c", "--color", help="Số màu bạn muốn sử dụng. (Nếu số lượng màu quá lớn thì chương trình có thể chạy rất chậm.)", type=int, default=32)
    args = paser.parse_args()
    K = args.color
    try:
        bitmapFile = open(args.filename, mode='r')
    except FileNotFoundError:
        print(__file__ + ': error: Tệp không tồn tại.')
        sys.exit()  # Exit if the file doesn't exist

    if os.path.splitext(args.filename)[1].lower() not in ['.jpg', '.bmp', '.png']:
        print(__file__ + ': error: Tệp không phải là tệp bitmap.')
        sys.exit()  # Exit if the file is not a bitmap

    bitmap = cv2.imread(args.filename)
    if bitmap.shape[0] > GetSystemMetrics(1):
        bitmap = cv2.resize(bitmap, (int(bitmap.shape[1] * (
            (GetSystemMetrics(1) - 50) / bitmap.shape[0])), GetSystemMetrics(1) - 50))
    drawBitmap(bitmap)

    print("Chúc thanh huyn giáng sinh zui zẻ.")
    sys.exit()
