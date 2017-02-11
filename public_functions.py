__author__ = 'liukaige'
import json
import csv
from private_functions import *

jsonData = {}

with open("data/"+"S"+'.json') as data_file:
    jsonData["S"] = json.load(data_file)
with open("data/"+"F"+'.json') as data_file:
    jsonData["F"] = json.load(data_file)
with open("data/"+"M1"+'.json') as data_file:
    jsonData["M1"] = json.load(data_file)
with open("data/"+"M2"+'.json') as data_file:
    jsonData["M2"] = json.load(data_file)

fceData = []
for i in range(0,8):
    with open("data/"+ str(i) +".csv") as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            fceData.append(row)



j = 0
for semester in ["S","F","M1","M2"]:
    for key in jsonData[semester]["courses"]:
        course = jsonData[semester]['courses'][key]
        while j < len(course["sections"]):
            section = course["sections"][j]
            if section["times"][0]["location"] == "Doha, Qatar":
                course["sections"].remove(section)
            else:
                j += 1

        j = 0
        while j < len(course["lectures"]):
            lecture = course["lectures"][j]
            if lecture["times"][0]["location"] == "Doha, Qatar":
                course["lectures"].remove(lecture)
            else:
                j += 1



def getPossibleSchedules(listOfCourseNameMust,listOfCourseNameOptional,semester,numberOfOptionals):
    classInfoMust = []
    classInfoOptional = []
    for i in listOfCourseNameMust:
        classInfoMust.append(jsonData[semester]["courses"][i])

    for i in listOfCourseNameOptional:
        classInfoOptional.append(jsonData[semester]["courses"][i])

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
    scheduels = []
    for thisComb in allCombinations:
        currentIndexes = []
        currentCoursesName = []
        ifLectures = []
        currentMaxes = []
        coursesInfo = []
        for i in range(numberOfOptionals + len(listOfCourseNameMust)):
            currentIndexes.append(0)
        for i in range(len(listOfCourseNameMust)):
            coursesInfo.append(classInfoMust[i])
            ifLectures.append(mustIfUseLectureAsIndex[i])
            currentMaxes.append(mustMaxIndexOfTimeChoices[i])
            currentCoursesName.append(listOfCourseNameMust[i])
        for i in thisComb:
            coursesInfo.append(classInfoOptional[i])
            ifLectures.append(optionalIfUseLectureAsIndex[i])
            currentMaxes.append(optionalMaxIndexOfTimeChoices[i])
            currentCoursesName.append(listOfCourseNameOptional[i])

        overLaps = []
        while not ifMax(currentIndexes,currentMaxes):
            overlapResult = ifOverlap(coursesInfo,currentIndexes,ifLectures)
            if not overlapResult[0]:
                schedule = extractIDInfo(coursesInfo,currentIndexes,ifLectures,currentCoursesName)
                schedules.append(schedule)
            else:
                overlap = []
                skip = False
                for k in overLaps:
                    if match(k,currentIndexes):
                        skip = True
                if not skip:
                    for i in range(len(currentCoursesName)):
                        overlap.append(-1)
                    overlap[overlapResult[1][0]] = currentIndexes[overlapResult[1][0]]
                    overlap[overlapResult[1][1]] = currentIndexes[overlapResult[1][1]]
                    existAlready = False
                    for thisOverlap in overLaps:
                        same = True
                        for i in range(len(thisOverlap)):
                            if not thisOverlap[i] == overlap[i]:
                                same = False
                        if same:
                            existAlready = True
                    if not existAlready:
                        overLaps.append(overlap)
            incrementArray(currentIndexes,currentMaxes)
        #add last element
        overlapResult = ifOverlap(coursesInfo,currentIndexes,ifLectures)
        if not overlapResult[0]:
            schedule = extractIDInfo(coursesInfo,currentIndexes,ifLectures,currentCoursesName)
            schedules.append(schedule)
        else:
            overlap = []
            skip = False
            for k in overLaps:
                if match(k,currentIndexes):
                    skip = True
            if not skip:
                for i in range(len(currentCoursesName)):
                    overlap.append(-1)
                overlap[overlapResult[1][0]] = currentIndexes[overlapResult[1][0]]
                overlap[overlapResult[1][1]] = currentIndexes[overlapResult[1][1]]
                existAlready = False
                for thisOverlap in overLaps:
                    same = True
                    for i in range(len(thisOverlap)):
                        if not thisOverlap[i] == overlap[i]:
                            same = False
                    if same:
                        existAlready = True
                if not existAlready:
                    overLaps.append(overlap)

    return schedules

def sortSchedulesByCompactness(g,semester):
    return sorted(g,key = lambda schedule : compactIndex(schedule,jsonData[semester]))


def filterSchedules(g,semester,args):
    results = []
    if "getuptime" in args:
        getuptime = args["getuptime"]
    else:
        getuptime = 0
    if "getbacktime" in args:
        getbacktime = args["getbacktime"]
    else:
        getbacktime = 24
    needToCheckLunch = True
    if "lunchtime" in args:
        needToCheckLunch = True
        lunchtime = args["lunchtime"]
    for k in g:
        if not getUpTooEarly(k,jsonData[semester],getuptime,getbacktime):
            if needToCheckLunch:
                if lunchTime(k,jsonData[semester],lunchtime[0],lunchtime[1],lunchtime[2]):
                    results.append(k)
            else:
                results.append(k)
    return results

def produceFullInfoForSchedule(schedule,semester):
    results = {}
    for c in schedule:
        lectureName = schedule[c][0]
        sectionName = schedule[c][1]
        result = {}
        result["courseName"] = jsonData[semester]["courses"][c]["name"]
        lectureDict = {}
        lectureDict["lectureName"] = lectureName
        for l in jsonData[semester]["courses"][c]["lectures"]:
            if l["name"]== lectureName:
                theLecture = l
                break
        lectureTimes = []
        lectureDays = []
        for t in theLecture["times"]:
            lectureDays += (t["days"])
            for j in range(len(t["days"])):
                lectureTimes.append([parseTimeTo24(t["begin"]),parseTimeTo24(t["end"])])
        lectureDict["lectureTime"] = lectureTimes
        lectureDict["lectureDays"] = lectureDays


        sectionDict = {}
        sectionDict["sectionName"] = "Sec "+sectionName
        for l in jsonData[semester]["courses"][c]["sections"]:
            if l["name"]== sectionName:
                theSection = l
                break
        sectionTimes = []
        sectionDays = []
        for t in theSection["times"]:
            sectionDays += (t["days"])
            for j in range(len(t["days"])):
                sectionTimes.append([parseTimeTo24(t["begin"]),parseTimeTo24(t["end"])])
        sectionDict["sectionTime"] = sectionTimes
        sectionDict["sectionDays"] = sectionDays
        result["lecture"]= lectureDict
        result["section"]= sectionDict
        results[c] = result
    return results


def fceReturn(courseWithGang):
    withnogang = courseWithGang[:2] + courseWithGang[3:]
    for i in fceData:
        if i[4] == withnogang:
            thisCourseRow = i
            break
    return {"hpw":i[9],"ot":i[17],"oc":i[18]}
