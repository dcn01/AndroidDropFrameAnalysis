#!/bin/env python
# coding:utf-8
import datetime
import json
import threading
import subprocess
import sys
import time
import re
import traceback
import xlwt
import math
from uiautomator import device as d
from time import sleep

patternFps = re.compile(r'[\s]+[\d]+.[\d]+[\s]+[\d]+.[\d]+[\s]+[\d]+.[\d]+[\s\S]*')
patternProfileData = re.compile(r'[\d]+,[\d]+,[\d]+,[\s\S]*')


def BeforeTestCommon():
    print("install start-up and screen-on")
    d.screen.on()
    print("unlock")
    d(index="0").swipe.up(steps=10)
    print("home")
    d.press.home()
    print("menu")
    d.press.menu()
    d(resourceId="com.android.systemui:id/clearButton").click()
    print("click clearButton")
    d.server.adb.cmd("shell", "am", "start", "-n", "com.miui.gallery/.activity.HomePageActivity")
    print("am start gallery")


def prepare_C_SlideLargeImage():
    try:
        uiselectobj = d(resourceId="com.miui.gallery:id/grid").child(className="android.widget.RelativeLayout",
                                                                     instance=0)
        if uiselectobj.count > 0:
            isclick = uiselectobj.click()
            print("isclick " + str(isclick))
        else:
            print("warning:no photo in home page!")
        sleep(1.2)
    except:
        traceback.print_exc()


def reset():
    print("gfxinfo reset")
    d.server.adb.cmd("shell", "dumpsys", "gfxinfo", "com.miui.gallery", "reset")
    sleep(1)
    print("sleep 1 second finished")


def swipePhotoPage():
    print("begin swipePhotoPage:" + str(datetime.datetime.now()))
    try:
        for i in range(5):
            for j in range(10):
                if j % 2 == 0:
                    sleep(0.5)
                if i % 2 == 0:
                    d(resourceId="com.miui.gallery:id/photo_pager").swipe.left()
                else:
                    d(resourceId="com.miui.gallery:id/photo_pager").swipe.right()

    except:
        traceback.print_exc()


def startTest():
    BeforeTestCommon()
    prepare_C_SlideLargeImage()
    reset()
    swipePhotoPage()
    getSystemDropRate()
    getFinalResult()


def getSystemDropRate():
    print("collecting results")
    intoGallery = "adb shell dumpsys gfxinfo com.miui.gallery framestats"
    process = subprocess.Popen(intoGallery, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    profileText = open('./output/C_SlideLargeImage/txt/SystemDumpAll.txt', 'w')
    while True:
        nextline = process.stdout.readline()
        nextlineDecode = nextline.decode()
        if nextlineDecode == "" or nextlineDecode is None:
            break
        profileText.write(nextlineDecode)
    print("collecting results end")


def getFinalResult():
    print("generating results")
    intoGallery = "adb shell dumpsys gfxinfo com.miui.gallery framestats"
    process = subprocess.Popen(intoGallery, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    profileText = open('./output/C_SlideLargeImage/FinalResult.txt', 'w')
    while True:
        nextline = process.stdout.readline()
        nextlineDecode = nextline.decode()
        if nextlineDecode == "" or nextlineDecode is None:
            break
        if nextlineDecode.find("Graphics info") != -1:
            profileText.write(nextlineDecode.strip())
            profileText.write("\n")
            for i in range(0, 9):
                nextline = process.stdout.readline()
                nextlineDecode = nextline.decode()
                profileText.write(nextlineDecode.strip())
                profileText.write("\n")
            print("generating results end")
            return


if __name__ == '__main__':
    startTest()


# d(text="相册").click()
#
# d(text="相机").click()
# while True:
#     isb = d(resourceId="com.miui.gallery:id/grid").scroll.vert.forward(steps=10)
#     if isb==False:
#         break;
# uiselect = d(className="android.widget.ListView", resourceId="com.miui.gallery:id/album_list").child(className="android.widget.RelativeLayout")
# uiobj = d(className="android.widget.ListView", resourceId="com.miui.gallery:id/album_list").child(className="android.widget.RelativeLayout",instance=1)
# uiobj.click()
