__author__ = 'liukaige'
def upperInt(x):
    if x%1 == 0:
        return int(x)
    else:
        return int(x) + 1

def evval(s):
    if s[0] == "0":
        return eval(s[1:])
    else:
        return eval(s)

def comb(arr,k):
    if len(arr) == k:
        return [arr]
    if k == 0:
        return [[]]
    else:
        rec1 = comb(arr[1:],k)
        rec2 = comb(arr[1:],k-1)
        result = []
        for i in rec1:
            result.append(i)
        for i in rec2:
            result.append([arr[0]] + i)
    return result

def parseTimeSlots(tt):
    result = []
    for t in tt:
        begin = 0.0
        end = 0.0
        if t["begin"][:2] == "12" and t["begin"][-2:] == "PM":
            if t["begin"][-4:-2] == "20":
                begin = 12.5
            else:
                begin = 13.0
        else:
            if t["begin"][-4:-2] == "20" or t["begin"][-4:-2] == "30":
                begin = evval(t["begin"][:t["begin"].index(":")]) + 0.5
            elif t["begin"][-4:-2] == "00":
                begin = evval(t["begin"][:t["begin"].index(":")])
            else:
                begin = evval(t["begin"][:t["begin"].index(":")]) + 1
            if t["begin"][-2:] == "PM":
                begin += 12.0

        if t["end"][:2] == "12" and t["end"][-2:] == "PM":
            if t["end"][-4:-2] == "20":
                end = 12.5
            else:
                end = 13.0
        else:
            if t["end"][-4:-2] == "20" or t["begin"][-4:-2] == "30":
                end = evval(t["end"][:t["end"].index(":")]) + 0.5
            elif t["begin"][-4:-2] == "00":
                begin = evval(t["begin"][:t["begin"].index(":")])
            else:
                end = evval(t["end"][:t["end"].index(":")]) + 1
            if t["end"][-2:] == "PM":
                end += 12.0
        for day in t["days"]:
            result.append((100*day+begin,100*day + end))
    return result

def ifMax(cur,maxx):
    for i in range(0,len(cur)):
        if cur[i] < maxx[i] - 1:
            return False
    return True

def incrementArray(cur,maxx):
    i = 0
    cur[0] += 1
    while cur[i] == maxx[i]:
        cur[i] = 0
        cur[i+1] += 1
        i += 1

def ifOverlap(coursesInfo,order,ifUseLectureAsIndex):
    timeSlots = []
    for i in range(len(order)):
        if ifUseLectureAsIndex[i]:
            added = parseTimeSlots(coursesInfo[i]["lectures"][order[i]]["times"])
            for t in added:
                timeSlots.append((t,i))
            if not len(coursesInfo[i]["sections"]) == 0:
                portion = upperInt(len(coursesInfo[i]["lectures"])/len(coursesInfo[i]["sections"]))
                added = parseTimeSlots(coursesInfo[i]["sections"][int(order[i]/portion)]["times"])
                for t in added:
                    timeSlots.append((t,i))
        else:
            added = (parseTimeSlots(coursesInfo[i]["sections"][order[i]]["times"]))
            for t in added:
                timeSlots.append((t,i))
            if not len(coursesInfo[i]["lectures"]) == 0:
                portion = upperInt(len(coursesInfo[i]["sections"])/len(coursesInfo[i]["lectures"]))
                added = parseTimeSlots(coursesInfo[i]["lectures"][int(order[i]/portion)]["times"])
                for t in added:
                    timeSlots.append((t,i))
    for i in range(len(timeSlots)-1):
        for j in range(i+1,len(timeSlots)):
            if timeSlots[i][0][1] > timeSlots[j][0][0] and timeSlots[i][0][1] <= timeSlots[j][0][1]:
                return (True,(timeSlots[i][1],timeSlots[j][1]))
            if timeSlots[i][0][0] >= timeSlots[j][0][0] and timeSlots[i][0][0] < timeSlots[j][0][1]:
                return (True,(timeSlots[i][1],timeSlots[j][1]))
    return (False,())

def extractIDInfo(coursesInfo,currentIndexes,ifLectures,coursesNames):
    result = {}
    for i in range(len(ifLectures)):
        if ifLectures[i]:
            lecture = coursesInfo[i]["lectures"][currentIndexes[i]]["name"]
            if (len(coursesInfo[i]["sections"]) == 0):
                section = ""
            else:
                portion = upperInt(len(coursesInfo[i]["lectures"])/len(coursesInfo[i]["sections"]))
                section = coursesInfo[i]["sections"][int(currentIndexes[i]/portion)]["name"]
        else:
            section = coursesInfo[i]["sections"][currentIndexes[i]]["name"]
            if (len(coursesInfo[i]["lectures"]) == 0):
                lecture = ""
            else:
                portion = upperInt(len(coursesInfo[i]["sections"])/len(coursesInfo[i]["lectures"]))
                lecture = coursesInfo[i]["lectures"][int(currentIndexes[i]/portion)]["name"]

        result[coursesNames[i]] = (lecture,section)
    return result

def match(overlapFormat, order):
    for i in range(len(overlapFormat)):
        if not overlapFormat[i] == order[i] and not overlapFormat[i] == -1:
            return False
    return True