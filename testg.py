# fpsAllFrameRead = open("profileAllFrame.txt", "r")
# profileDataReadList =[]
# t = []
# for line in fpsAllFrameRead.readlines():
#     profileDataReadList.append(line)
#
# for line in profileDataReadList:
#     splitByComma = line.split(",")
#     l = len(splitByComma)
#     print str(l)

a = 34.4/(1000/60)
print str(a)

# fin = ""
# c = 0
# e = len(willBeInsertIntoSqlList)
# for tmplist in willBeInsertIntoSqlList:
#     splitByT =  tmplist.split("\t")
#     if c==0:
#         fin = fin +"{"
#     
#     if c==e -1:
#         fin = fin+str(c)+":{\"Draw\":"+splitByT[1]+",\"Prepare\":"+splitByT[2]+",\"Process\":"+splitByT[3]+",\"Execute\":"+splitByT[4].strip()+"}}"
#     else:
#         fin = fin+str(c)+":{\"Draw\":"+splitByT[1]+",\"Prepare\":"+splitByT[2]+",\"Process\":"+splitByT[3]+",\"Execute\":"+splitByT[4].strip()+"},"
#         
#     c = c+1
# fin = "var person_data = "+fin+";\nvar svg_width = 88350;"
# dataWrite = open("./output/js/data.js", "w")
# dataWrite.write(fin)
