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


def prepare_B_ClickLargeImage_():
    try:
        gridTop = ""
        gridinfo = d(resourceId="com.miui.gallery:id/grid").info
        gridjson = json.dumps(gridinfo)
        gridjson = json.loads(gridjson)
        for key in gridjson.keys():
            boundsVal = gridjson[key]
            if key == "bounds":
                boundsVal = json.dumps(boundsVal)
                boundsValJson = json.loads(boundsVal)
                gridTop = boundsValJson["top"]
    
        action_barBottomTop = ""
        action_barBottominfo = d(resourceId="miui:id/action_bar").info
        action_barBottominfo = json.dumps(action_barBottominfo)
        action_barBottominfo = json.loads(action_barBottominfo)
        for key in action_barBottominfo.keys():
            boundsVal = action_barBottominfo[key]
            if key == "bounds":
                boundsVal = json.dumps(boundsVal)
                boundsValJson = json.loads(boundsVal)
                action_barBottomTop = boundsValJson["bottom"]
        if gridTop != action_barBottomTop:
            print(str(action_barBottomTop) + "Unequal" + str(gridTop))
            d(resourceId="com.miui.gallery:id/grid").scroll.vert.forward(steps=10)
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
        for i in range(0,3):
            for i in range(0,100):
                uiselectobj = d(resourceId="com.miui.gallery:id/grid").child(className="android.widget.RelativeLayout",instance=i)
                if uiselectobj.count > 0:
                    uiselectobj.click()
                    sleep(1.2)
                    d.press.back()
                    sleep(1.2)
    except:
        traceback.print_exc()
        

    
     

def startTest():
    BeforeTestCommon()
    prepare_B_ClickLargeImage_()
    reset()
    swipePhotoPage()
    getSystemDropRate()
    getFinalResult()
def getSystemDropRate():
    print("collecting results")
    intoGallery = "adb shell dumpsys gfxinfo com.miui.gallery framestats"
    process = subprocess.Popen(intoGallery, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    profileText = open('./output/B_ClickLargeImage_/txt/SystemDumpAll.txt', 'w')
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
    profileText = open('./output/B_ClickLargeImage_/FinalResult.txt', 'w')
    while True:
        nextline = process.stdout.readline()
        nextlineDecode = nextline.decode()
        if nextlineDecode == "" or nextlineDecode is None:
            break
        if nextlineDecode.find("Graphics info") != -1:
            profileText.write(nextlineDecode.strip())
            profileText.write("\n")
            for i in range(0,9):
                nextline = process.stdout.readline()
                nextlineDecode = nextline.decode()
                profileText.write(nextlineDecode.strip())
                profileText.write("\n")
            print("generating results end")
            return



if __name__ == '__main__':
    startTest()