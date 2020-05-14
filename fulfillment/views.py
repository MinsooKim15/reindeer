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
from library.agent import *

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
      "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
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
    agent = Agent(request)

    # 로직 변경을 위한 임시 주석처리

    # req = json.loads(request.body)
    # mainLogger.info({"request":req})
    # print("Request ------------")
    # print(req)
    # action = req.get('queryResult').get('action')
    # inputContexts = req.get('queryResult').get('outputContexts')
    # contexts = []
    # for inputContext in inputContexts:
    #     context = Context.fromDict(inputContext)
    #     contexts.append(context)
    # #Dialoflow Request를 소화하는 로직이 하나 있어야 할듯
    # #Context를 객체화 시켜서 저장합니다.
    #
    # dialogFlowParameters = req.get("queryResult").get("parameters")
    #
    # contextList = []
    # projectId = contexts[0].projectId
    # session = contexts[0].session
    # payload = req.get('originalDetectIntentRequest').get('payload')
    # if "data" in payload:
    #     sid = payload.get('data').get('sender').get('id')
    # else:
    #     sid = None

    processor = Processor(
        action= agent.action,
        contexts= agent.contexts,
        params= agent.params,
        projectId = agent.projectId,
        session= agent.session,
        sid = agent.sid,
        intent = agent.getIntent(),
        agent = agent
    )

    #TODO :로깅 로직 수정
    contextList = []
    for context in processor.contexts:
        contextName = context.contextName
        count = context.lifeSpan
        addingContext = {"contextName": contextName, "count": count}
        contextList.append(addingContext)
    mainLogger.info({"contextList": contextList})
    #여기까지가 로깅 로직

    ffResponse = FulfillmentResponse()#그냥 놓친 action으로 인한 에러를 막기 위함.

    # General Intent들
    if agent.action == paramActions.welcome:
        ffResponse = processor.generalWelcome()
    if agent.action == paramActions.tutorialFeedback:
        ffResponse = processor.generalTutorialFeedback()
    if agent.action == paramActions.newMission:
        ffResponse = processor.generalNewMission()
    if agent.action == paramActions.selectMission:
        ffResponse = processor.generalSelectMission()
    if agent.action == paramActions.fallback:
        ffResponse = processor.generalFallback()
    if agent.action == paramActions.later:
        ffResponse = processor.later()

    # General 소감 표현을 처음 받았을 때의 처리
    if agent.action == paramActions.feelGood:
        ffResponse = processor.generalFeelGood()
    if agent.action == paramActions.feelBad:
        ffResponse = processor.generalFeelBad()
    if agent.action == paramActions.feelSoso:
        ffResponse = processor.generalFeelSoso()
    if agent.action == paramActions.missiondoodleGiveImage:
        ffResponse = processor.missionDoodleGiveImage()
    if agent.action == paramActions.missionStart:
        ffResponse = processor.missionStart()
    if agent.action == paramActions.generalMissionDone:
        ffResponse = processor.generalMissionDone()

    # 미션이 종료하고 최종 피드백을 한다. Param에 들어있는 Intent를 Firebase로 날려 처리한다.
    if agent.action == paramActions.missionFeedback:
       ffResponse = processor.missionFeedback()
    if agent.action == "choose.community":#임시임.
        ffResponse = processor.missionChooseCommunity()

    if agent.action == paramActions.emotionGood:
        ffResponse = processor.emotionGood()
    if agent.action == paramActions.emotionBad:
        ffResponse = processor.emotionBad()
    if agent.action == paramActions.emotionNeutral:
        ffResponse = processor.emotionNeutral()
    # ffResponse.addContexts(agent.contexts)
    finalResponse = ffResponse.getResponse()
    mainLogger.info({"response": finalResponse})
    return JsonResponse(finalResponse, safe = False)

