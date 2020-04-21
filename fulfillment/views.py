from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
#import csrf from CSRF protection
from django.views.decorators.csrf import csrf_exempt
#import df_library
import os
from library.df_response_lib import *
#import json to get json request
import json
from fulfillment.parameters import Actions, Intents, Events, Contexts, Scenarios
from library.responseUtility import *
from library.utility import *
import json
import random
from django.core.exceptions import PermissionDenied

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pathlib
from firebase_admin import storage
import logging
import inspect

path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
mainLogger = logging.getLogger("fulfillment")
mainLogger.setLevel(logging.INFO)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
mainLogger.addHandler(streamHandler)
fileHandler = logging.FileHandler(path + "/main.log")
fileHandler.setFormatter(formatter)
mainLogger.addHandler(fileHandler)



path = str(pathlib.Path().absolute())
# cred = credentials.Certificate(os.environ.get("FIREBASE_TOKEN"))

print(os.environ.get("FIREBASE_PRIVATE_KEY_ID"))
cred = credentials.Certificate({
      "type": "service_account",
      "project_id": "reindeer-fulfillment",
      "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID"),
      "private_key": os.environ.get("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
      "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
      "client_id": os.environ.get("FIREBASE_CLIENT_ID"),
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://oauth2.googleapis.com/token",
      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_CERT_URI")
})
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
    verifyToken = os.environ.get("FULFILLMENT_TOKEN")
    requestToken = request.headers["Fulfilllment-Token"]
    print(request.headers)
    if requestToken != verifyToken:
        raise PermissionDenied
    req = json.loads(request.body)
    mainLogger.info({"request":req})
    print("Request ------------")
    print(req)
    action = req.get('queryResult').get('action')
    contexts = req.get('queryResult').get('outputContexts')
    dialogFlowParameters = req.get("queryResult").get("parameters")

    contextList = []
    projectId = contexts[0]["name"].split("/")[1]
    session = contexts[0]["name"].split("/")[4]
    payload = req.get('originalDetectIntentRequest').get('payload')
    if "data" in payload:
        sid = payload.get('data').get('sender').get('id')
    else:
        sid = None

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
    contextList = []
    for context in contexts:
        contextName = context["name"].split("/")[-1]
        if 'lifespanCount' in context:
            count = context["lifespanCount"]
        else:
            count = 0
        addingContext = {"contextName": contextName, "count": count}
        contextList.append(addingContext)
    mainLogger.info({"contextList": contextList})
    # TODO : Suggestion Chips 로직을 참고해, User 정보를 다루는 구성을 만들자

    ffResponse = FulfillmentResponse()#그냥 놓친 action으로 인한 에러를 막기 위함.

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
        print("generalFallback 종료")
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
    if action == "choose.community":#임시임.
        ffResponse = processor.missionChooseCommunity()

    finalResponse = ffResponse.getResponse()
    print("RESPONSE-----------------")
    print(finalResponse)
    mainLogger.info({"response": finalResponse})
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
        userNew, user = checkNewAndGetUser(sid = self.sid, sourceService = "facebook")
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
        isNew, user = checkNewAndGetUser(sid=self.sid, sourceService="facebook")
        print(isNew)
        print(user)

        if isNew:
            user = makeNewUserAndGet(self.sid, sourceService="facebook", countOne = False)
            mission = getRandomMission(self.sid, getCount=1)
        else:
            mission = getRandomMission(self.sid, getCount = 1)
        print("최종 event")
        print(mission.event)
        ffResponse.addFollowupEvent(event = mission.event)
        return ffResponse

    def generalFallback(self):
        #TODO : Context가 2번 이상 유지 되지 않는 문제가 있음, Outputcontext를 추가하자
        print("generalFallback 진입")
        ffResponse = FulfillmentResponse()
        contextList  = getActionContextNames(self.contexts)

        ffResponse = fallbackScenraioFromJson(fileName="fallback", contextList= contextList)

        print(len(self.contexts))
        self.contexts = makeContextsLifespan(self.contexts, lifespanCount= 3)
        print(len(self.contexts))
        ffResponse.addContexts(contexts = self.contexts)
        print("generalFallback 종료")
        return ffResponse

    def generalSelectMission(self):
        ffResponse = FulfillmentResponse()
        isNew, user = checkNewAndGetUser(sid=self.sid, sourceService="facebook")
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
        # TODO : 그냥 뜸근없이 유입된 경우 대비 시나리오 추가

        contextList = getActionContextNames(self.contexts)
        # 임시테스트
        intent = getIntentFromContexts(self.contexts)
        print(intent)
        if intent != None:
            ffResponse = scenarioFromJson(fileName= paramScenarios.feelgood, param= intent)
        else:
            ffResponse = scenarioFromJson(fileName= paramScenarios.feelgood, param = "default")
        # self.contexts = makeContextsLifespan(self.contexts, lifespanCount=3)
        # print(ffResponse.replyList)
        #
        # if intent != None:
        #     self.contexts = addIntentToContexts(self.contexts, intent)
        # ffResponse.addContexts(self.contexts)
        # ffResponse.addButton(url = "https://www.buymeacoffee.com/reindeer",buttonText = "레인디어 후원하기")
        return ffResponse

    def generalFeelBad(self):
        # TODO : 그냥 뜸근없이 유입된 경우 대비 시나리오 추가
        intent = getIntentFromContexts(self.contexts)
        print(intent)
        mainLogger.info({"intent":intent})
        if intent != None:
            ffResponse = scenarioFromJson(fileName= paramScenarios.feelbad, param= intent)
        else:
            ffResponse = scenarioFromJson(fileName= paramScenarios.feelbad, param = "default")
        return ffResponse

    def generalFeelSoso(self):
        # TODO : 그냥 뜸근없이 유입된 경우 대비 시나리오 추가
        intent = getIntentFromContexts(self.contexts)
        print("this is intent============")
        print(intent)
        if intent != None:
            ffResponse = scenarioFromJson(fileName= paramScenarios.feelsoso, param= intent)
        else:
            ffResponse = scenarioFromJson(fileName= paramScenarios.feelsoso, param = "default")
        return ffResponse

    def missionFeedback(self):
        #TODO : Action과 parameter가 들어오면 Firebase를 호출해서, 적한 로직으로 답을 준다.
        ffResponse = FulfillmentResponse()
        intent = None
        mission = None
        user = None
        intentCount = None
        intent = getIntentFromContexts(self.contexts)
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
        intentCount +=1
        ffResponse = missionFeedbackSenarioFromJson(fileName="missionFeedback", intent = intent, intentCount = intentCount)
        print("intent : {}, mission:{}, user:{}, intentCount : {}".format(intent, mission, user, intentCount))
        user.totalCount += 1
        if intentCount == 1:
            user.intent[intent] = 1
        elif intentCount == None:
            ffResponse.addTextReply("좋았어")
        else:
            user.intent[intent] += 1
        if mission.useStamp == True:
            #TODO : FirebaseStorage TO CDN(보안)
            ffResponse.addImageReply(url = mission.stampUrl)
        # notDonate, donationText = getDonationText()

        return ffResponse
    def missionChooseCommunity(self):
        param = None
        if self.params:
            if u"taget-commuinity-them" in self.params:
                param = self.params[u"taget-commuinity-them"]
            else:
                param = "nothing"
        else:
            param = "nothing"

        ffResponse = scenarioFromJson(fileName = "chooseCommunity", param =  param)
        ffResponse.addTextReply("그럼 오늘은 신청이나 등록 같은거 까지만 해보자")
        ffResponse.addFacebookQuickReply(title = "한번에 나가는 건 큰 결심이지만, 등록 같은건 금방 해볼 수 있자나",quickReplyList=["그러자"])
        return ffResponse