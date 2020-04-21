import json
from library.responseUtility import *
import random
import requests
from fulfillment.querys import *
from fulfillment.models import *
import random
import os


def checkContext(target, contexts):
    contextList = []
    for context in contexts:
        contextName = context["name"].split("/")[-1]
        contextList.append(contextName)
    if target in contextList:
        return True
    else:
        return False
def getActionContextNames(contexts):
    contextList = []
    for context in contexts:
        contextName = context["name"].split("/")[-1]
        if (contextName != "generic") & (contextName != "__system_counters__"):
            contextList.append(contextName)
    return contextList

def fallbackScenraioFromJson(fileName,contextList):
    with open('./scenario/'+fileName + ".json") as json_file:
        jsonScenario = json.load(json_file)
    keys = jsonScenario.keys()
    selectedKey = None
    if len(contextList) >=1:
        for key in keys:
            if selectedKey != None:
                break
            for context in contextList:
                if key == context:
                    selectedKey = key
                    break
    if selectedKey != None:
        scenario = jsonScenario[selectedKey]
    else:
        scenario = jsonScenario["default"]
    ffResponse = scenarioToResponse(scenario)
    return ffResponse
# def getRecentContexts(contexts):
#     selectedContext = None
#     if len(contexts) >=1:
#         for context in contexts:
#             #변수 설정
#             contextName = context["name"].split("/")[-1]
#             lifeSpanCount = None
#             if 'lifespanCount' in context:
#                 lifeSpanCount = context["lifespanCount"]
#             lifeSpanChanged = False
#             if 'parameters' in context:
#                 if u"lifeSpanChanged" in context[u"parameters"]:
#                     lifeSpanChanged = True
#
#             if (contextName != "generic") & (contextName != "__system_counters__"):
#                 pass
#             if lifeSpanChanged:
#                 pass
#             if selectedContext == None:
#                 selectedContext = {"names": [contextName], "count": lifeSpanCount}
#             else:
#                 if lifeSpanCount == selectedContext["count"]:
#                     selectedContext["names"].append(contextName)
#                 elif lifeSpanCount > selectedContext["count"]:
#                     selectedContext = {"names": [contextName], "count": lifeSpanCount}
#
#     if selectedContext!=None:
#         return selectedContext["names"]
#     else:
#         return None




def scenarioFromJson(fileName,param):
    with open('./scenario/'+fileName + ".json") as json_file:
        jsonScenario = json.load(json_file)
    if param in jsonScenario.keys():
        scenario = jsonScenario[param]
        ffResponse = scenarioToResponse(scenario)
    else:
        scenario = jsonScenario["default"]
        ffResponse = scenarioToResponse(scenario)
    return ffResponse
def missionFeedbackSenarioFromJson(fileName, intent, intentCount):
    with open('./scenario/'+fileName + ".json") as json_file:
        jsonScenario = json.load(json_file)
    intentCount = str(intentCount)
    ffResponse = FulfillmentResponse()
    if intent in jsonScenario.keys():
        if intentCount in jsonScenario[intent]:
            scenario = jsonScenario[intent][intentCount]
        else:
            scenario = jsonScenario[intent]["n"]
        ffResponse.addTextReply(text = scenario.format(intentCount))
    else:
        if intentCount in jsonScenario["default"]:
            scenario = jsonScenario["default"][intentCount]
        else:
            scenario = jsonScenario["default"]["n"]
        ffResponse.addTextReply(text = scenario.format(intentCount))
    print(ffResponse.getResponse())
    return ffResponse


def scenarioToResponse(scenario):
    ffResponse = FulfillmentResponse()
    if scenario["type"] == "randomText":
        prompt = random.choice(scenario["textList"])
        ffResponse.addTextReply(prompt)
    elif scenario["type"] == "text":
        prompt = scenario["text"]
        ffResponse.addTextReply(prompt)
    elif scenario["type"] == "quickReplies":
        ffResponse.addFacebookQuickReply(title=scenario["text"], quickReplyList= scenario["replies"])
    else:
        raise ValueError
    return ffResponse

def getFBUserData(sid):
    page_access_token = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN")
    URL = "https://graph.facebook.com/" + sid + "?fields=first_name,last_name,profile_pic&access_token=" + page_access_token
    response_fb = requests.get(URL)
    resFbJson= response_fb.json()
    result = "a"
    if u"error" in resFbJson:
        # 에러면 None을 반환
        result = None
    else:
        firstName = resFbJson["first_name"]
        lastName = resFbJson["last_name"]
        facebookId = resFbJson["id"]
        profilePic = resFbJson["profile_pic"]
        result = {
            "firstName" : firstName,
            "lastName" : lastName,
            "facebookId" : facebookId,
            "profilePic" : profilePic
        }
    return result

def checkNewAndGetUser(sid,sourceService):
    fbQuery = FirebaseQuery()
    user = fbQuery.get_user(sid,sourceService)
    print("checkNewAndGetUser쿼리후,", user)
    if user is None:
        return (True, user)
    else:
        return (False,user)

def makeNewUserAndGet(sid,sourceService,countOne = True, intent=None, stamp = None):
    if countOne :
        totalCount = 1
    else:
        totalCount = 0
    if intent == None:
        intentDict = {}
    else:
        intentDict = {
            intent : 1
        }
    if stamp == None:
        stampList = []
    else:
        stampList = [stamp]
    if sourceService == "facebook":
        userData = getFBUserData(sid)
        if userData is not None:
            user = User(
                firstName=userData["firstName"],
                lastName=userData["lastName"],
                serviceId = userData["facebookId"],
                sourceService=sourceService,
                totalCount = totalCount,
                intent = intentDict,
                stamp = stampList
            )
        else:
            #FacebookGraph API 에러 상황
            user = User(
                serviceId = sid,
                sourceService = sourceService,
                totalCount = totalCount,
                intent = intentDict,
                stamp = stampList
            )
    fbQuery = FirebaseQuery()
    fbQuery.set_user(user)
    print(user)
    return user

def getRandomIntent(sid):
    fbQuery = FirebaseQuery()
    user = fbQuery

def getRandomMission(sid,getCount = 1,sourceService = "facebook"):
    fbQuery = FirebaseQuery()
    user = fbQuery.get_user(sid,sourceService=sourceService)
    missions = fbQuery.get_mission_list()
    finalMissionList = []
    print(missions)
    print(user)
    for mission in missions:
        print(mission)
        if u"totalCount" in mission.condition:
            print("카운ㅌ트 있음!!!!!!!!!")
            print(mission.condition)
            if user.totalCount >= mission.condition[u"totalCount"]:
                finalMissionList.append(mission)
        else:
            print("무조건 포함(totalCount 조건 없음)")
            finalMissionList.append(mission)

    random.shuffle(finalMissionList)
    print(finalMissionList)
    if getCount == 1:
        return finalMissionList[0]
    else:
        return finalMissionList[0:getCount]

def getDonationText(ffResponse):
    with open('./scenario/donation' + ".json") as json_file:
        jsonScenario = json.load(json_file)
    randomList = []

    for key,value in jsonScenario.values():
        randomList += [key]*value["weight"]
    randomKey = random.choice(randomList)
    # if randomKey["type"] == "text":
    #
def getIntentFromContexts(contexts):
    intent = None
    for context in contexts:
        print(context)
        if "parameters" in context:
            if "intent" in context["parameters"]:
                intent = context["parameters"]["intent"]
    return intent