class Processor():
    def __init__(self, action, contexts, params, projectId, session, sid, intent, agent):
        self.action = action
        self.contexts = contexts
        self.params = params
        self.projectId  = projectId
        self.session = session
        self.sid = sid
        self.intent = intent
        self.agent = agent

    def generalWelcome(self):
        userNew, user = checkNewAndGetUser(sid = self.sid, sourceService = "facebook")
        ffResponse = FulfillmentResponse()
        if (userNew):
            ffResponse.addFollowupEvent(event = paramEvents.tutorial)
            user = makeNewUserAndGet(self.sid, "facebook", countOne= False)
        elif (user.totalCount ==0):
            ffResponse.addFollowupEvent(event = paramEvents.tutorial)
        else:
            ffResponse.addTextReply(text="기억해 엄청 단순해 보이지만, 특별한 힘이 있다는거!")

            ffResponse.addFacebookQuickReply(
                title = "새로운 미션을 원하면 언제든 '시작하기'라고 말해줘".format(user.firstName),
                quickReplyList= ["시작하기"]
            )
        return ffResponse

    def generalTutorialFeedback(self):
        ffResponse = FulfillmentResponse()
        # TODO : 스탬프를 돌려준다.
        fbQuery = FirebaseQuery()
        user = fbQuery.get_user(id = self.sid, sourceService="facebook")
        stamp = fbQuery.get_stamp(stampName = "achieve.1")
        ffResponse.addImageReply(url= stamp.imgUrl)
        ffResponse.addTextReply(text= stamp.prompt)
        mission = fbQuery.get_mission_by_intent(intent = "mission.tutorial")
        user.missionDone(mission = mission)
        fbQuery.set_user(user = user)
        ffResponse.addTextReply(text = "이제 새로운 미션을 하고 싶을 땐 언제든 '시작하기'라고 말해줘")
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
        # contextList  = getActionContextNames(self.contexts)
        # for context in self.contexts:
        ffResponse = fallbackScenraioFromJson(fileName="fallback", contextList= self.contexts)

        print(len(self.contexts))
        for context in self.contexts:
            context.extandIntentLifeSpan(lifespanCount=3)
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
        for mission in missionList:
            if mission.intent == self.intent:
                missionList.remove(mission)
        for mission in missionList:
            replyList.append(mission.phrase)
        replyList = replyList[0:2]
        ffResponse.addFacebookQuickReply(title= "으음ㅜ 재밌을텐데 아쉽다. 그럼 이런건 어때",quickReplyList=replyList)
        return ffResponse

    def generalFeelGood(self):
        # TODO : 그냥 뜸근없이 유입된 경우 대비 시나리오 추가

        # 임시테스트
        # intent = getIntentFromContexts(self.contexts)

        if self.intent != None:
            ffResponse = scenarioFromJson(fileName= paramScenarios.feelgood, param= self.intent)
        else:
            ffResponse = scenarioFromJson(fileName= paramScenarios.feelgood, param = "default")
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
        # if "intent" in self.params:
        #     intent = self.params["intent"]
        # else:
        #     intent = getIntentFromContexts(self.contexts)
        if self.intent != None:
            print("intent는 NONE이 아님")
            fbQuery = FirebaseQuery()

            mission = fbQuery.get_mission_by_intent(self.intent)
            user = fbQuery.get_user(self.sid, sourceService="facebook")
        mainLogger.info({"user": user, "intent" : self.intent, "mission" : mission})
        if (mission != None) & (user != None):
            if self.intent in user.intent:
                intentCount = user.intent[self.intent]
            else:
                intentCount = 0
        intentCount += 1
        mainLogger.info({"intentCount": intentCount})
        user.missionDone(mission)
        #만약 달성하지 못했으면 None
        achieveStamp = getStampIfExist(user=user, latestMission= mission)
        if achieveStamp != None:
            ffResponse.addImageReply(url = achieveStamp.imgUrl)
            ffResponse.addTextReply(text = achieveStamp.prompt)
        else:
            ffResponse = missionFeedbackSenarioFromJson(fileName="missionFeedback", intent = self.intent, intentCount = intentCount)
        print("intent : {}, mission:{}, user:{}, intentCount : {}".format(self.intent, mission, user, intentCount))

        if intentCount == None:
            ffResponse.addTextReply("좋았어")

        if mission.useStamp == True:
            #TODO : FirebaseStorage TO CDN(보안)
            ffResponse.addImageReply(url = mission.stampUrl)
        mainLogger.info({"user": user})
        mainLogger.info({"reply": ffResponse.replyList})
        fbQuery.set_user(user=user)
        # notDonate, donationText = getDonationText()
        return ffResponse
    def missionStart(self):
        ffResponse = FulfillmentResponse()
        fbQuery = FirebaseQuery()
        user = fbQuery.get_user(self.sid, sourceService="facebook")
        user.missionStart(self.intent)
        # TODO : 시작 시나리오를 Json으로 가져오기(답변 속도 향상을 위함)
        fbQuery.set_user(user)
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
    def missionDoodleGiveImage(self):
        ffResponse = FulfillmentResponse()
        ffResponse.addTextReply("좋아 이번엔 나부터 보여줄게")
        url = "https://firebasestorage.googleapis.com/v0/b/reindeer-fulfillment.appspot.com/o/doodle.png?alt=media&token=a1612433-3169-44f4-8896-fb0adac5ac6f"
        ffResponse.addImageReply(url = url)
        ffResponse.addTextReply("짜잔...! 영험한 나를 그린 거야")
        ffResponse.addTextReply("커피와 당근을 아주 좋아하지")
        ffResponse.addTextReply("ㅎㅎ ㅜ 부끄럽다 이제 얼마나 대충 그려도 될지 알겠지?")
        ffResponse.addTextReply("다 그리면 보내줘ㅎ 기다릴게")
        notUsingresponse = self.missionStart()
        return ffResponse
    def generalMissionDone(self):
        fbQuery = FirebaseQuery()
        user = fbQuery.get_user(self.sid,sourceService="facebook")
        ffResponse = FulfillmentResponse()
        #하던 미션이 있으면, 해당 미션 이어서 진행할 수 있도록 doneEvent를 날린다.
        if user.doingMission != None:
            mission = fbQuery.get_mission_by_intent(user.doingMission)
            ffResponse.addFollowupEvent(event = mission.doneEvent)
            #TODO : Context를 같이 보내주면 event가 먹네요. 데이터 구조에 doneContext도 추가해야 할듯 ㅜ
            #lifespan을 2 이상으로 두면 fallback이 context를 물어서 난리 버거지가 난다
            context = Context(projectId = self.projectId, session = self.session, lifeSpan = 1, parameters = {}, contextName= mission.doneContext)
            ffResponse.addContexts([context])
        else:
        # 하던 미션이 없으면, fallback 처리한다.
            ffResponse.addTextReply(text = "음 잘 모르겠어")
        return ffResponse
    def emotionGood(self):
        #TODO : 좋은 emotion은 그냥 smallTalk처리
        ffResponse = FulfillmentResponse()
        return ffResponse


    def emotionBad(self):
        ffResponse = FulfillmentResponse()
        missions = getRandomMission(self.sid, getCount= 3, sourceService= "facebook")
        ffResponse.addTextReply(text = "에고, 그렇구나.. 그럴 때는 가볍게 기분이 풀릴만한 것들을 해보는 것도 괜찮아")

        quickReplyList = []
        for mission in missions:
            quickReplyList.append(mission.phrase)
        quickReplyList.append("그만할래")
        ffResponse.addFacebookQuickReply(title="이런건 어때?", quickReplyList=quickReplyList)
        self.agent.clearAllContext()
        ffResponse.addContexts(self.agent.contexts)
        return ffResponse

    def emotionNeutral(self):
        ffResponse = FulfillmentResponse()
        missions = getRandomMission(self.sid, getCount= 3, sourceService= "facebook")
        ffResponse.addTextReply(text = "그럴 땐 나랑 노는 거 어때?")

        quickReplyList = []
        for mission in missions:
            quickReplyList.append(mission.phrase)
        quickReplyList.append("그만할래")
        ffResponse.addFacebookQuickReply(title="새로운 미션들을 해보자", quickReplyList=quickReplyList)
        return ffResponse

