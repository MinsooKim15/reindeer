from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
#import csrf from CSRF protection
from django.views.decorators.csrf import csrf_exempt
#import df_library
from library.df_response_lib import *
#import json to get json request
import json
from fulfillment.parameters import Actions, Intents, Events, Contexts, Scenarios
from library.responseUtility import *
from library.utility import *
import json
import random

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pathlib
path = str(pathlib.Path().absolute())
cred = credentials.Certificate(path + '/environment/reindeer-fulfillment-firebase-adminsdk-cwcle-f6101f3cf3.json')
default_app = firebase_admin.initialize_app(cred)


paramEvents = Events()
paramActions = Actions()
paramIntents = Intents()
paramContexts = Contexts()
paramScenarios = Scenarios()
# Create your views here.
def home(request):
    return HttpResponse("Hello World!")

@csrf_exempt
def webhook(request):
    isNew = False
    req = json.loads(request.body)
    print("Request ------------")
    print(req)
    action = req.get('queryResult').get('action')
    contexts = req.get('queryResult').get('outputContexts')
    dialogFlowParameters = req.get("queryResult").get("parameters")

    contextList = []
    projectId = contexts[0]["name"].split("/")[1]
    session = contexts[0]["name"].split("/")[4]
    sid = req.get('originalDetectIntentRequest').get('payload').get('data').get('sender').get('id')

    # projectData = {
    #     "projectId" : projectId,
    #     ""
    # }
    processor = Processor(
        action=action,
        contexts=contexts,
        params=dialogFlowParameters,
        projectId = projectId,
        session=session,
        sid = sid,
    )

    # TODO : Suggestion Chips 로직을 참고해, User 정보를 다루는 구성을 만들자

    if action == "get_suggestion_chips":

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
    print("RESPONSE-----------------")
    print(finalResponse)
    return JsonResponse(finalResponse, safe = False)

