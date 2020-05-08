from django.db import models
from datetime import datetime

# Create your models here.
class User(object):
    def __init__(self,serviceId, sourceService = "facebook", totalCount=0,firstName="", lastName="",  intent={}, stamp=[],emotionTypeCount = {}, doingMission = None,latestMission = None ):
        #firstName, lastName 비워질 수 있게 변경

        if len(firstName) > 0 :
            self.firstName = firstName
        if len(lastName) > 0 :
            self.lastName = lastName
        self.serviceId = serviceId
        self.totalCount = totalCount
        self.sourceService = sourceService
        self.intent = intent
        self.stamp = stamp
        self.emotionTypeCount = emotionTypeCount
        self.doingMission = doingMission
        self.latestMission = latestMission

        if self.sourceService == "facebook":
            self.id = u"fb_" + serviceId
        else:
            self.id = u"df_" + serviceId


    @staticmethod
    def from_dict(source):
        user = User(source[u"serviceId"])

        if u"firstName" in source:
            user.firstName = source[u"firstName"]

        if u"lastName" in source:
            user.lastName = source[u"lastName"]

        if u"sourceService" in source:
            user.sourceService = source[u"sourceService"]
        else:
            user.sourceService = "facebook"

        if u"totalCount" in source:
            user.totalCount = source[u"totalCount"]
        if u"intent" in source:
            user.intent = source[u"intent"]
        else:
            user.intent = {}
        if u"stamp" in source:
            user.stamp = source[u"stamp"]
        else:
            user.stamp = []
        if u"emotionTypeCount" in source:
            user.emotionTypeCount = source[u"emotionTypeCount"]
        else:
            user.emotionTypeCount = {
                "calm" : 0,
                "confident" : 0
            }
        if u"doingMission" in source:
            user.doingMission = source[u"doingMission"]
        else:
            user.doingMission = None
        if u"latestMission" in source:
            user.latestMission = source[u"latestMission"]
        else:
            user.latestMission = None

        return user

    def to_dict(self):
        dest = {
            u"serviceId" : self.serviceId,
            u"sourceService" : self.sourceService,
            u"totalCount" : self.totalCount,
            u"intent" : self.intent,
            u"stamp": self.stamp,
            u"emotionTypeCount" : self.emotionTypeCount,
            u"updated" : datetime.now(),
            u"latestMission" : self.latestMission,
            u"doingMission" : self.doingMission
        }
        if self.firstName:
           dest[u'firstName'] = self.firstName
        if self.lastName:
            dest[u"lastName"] = self.lastName
        return dest
    def get_id(self):
        return self.id
    def set_id(self,id):
        self.id = id
    def __repr__(self):
        return(
            u"User(id={}, firstName={}, lastName={}, serviceId={}, sourceService={},totalCount ={}, intent={}, stamp={}, emotionTypeCount={}), latestMission={}, doingMission= {}".format(self.id, self.firstName, self.lastName, self.serviceId, self.sourceService, self.totalCount, self.intent, self.stamp, self.emotionTypeCount, self.latestMission, self.doingMission)
        )
    def missionDone(self, mission = None):

        self.totalCount += 1

        # 끝낸 EmotionType Count를 추가합니다.
        if self.emotionTypeCount == None:
            self.emotionTypeCount = {}
        if mission.emotionType in self.emotionTypeCount:
            self.emotionTypeCount[mission.emotionType] += 1
        else:
            self.emotionTypeCount[mission.emotionType] = 1

        # 끝낸 Intent를 추가합니다.
        if self.intent == None :
            self.intent = {}
        if mission.intent in self.intent:
            self.intent[mission.intent] += 1
        else:
            self.intent[mission.intent] = 1
        #종료한 미션의 종류와 상관없이,doingMission을 비웁니다.
        self.doingMission = None
        self.latestMission = mission.intent


    def missionStart(self,mission):
        # intent명만 받아서 바로 집어넣는다.
        self.doingMission = mission



class Stamp(object):
    def __init__(self,title,imgUrl = "", condition = {}, prompt=""):
        self.id = None
        self.title = title
        self.imgUrl = imgUrl
        self.condition = condition
        self.prompt = prompt

    @staticmethod
    def from_dict(source):
        stamp = Stamp(source[u"title"])
        if u"imgUrl" in source:
           stamp.imgUrl = source[u"imgUrl"]
        if u"condition" in source:
            stamp.condition = source[u"condition"]
        if u"prompt" in source:
            stamp.prompt = source[u"prompt"]
        return stamp

    def to_dict(self):
        dest = {
            u"title": self.title,
            u"updated": datetime.now()
        }
        if self.imgUrl:
            dest[u"imgUrl"] = self.imgUrl
        if self.condition:
            dest[u"condition"] = self.condition
        if self.prompt:
            dest[u"prompt"] = self.prompt
        return dest

    def get_id(self):
        return self.id
    def set_id(self,id):
        self.id = id
    def __repr__(self):
        return(
            "Stamp(id={}, title={}, imgUrl={}, condition={}, prompt={})".format(self.id, self.title, self.imgUrl, self.condition,self.prompt)
        )

class Mission(object):
    def __init__(self, intent, phrase, event, emotionType, actionType, category, stampUrl = "",  condition={}, notUse= False, useStamp =False, doneEvent = None, doneContext = None ):
        self.intent = intent
        self.phrase = phrase
        self.stampUrl = stampUrl
        self.event = event
        self.emotionType = emotionType
        self.actionType = actionType
        self.category = category
        self.condition = condition
        self.id = None
        self.notUse = notUse
        self.useStamp = useStamp
        self.doneEvent = doneEvent
        self.doneContext = doneContext


    @staticmethod
    def from_dict(source):
        mission = Mission(source[u"intent"],source[u"phrase"],source[u"event"],source[u"emotionType"], source[u"actionType"],source[u"category"],source[u"notUse"],source[u"useStamp"])
        if u"condition" in source:
            mission.condition = source[u"condition"]
        else:
            mission.condtion = {}
        if u"stampUrl" in source:
            mission.stampUrl = source[u"stampUrl"]
        if u"doneEvent" in source:
            mission.doneEvent = source[u"doneEvent"]
        else:
            mission.doneEvent = None
        if u"doneContext" in source:
            mission.doneContext = source[u"doneContext"]
        else:
            mission.doneContext = None

        return mission
    def to_dict(self):
        dest = {
            u"intent": self.intent,
            u"phrase" : self.phrase,
            u"emotionType" : self.emotionType,
            u"actionType" : self.actionType,
            u"category" : self.category,
            u"updated" : datetime.now(),
            u"notUse" : self.notUse,
            u"event" : self.event,
            u"useStamp" : self.useStamp,
            u"doneEvent": self.doneEvent,
            u"doneContext" : self.doneContext
        }
        if self.condtion:
            dest[u"condition"] = self.condition
        if self.stampUrl:
            dest[u"stampUrl"] = self.stampUrl
        return dest
    def get_id(self):
        return self.id
    def set_id(self,id):
        self.id = id
    def __repr__(self):
        return(
            "Mission(id={}, intent={}, phrase={}, stampUrl ={}, emotionType={}, actionType={}, category={}, condition={}, notUse = {}, event ={}, useStamp ={}, doneEvent= {})".format(self.id, self.intent, self.phrase, self.stampUrl, self.emotionType, self.actionType, self.category, self.condition, self.notUse, self.event, self.useStamp, self.doneEvent)
        )