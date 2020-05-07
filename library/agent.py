import json
from library.responseUtility import *
import inspect
import logging
import os

#Input Context를 그대로 OutPut으로 내보내는 방식
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


class Agent():
    def __init__(self, request):
        req = json.loads(request.body)
        self.action = req.get('queryResult').get('action')
        inputContexts = req.get('queryResult').get('outputContexts')
        self.contexts = []
        for inputContext in inputContexts:
            context = Context.fromDict(inputContext)
            self.contexts.append(context)
        payload = req.get('originalDetectIntentRequest').get('payload')
        self.sid = None
        if "data" in payload:
            self.sid = payload.get('data').get('sender').get('id')
        self.projectId = self.contexts[0].projectId
        self.session = self.contexts[0].session
        self.params = req.get("queryResult").get("parameters")
        self.responseList = []
        mainLogger.info({"request":req})

    def getIntent(self):
        intent = None
        if u"intent" in self.params:
            intent = self.params[u"intent"]
            self.addIntentToContext(intent)
        else:
            intent = self.getIntentFromContexts()
        return intent

    def getIntentFromContexts(self):
        intent = None
        for context in self.contexts:
            intentTemp = context.getIntent()
            if intentTemp != None:
                intent = intentTemp
            mainLogger.info("getIntent호출")
            mainLogger.info(intent)
        return intent
    def addIntentToContext(self, intent):
        for context in self.contexts:
            if (context.notSystemCounter())&(context.notGeneric()):
                context.addParam(key = "intent", value = intent)


#Response 관련
    def add(self, inputResponse):
        if isinstance(inputResponse, Event):
            self.event = inputResponse
        if isinstance(inputResponse,Context):
            self.contexts.append(inputResponse)
        self.responseList.append(inputResponse.toDict())
    def getResponse(self):
        response = {}
        if len(self.responseList) > 0:
            response["fulfillmentMessages"] = self.responseList
        if self.event != None:
            response["followupEventInput"] = self.event
        if self.contexts !=None :
            response["outputContexts"] = self.contexts
        return response


class Event():
    def __init__(self, eventName, params ={}):
        self.eventName = eventName
        self.params = params
    def toDict(self):
        dict = {
            "name": self.eventName,
            "parameters": self.params
        }
        return dict

#Button은 아직 못쓴다
class Button():
    def __init__(self, url, buttonText):
        self.url = url
        self.buttonText = buttonText
    def toDict(self):
        dict = {
            "type": "web_url",
            "url" : self.url,
            "buttonText" : self.buttonText
        }
        return dict

class FacebookText():
    def __init__(self,text):
        self.text = text
    def toDict(self):
        dict = {
                    "payload":{
                        "facebook":{
                            "text": self.text
                        }
                    }
                }
        return dict

class FacebookImage():
    def __init__(self,url):
        self.url = url

    def toDict(self):
        dict = {
                    "payload":{
                        "facebook":{
                            "attachment": {
                                "type": "image",
                                "payload": {
                                    "url": self.url,
                                    "is_reusable": True
                                }
                            }
                        }
                    }
                }
        return dict

class FacebookQuickReply():
    def __init__(self, title, replyList):
        self.title = title
        self.replyList = replyList

    def toDict(self):
        facebook = {}
        facebook["text"] = self.title
        facebook["quick_replies"] = []
        for quickReply in self.replyList:
            qr = {
                "content_type": "text",
                "title": quickReply,
                "payload": "<POSTBACK_PAYLOAD>"
            }
            facebook["quick_replies"].append(qr)

        dict = {
            "payload": {
                "facebook": facebook
            }
        }
        return dict