class Processor():
    def __init__(self, action, contexts, params, projectId, session, sid):
        self.action = action
        self.contexts = contexts
        self.params = params
        self.projectId  = projectId
        self.session = session
        self.sid = sid
    def generalWelcome(self):
        userNew, user = checkNewAndGetUser(sid = self.sid,sourceService = "facebook")
        ffResponse = FulfillmentResponse()
        if userNew:
            ffResponse.addFollowupEvent(event = paramEvents.tutorial)
        else:
            ffResponse.addFacebookQuickReply(
                title = "다시 보니 반가워 {} 미션을 시작할 때는 언제든 시작하기라고 말해줘".format(user.firstName),
                quickReplyList= ["시작하기"]
            )
        return ffResponse


    def generalTutorialFeedback(self):
        ffResponse = FulfillmentResponse()
        # TODO : 스탬프를 돌려준다.
        user = makeNewUserAndGet(self.sid,"facebook")
        ffResponse.addTextReply("잘했어,{}".format(user.firstName))
        return ffResponse

    def later(self):
        ffResponse = FulfillmentResponse()
        ffResponse.addFollowupEvent(event=paramEvents.selectMission)
        return ffResponse

    def generalNewMission(self):
        ffResponse = FulfillmentResponse()
        # TODO : Firebase 호출해, Random하게 1개의 Mission을 Event로 돌려준다.
        isNew, user = checkNewAndGetUser()
        if isNew:
            user = makeNewUserAndGet(self.sid, sourceService="facebook", countOne = False)
        mission = getRandomMission(self.sid, getCount = 1)
        print("최종 event")
        print(mission.event)
        ffResponse.addFollowupEvent(event = mission.event)
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
        self.contexts = makeContextsLifespan(self.contexts, lifespanCount= 3)
        ffResponse.addContexts(contexts = self.contexts)
        return ffResponse

    def generalSelectMission(self):
        ffResponse = FulfillmentResponse()
        isNew, user = checkNewAndGetUser()
        if isNew:
            user = makeNewUserAndGet(self.sid, sourceService="facebook", countOne = False)
        missionList = getRandomMission(self.sid, getCount = 3)
        replyList = []
        if u"intent" in self.params:
            for mission in missionList:
                if mission.intent == self.params[u"intent"]:
                    missionList.remove(mission)
        for mission in missionList:
            replyList.append(mission.phrase)
        replyList = replyList[0:2]
        ffResponse.addFacebookQuickReply(title= "그럼 이런건 어때",quickReplyList=replyList)
        return ffResponse

    def generalFeelGood(self):
        # TODO: 기분 측정시 전달 받은 Context리스트를 그대로 밀어 넣자

        contextList = getActionContextNames(self.contexts)
        # 임시테스트
        if len(contextList) >= 1:
            ffResponse = scenarioFromJson(fileName= paramScenarios.feelgood, param=contextList[0])
        else:
            ffResponse = scenarioFromJson(fileName= paramScenarios.feelgood, param = "default")
        self.contexts = makeContextsLifespan(self.contexts, lifespanCount=3)
        intent = None
        for param in self.params:
            if "intent" in param:
                intent = param["intent"]
        if intent != None:
            self.contexts = addIntentToContexts(self.contexts, intent)
        ffResponse.addContexts(self.contexts)
        return ffResponse

    def generalFeelBad(self):
        # contextList = getActionContextNames(self.contexts)
        # if len(contextList) >= 1:
        #     ffResponse = scenarioFromJson(fileName=  paramScenarios.feelbad, param=contextList[0])
        # else:
        #     ffResponse = scenarioFromJson(fileName=  paramScenarios.feelbad, param = "default")
        ffResponse = FulfillmentResponse()
        ffResponse.addImage("https://firebasestorage.googleapis.com/v0/b/reindeer-fulfillment.appspot.com/o/%E1%84%8F%E1%85%A1%E1%84%86%E1%85%A6%E1%84%85%E1%85%A1%E1%84%85%E1%85%B3%E1%86%AF%E1%84%86%E1%85%A5%E1%86%B7%E1%84%8E%E1%85%AE%E1%84%86%E1%85%A7%E1%86%AB%E1%84%8B%E1%85%A1%E1%86%AB%E1%84%83%E1%85%AB_8.png?alt=media&token=7cf24584-7ecc-434a-91d7-8c99fd7d1e18")
        return ffResponse

    def generalFeelSoso(self):
        contextList = getActionContextNames(self.contexts)
        if len(contextList) >= 1:
            ffResponse = scenarioFromJson(fileName=  paramScenarios.feelsoso, param=contextList[0])
        else:
            ffResponse = scenarioFromJson(fileName=  paramScenarios.feelsoso, param = "default")
        return ffResponse

    def missionFeedback(self):
        #TODO : Action과 parameter가 들어오면 Firebase를 호출해서, 적한 로직으로 답을 준다.
        ffResponse = FulfillmentResponse()
        intent = None
        mission = None
        user = None
        intentCount = None
        for context in self.contexts:
            print("------")
            print(context)
            if u"intent" in context[u"parameters"]:
                print("param 있네")
                intent = context[u"parameters"][u"intent"]
        if intent != None:
            print("intent는 NONE이 아님")
            fbQuery = FirebaseQuery()
            mission = fbQuery.get_mission_by_intent(intent)
            user = fbQuery.get_user(self.sid,sourceService="facebook")
        if (mission != None) & (user != None):
            if intent in user.intent:
                intentCount = user.intent[intent]
            else:
                intentCount = 0
        ffResponse = missionFeedbackSenarioFromJson(fileName="missionFeedback", intent = intent, intentCount = intentCount)
        user.totalCount += 1
        print("intent : {}, mission:{}, user:{}, intentCount : {}".format(intent, mission, user, intentCount))
        if intentCount == 0:
            user.intent[intent] = 0
        elif intentCount == None:
            ffResponse.addTextReply("뭔가 이ㅇㅏㄴㅣ")
        else:
            user.intent[intent] += 1
        # fbQuery.set_user(user)
        #TODO : 이래 두 개 조건은 뒤집으면 에러가 난다. 모든 상황에서 쓸 수 있도록 개선
        # ffResponse.addImage(url ="https://firebasestorage.googleapis.com/v0/b/reindeer-fulfillment.appspot.com/o/%E1%84%8F%E1%85%A1%E1%84%86%E1%85%A6%E1%84%85%E1%85%A1%E1%84%85%E1%85%B3%E1%86%AF%E1%84%86%E1%85%A5%E1%86%B7%E1%84%8E%E1%85%AE%E1%84%86%E1%85%A7%E1%86%AB%E1%84%8B%E1%85%A1%E1%86%AB%E1%84%83%E1%85%AB_8.png?alt=media&token=7cf24584-7ecc-434a-91d7-8c99fd7d1e18")
        ffResponse.dumpResponse()
        # if mission.useStamp == True:
        return ffResponse