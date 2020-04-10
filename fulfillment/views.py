from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
#import csrf from CSRF protection
from django.views.decorators.csrf import csrf_exempt
#import df_library
from library.df_response_lib import *
#import json to get json request
import json
import requests
from fulfillment.parameters import Actions, Intents, Events, Contexts, Scenarios
from library.responseUtility import *
from library.utility import *
import json
import random

paramEvents = Events()
paramActions = Actions()
paramIntents = Intents()
paramContexts = Contexts()
paramScenrios = Scenarios()
# Create your views here.
def home(request):
    return HttpResponse("Hello World!")

@csrf_exempt
def webhook(request):
    # Build a request object
    # print()

    req = json.loads(request.body)
    print(req)
    action = req.get('queryResult').get('action')
    contexts = req.get('queryResult').get('outputContexts')
    dialogFlowParameters = req.get("queryResult").get("parameters")
    processor = Processor(action = action, contexts = contexts, params = dialogFlowParameters, scenarios= paramScenrios)
    print("유입")
    contextList = []
    for context in contexts:
        contextName = context["name"].split("/")[-1]
        contextList.append(contextName)
    print(contextList)
    print("!!!!!!!!")
    ffResponse = FulfillmentResponse()

    # TODO : Suggestion Chips 로직을 참고해, User 정보를 다루는 구성을 만들자

    if action == "get_suggestion_chips":

        contexts = req.get('queryResult').get('outputContexts')
        session = req.get('session')
        sid = req.get('originalDetectIntentRequest').get('payload').get('data').get('sender').get('id')
        page_access_token = "EAAJH9hLZCkRwBAC0OrxNxl97pah1Rq6a7gW9ZCN6uS9KQRGjBZA3al1hw2EaDppGWApgbjW0Xfh5WOUSw9sujZBCEVhxFCHcF85hUMh1BYyAiHNSIc76HsCZA0G0oQdQUusZBPbzgXkqkYWRCMjCi1cIqD72jh4ettysnORZBW1NDuZA60lCD0KMhpr9FsyEVU0ZD"
        URL = "https://graph.facebook.com/" + sid + "?fields=first_name,last_name,profile_pic&access_token=" + page_access_token
        response_fb = requests.get(URL)
        response_fb.json()
        print(response_fb.json())
        firstName = response_fb.json()["first_name"]
        lastName = response_fb.json()["last_name"]
        # print(original)
        session = session.split("/")[-1]
        print(contexts)
        print(session)

        contexts[0]["parameters"]["hey"] = firstName
        # for context in contexts:
        #     print(context[0])
        #     print("-----------")
        fr = fulfillment_response()
        # output_contexts_new = fr.output_contexts(session, contexts)
        output_contexts = {
            "output_contexts": contexts
        }
        # set fulfillment text
        fulfillmentText = firstName + "님, 안녕하세요!"
        aog = actions_on_google_response()
        aog_sr = aog.simple_response([
            [fulfillmentText,fulfillmentText, False]
        ])
        #create suggestiong chips
        # aog_sc = aog.suggestion_chips(["suggestion1", "suggestion2"])
        ff_response = fulfillment_response()
        ff_text = ff_response.fulfillment_text(fulfillmentText)
        # ff_messages = ff_response.fulfillment_messages([aog_sr, aog_sc])
        reply = ff_response.main_response(ff_text, output_contexts = output_contexts)
    print(action)
    # General Intent들
    if action == paramActions.welcome:
        ffResponse = processor.generalWelcome()
    if action == paramActions.tutorialFeedback:
        ffResponse = processor.generalTutorialFeedback()
    if action == paramActions.newMission:
        ffResponse = processor.generalNewMission()
    if action == paramActions.selectMission:
        ffResponse = processor.generalSelectMission()
    if action == paramActions.fallback:
        ffResponse = processor.generalFallback()
    if action == paramActions.later:
        ffResponse = processor.later()

    # General 소감 표현을 처음 받았을 때의 처리
    if action == paramActions.feelGood:
        ffResponse = processor.generalFeelGood()
    if action == paramActions.feelBad:
        ffResponse = processor.generalFeelBad()
    if action == paramActions.feelSoso:
        ffResponse = processor.generalFeelSoso()


    # 미션이 종료하고 최종 피드백을 한다. Param에 들어있는 Intent를 Firebase로 날려 처리한다.
    if action == paramActions.missionFeedback:
       ffResponse = processor.missionFeedback()


    finalResponse = ffResponse.getResponse()
    print(finalResponse)
    return JsonResponse(finalResponse, safe = False)

class Processor():
    def __init__(self, action, contexts, params, scenarios):
        self.action = action
        self.contexts = contexts
        self.params = params
        self.scenarios = scenarios
    def generalWelcome(self):
        # TODO : 사용자 체크, 처음이면 Tutorial Event, 본 적있으면 끝낸다.
        ffResponse = FulfillmentResponse()
        # TODO : 스탬프를 돌려준다.
        return ffResponse


    def generalTutorialFeedback(self):
        ffResponse = FulfillmentResponse()
        # TODO : 스탬프를 돌려준다.
        return ffResponse

    def later(self):
        ffResponse = FulfillmentResponse()
        ffResponse.addFollowupEvent(event=paramEvents.selectMission)
        return ffResponse

    def generalNewMission(self):
        ffResponse = FulfillmentResponse()
        # TODO : Firebase 호출해, Random하게 1개의 Mission을 Event로 돌려준다.
        return ffResponse

    def generalFallback(self):
        #TODO : Context가 2번 이상 유지 되지 않는 문제가 있음, Outputcontext를 추가하자
        ffResponse = FulfillmentResponse()
        with open('./scenario/fallback.json') as json_file:
            fallbackScenario = json.load(json_file)
        contextList  = getActionContextNames(self.contexts)
        if len(contextList) >= 1:
            ffResponse = scenarioFromJson(fileName = "fallback", param = contextList[0])
        else:
            ffResponse = scenarioFromJson(fileName = "fallback", param = "default")
        return ffResponse

    def generalSelectMission(self):
        ffResponse = FulfillmentResponse()
        ffResponse.addTextReply("selectMission")
        #TODO : Firebase 호출해, Random학게 3개의 미션을 뽑아서 Quick Reply로 돌려준다.
        return ffResponse

    def generalFeelGood(self):
        contextList = getActionContextNames(self.contexts)
        if len(contextList) >= 1:
            ffResponse = scenarioFromJson(fileName= self.scenarios.feelgood, param=contextList[0])
        else:
            ffResponse = scenarioFromJson(fileName= self.scenarios.feelgood, param = "default")
        return ffResponse

    def generalFeelBad(self):
        contextList = getActionContextNames(self.contexts)
        if len(contextList) >= 1:
            ffResponse = scenarioFromJson(fileName= self.scenarios.feelbad, param=contextList[0])
        else:
            ffResponse = scenarioFromJson(fileName= self.scenarios.feelbad, param = "default")
        return ffResponse

    def generalFeelSoso(self):
        contextList = getActionContextNames(self.contexts)
        if len(contextList) >= 1:
            ffResponse = scenarioFromJson(fileName= self.scenarios.feelsoso, param=contextList[0])
        else:
            ffResponse = scenarioFromJson(fileName= self.scenarios.feelsoso, param = "default")
        return ffResponse

    def missionFeedback(self):
        #TODO : Action과 parameter가 들어오면 Firebase를 호출해서, 적한 로직으로 답을 준다.
        ffResponse = FulfillmentResponse()
        return ffResponse