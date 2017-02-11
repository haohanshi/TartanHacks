__author__ = 'liukaige'
import json

jsonData = {}

with open("data/"+"S"+'.json') as data_file:
    jsonData["S"] = json.load(data_file)
with open("data/"+"F"+'.json') as data_file:
    jsonData["F"] = json.load(data_file)
with open("data/"+"M1"+'.json') as data_file:
    jsonData["M1"] = json.load(data_file)
with open("data/"+"M2"+'.json') as data_file:
    jsonData["M2"] = json.load(data_file)
with open("data/"+"S"+'.json') as data_file:
    jsonData["S"] = json.load(data_file)




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
            portion = upperInt(len(coursesInfo[i]["lectures"])/len(coursesInfo[i]["sections"]))
            timeSlots+= parseTimeSlots(coursesInfo[i]["lectures"][order[i]]["times"])
            timeSlots+= parseTimeSlots(coursesInfo[i]["sections"][int(order[i]/portion)]["times"])
        else:
            portion = upperInt(len(coursesInfo[i]["sections"])/len(coursesInfo[i]["lectures"]))
            timeSlots+=(parseTimeSlots(coursesInfo[i]["sections"][order[i]]["times"]))
            timeSlots+= parseTimeSlots(coursesInfo[i]["lectures"][int(order[i]/portion)]["times"])
    for i in range(len(timeSlots)-1):
        for j in range(i+1,len(timeSlots)):
            if timeSlots[i][1] > timeSlots[j][0] and timeSlots[i][1] <= timeSlots[j][1]:
                return True
            if timeSlots[i][0] >= timeSlots[j][0] and timeSlots[i][0] < timeSlots[j][1]:
                return True
    print(timeSlots)
    return False



def getPossibleSchedules(listOfCourseNameMust,listOfCourseNameOptional,semester,numberOfOptionals):
    with open("data/"+semester+'.json') as data_file:
        data = json.load(data_file)
    classInfoMust = []
    classInfoOptional = []
    for i in listOfCourseNameMust:
        classInfoMust.append(data["courses"][i])
        for section in data["courses"][i]["sections"]:
            if section["times"][0]["location"] == "Doha, Qatar":
                data["courses"][i]["sections"].remove(section)
        for lecture in data["courses"][i]["lectures"]:
            if lecture["times"][0]["location"] == "Doha, Qatar":
                data["courses"][i]["lectures"].remove(lecture)

    for i in listOfCourseNameOptional:
        classInfoOptional.append(data["courses"][i])
        for section in data["courses"][i]["sections"]:
            if section["times"][0]["location"] == "Doha, Qatar":
                data["courses"][i]["sections"].remove(section)
        for lecture in data["courses"][i]["lectures"]:
            if lecture["times"][0]["location"] == "Doha, Qatar":
                data["courses"][i]["lectures"].remove(lecture)

    schedules = []

    mustIfUseLectureAsIndex = []
    mustMaxIndexOfTimeChoices = []

    optionalIfUseLectureAsIndex = []
    optionalMaxIndexOfTimeChoices = []

    for info in classInfoMust:
        if (len(info["sections"]) < len(info["lectures"])):
            mustIfUseLectureAsIndex.append(True)
            mustMaxIndexOfTimeChoices.append(len(info["lectures"]))
        else:
            mustIfUseLectureAsIndex.append(False)
            mustMaxIndexOfTimeChoices.append(len(info["sections"]))

    for info in classInfoOptional:
        if (len(info["sections"]) < len(info["lectures"])):
            optionalIfUseLectureAsIndex.append(True)
            optionalMaxIndexOfTimeChoices.append(len(info["lectures"]))
        else:
            optionalIfUseLectureAsIndex.append(False)
            optionalMaxIndexOfTimeChoices.append(len(info["sections"]))
    indexesForOptionals = []
    for i in range(len(listOfCourseNameOptional)):
        indexesForOptionals.append(i)

    allCombinations = comb(indexesForOptionals,numberOfOptionals)
    for thisComb in allCombinations:
        currentIndexes = []
        ifLectures = []
        currentMaxes = []
        coursesInfo = []
        for i in range(numberOfOptionals + len(listOfCourseNameMust)):
            currentIndexes.append(0)
        for i in range(len(listOfCourseNameMust)):
            coursesInfo.append(classInfoMust[i])
            ifLectures.append(mustIfUseLectureAsIndex[i])
            currentMaxes.append(mustMaxIndexOfTimeChoices[i])
        for i in thisComb:
            coursesInfo.append(classInfoOptional[i])
            ifLectures.append(optionalIfUseLectureAsIndex[i])
            currentMaxes.append(optionalMaxIndexOfTimeChoices[i])
        while not ifMax(currentIndexes,currentMaxes):
            if not ifOverlap(coursesInfo,currentIndexes,ifLectures):
                pass
                #print(currentIndexes)
            incrementArray(currentIndexes,currentMaxes)


getPossibleSchedules(["15-214","15-251","15-150","80-150","21-269"],[],"S",0)