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


def prepare_A_PhotoSlide():
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
    while True:
        isend = d(resourceId="com.miui.gallery:id/grid").scroll.vert.forward(steps=10)
        if isend == False:
            break


def dumpsysFramestats():
    print("begin dumpsysFramestats:" + str(datetime.datetime.now()))
    intoGallery = "adb shell dumpsys gfxinfo com.miui.gallery framestats"
    process = subprocess.Popen(intoGallery, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    countFailGetFps = -1
    thisTimeHasFps = False
    profileText = open('./output/A_PhotoSlide/txt/AllFrame.txt', 'w')
    profileText.write("###########################################" + str(countFailGetFps) + "\n")
    while True:
        nextline = process.stdout.readline()
        matchFps = patternFps.match(nextline.decode())
        if matchFps:
            thisTimeHasFps = True
            profileText.write(nextline.decode())
        else:
            matchProfileData = patternProfileData.match(nextline.decode())
            if matchProfileData and thisTimeHasFps:
                profileText.write(nextline.decode())

        if "Total DisplayList" in nextline.decode():
            if (thisTimeHasFps):
                thisTimeHasFps = False
            else:
                countFailGetFps += 1
            if countFailGetFps > 10:
                break
            profileText.write("###########################################" + str(countFailGetFps) + "\n")
            sleep(1.2)
            process = subprocess.Popen(intoGallery, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def threadWillBeStart():
    print("threadWillBeStart" )
    threads = []
    t1 = threading.Thread(target=swipePhotoPage, args=())
    threads.append(t1)
    t2 = threading.Thread(target=dumpsysFramestats, args=())
    threads.append(t2)
    
    for t in threads:
        t.setDaemon(True)
        t.start()
    
    for t in threads:
        t.join()
    print("threadWillBeEnd start processResult" )
    
def countSplitByComma(splitByComma,i, j):
    return (float(splitByComma[i]) - float(splitByComma[j])) / 1000000

def beginProcessResult():
    print("begin processResult:" + str(datetime.datetime.now()))
    fpsReadList = []
    profileDataReadList = []
    fpsTmpReadList = []
    profileDataTmpReadList = []
    profileRead = open('./output/A_PhotoSlide/txt/AllFrame.txt', 'r')
    for line in profileRead.readlines():
        if "####" in line:
            for fpstmpreadlist in fpsTmpReadList:
                fpsReadList.append(fpstmpreadlist)
            fpstmpreadlistlen = len(fpsTmpReadList)
            profiledatareadlistlen = len(profileDataTmpReadList)
            startFps = profiledatareadlistlen - fpstmpreadlistlen
            for i in range(startFps, profiledatareadlistlen):
                profileDataReadList.append(profileDataTmpReadList[i])
            fpsTmpReadList = []
            profileDataTmpReadList = []
        matchFps = patternFps.match(line)
        if matchFps:
            fpsTmpReadList.append(line)
        matchProfileData = patternProfileData.match(line)
        if matchProfileData:
            profileDataTmpReadList.append(line)
    
    fpsReadListLen = len(fpsReadList)
    profileDataReadListLen = len(profileDataReadList)
    
    print("FourFrameLength=" + str(fpsReadListLen) + " ; NineFrameLength=" + str(profileDataReadListLen))
    
    fpsAllFrameRead = open("./output/A_PhotoSlide/txt/FourFrame.txt", "w")
    for fpsallframe in fpsReadList:
        fpsAllFrameRead.write(fpsallframe)
    profileAllFrameRead = open("./output/A_PhotoSlide/txt/NineFrame.txt", "w")
    for profileallframe in profileDataReadList:
        profileAllFrameRead.write(profileallframe)
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('FourFrame统计')
    ws.write(0, 0, "Draw")
    ws.write(0, 1, "Prepare")
    ws.write(0, 2, "Process")
    ws.write(0, 3, "Execute")
    ws.write(0, 4, "All")
    ws.write(0, 5, "TimeOut")
    ws.write(0, 6, "SkipFrame")
    ws.write(0, 7, "SkipFrameSum")
    ws.write(0, 8, "DropRate")
    recordRow = 1
    skipFrameSum = 0.0
    for line in fpsReadList:
        splitByT = line.split("\t")
        ws.write(recordRow, 0, splitByT[1])
        ws.write(recordRow, 1, splitByT[2])
        ws.write(recordRow, 2, splitByT[3])
        ws.write(recordRow, 3, splitByT[4].strip())
        allTime = float(splitByT[1]) + float(splitByT[2]) + float(splitByT[3]) + float(splitByT[4].strip())
        ws.write(recordRow, 4, str(allTime))
        timeout = allTime / (1000.00 / 60.00)
        ws.write(recordRow, 5, str(timeout))
        skipFrame = math.ceil(timeout) - 1.00
        ws.write(recordRow, 6, str(skipFrame))
        skipFrameSum = skipFrameSum + skipFrame
        ws.write(recordRow, 7, str(skipFrameSum))
        DropRate = skipFrameSum/(skipFrameSum + recordRow)
        ws.write(recordRow, 8, str(DropRate))
        recordRow += 1
    wb.save('./output/A_PhotoSlide/excel/FourFrame.xlsx')
    
    fin = ""
    c = 0
    e = len(fpsReadList)
    for tmplist in fpsReadList:
        splitByT = tmplist.split("\t")
        if c == 0:
            fin = fin + "{"
        if c == e - 1:
            fin = fin + str(c) + ":{\"Draw\":" + splitByT[1] + ",\"Prepare\":" + splitByT[2] + ",\"Process\":" + splitByT[
                3] + ",\"Execute\":" + splitByT[4].strip() + "}}"
        else:
            fin = fin + str(c) + ":{\"Draw\":" + splitByT[1] + ",\"Prepare\":" + splitByT[2] + ",\"Process\":" + splitByT[
                3] + ",\"Execute\":" + splitByT[4].strip() + "},"
        c = c + 1
    frameCount = 25 * e + 50
    fin = "var person_data = " + fin + ";\nvar svg_width = " + str(frameCount) + ";"
    dataWrite = open("./output/A_PhotoSlide/html/FourFrame/js/data.js", "w")
    dataWrite.write(fin)
    print("FourFrameEnd")
    
    fin = ""
    c = 0
    e = len(profileDataReadList)
    for tmplist in profileDataReadList:
        splitByComma = tmplist.split(",")
        Vsync_IntendedVsync = countSplitByComma(splitByComma,2, 1)
        HandleInputStart_Vsync = countSplitByComma(splitByComma,5, 2)
        AnimationStart_HandleInputStart = countSplitByComma(splitByComma,6, 5)
        PerformTraversalsStart_AnimationStart = countSplitByComma(splitByComma,7, 6)
        DrawStart_PerformTraversalsStart = countSplitByComma(splitByComma,8, 7)
        SyncQueued_DrawStart = countSplitByComma(splitByComma,9, 8)
        SyncStart_SyncQueued = countSplitByComma(splitByComma,10, 9)
        IssueDrawCommandsStart_SyncStart = countSplitByComma(splitByComma,11, 10)
        FrameCompleted_IssueDrawCommandsStart = countSplitByComma(splitByComma,13, 11)
        # if Vsync_IntendedVsync!=0:
        # print(str(Vsync_IntendedVsync))
        if c == 0:
            fin = fin + "{"
        fin = fin + str(c) + ":{\"Vsync_IntendedVsync\":" + str(Vsync_IntendedVsync) + ",\"HandleInputStart_Vsync\":" + str(
            HandleInputStart_Vsync) + ",\"AnimationStart_HandleInputStart\":" + str(
            AnimationStart_HandleInputStart) + ",\"PerformTraversalsStart_AnimationStart\":" + str(
            PerformTraversalsStart_AnimationStart) + ",\"DrawStart_PerformTraversalsStart\":" + str(
            DrawStart_PerformTraversalsStart) + ",\"SyncQueued_DrawStart\":" + str(
            SyncQueued_DrawStart) + ",\"SyncStart_SyncQueued\":" + str(
            SyncStart_SyncQueued) + ",\"IssueDrawCommandsStart_SyncStart\":" + str(
            IssueDrawCommandsStart_SyncStart) + ",\"FrameCompleted_IssueDrawCommandsStart\":" + str(
            FrameCompleted_IssueDrawCommandsStart) + "}"
        if c == e - 1:
            fin = fin + "}"
        else:
            fin = fin + ","
        c = c + 1

    frameCount = 25 * e + 50
    fin = "var person_data = " + fin + ";\nvar svg_width = " + str(frameCount) + ";"
    dataWrite = open("./output/A_PhotoSlide/html/NineFrame/js/data.js", "w")
    dataWrite.write(fin)
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('NineFrame统计')
    ws.write(0, 0, "Vsync_IntendedVsync")
    ws.write(0, 1, "HandleInputStart_Vsync")
    ws.write(0, 2, "AnimationStart_HandleInputStart")
    ws.write(0, 3, "PerformTraversalsStart_AnimationStart")
    ws.write(0, 4, "DrawStart_PerformTraversalsStart")
    ws.write(0, 5, "SyncQueued_DrawStart")
    ws.write(0, 6, "SyncStart_SyncQueued")
    ws.write(0, 7, "IssueDrawCommandsStart_SyncStart")
    ws.write(0, 8, "FrameCompleted_IssueDrawCommandsStart")
    ws.write(0, 9, "All")
    ws.write(0, 10, "TimeOut")
    ws.write(0, 11, "SkipFrame")
    ws.write(0, 12, "SkipFrameSum")
    ws.write(0, 13, "DropRate")
    recordRow = 1
    skipFrameSum = 0.0
    for tmplist in profileDataReadList:
        splitByComma = tmplist.split(",")
        Vsync_IntendedVsync = countSplitByComma(splitByComma,2, 1)
        HandleInputStart_Vsync = countSplitByComma(splitByComma,5, 2)
        AnimationStart_HandleInputStart = countSplitByComma(splitByComma,6, 5)
        PerformTraversalsStart_AnimationStart = countSplitByComma(splitByComma,7, 6)
        DrawStart_PerformTraversalsStart = countSplitByComma(splitByComma,8, 7)
        SyncQueued_DrawStart = countSplitByComma(splitByComma,9, 8)
        SyncStart_SyncQueued = countSplitByComma(splitByComma,10, 9)
        IssueDrawCommandsStart_SyncStart = countSplitByComma(splitByComma,11, 10)
        FrameCompleted_IssueDrawCommandsStart = countSplitByComma(splitByComma,13, 11)
    
        ws.write(recordRow, 0, Vsync_IntendedVsync)
        ws.write(recordRow, 1, HandleInputStart_Vsync)
        ws.write(recordRow, 2, AnimationStart_HandleInputStart)
        ws.write(recordRow, 3, PerformTraversalsStart_AnimationStart)
        ws.write(recordRow, 4, DrawStart_PerformTraversalsStart)
        ws.write(recordRow, 5, SyncQueued_DrawStart)
        ws.write(recordRow, 6, SyncStart_SyncQueued)
        ws.write(recordRow, 7, IssueDrawCommandsStart_SyncStart)
        ws.write(recordRow, 8, FrameCompleted_IssueDrawCommandsStart)
        allTime = Vsync_IntendedVsync + HandleInputStart_Vsync + AnimationStart_HandleInputStart + PerformTraversalsStart_AnimationStart + DrawStart_PerformTraversalsStart + SyncQueued_DrawStart + SyncStart_SyncQueued + IssueDrawCommandsStart_SyncStart+FrameCompleted_IssueDrawCommandsStart
        ws.write(recordRow, 9, str(allTime))
        timeout = allTime / (1000.00 / 60.00)
        ws.write(recordRow, 10, str(timeout))
        skipFrame = math.ceil(timeout) - 1.00
        ws.write(recordRow, 11, str(skipFrame))
        skipFrameSum = skipFrameSum + skipFrame
        ws.write(recordRow, 12, str(skipFrameSum))
        DropRate = skipFrameSum/(skipFrameSum + recordRow)
        ws.write(recordRow, 13, str(DropRate))
        recordRow += 1
    wb.save('./output/A_PhotoSlide/excel/NineFrame.xlsx')
    print("NineFrameEnd")


def startTest():
    BeforeTestCommon()
    prepare_A_PhotoSlide()
    reset()
    threadWillBeStart()
    beginProcessResult()
    getSystemDropRate()
    getFinalResult()
def getSystemDropRate():
    print("collecting results")
    intoGallery = "adb shell dumpsys gfxinfo com.miui.gallery framestats"
    process = subprocess.Popen(intoGallery, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    profileText = open('./output/A_PhotoSlide/txt/SystemDumpAll.txt', 'w')
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
    profileText = open('./output/A_PhotoSlide/FinalResult.txt', 'w')
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
