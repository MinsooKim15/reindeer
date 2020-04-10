import json
from library.responseUtility import *
import random

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