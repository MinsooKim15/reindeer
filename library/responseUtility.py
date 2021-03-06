# TODO : Event를 돌려준 거 만들자
# TODO : Contexts 클래스 만들기
# TODO : Input을 하나의 Agent Class로 만들기

class FulfillmentResponse():
    #Facebook Only 지향으로 만들어졌습니다. 수정하거면 전체의 수정을 해야 합니다.

    def __init__(self):
        self.data = {"fulfillmentText" : "",
                     "payload": {}
                }
        self.replyList = []
        self.contexts = None
        self.event = None
        self.button = None
        self.contexts = None
        self.webviewUrl = None
    def addTextReply(self, text):
        # self.data["fulfillmentText"] = text
        reply = {
            u"type" : "text",
            u"text" : text
        }
        self.replyList.append(reply)
    def addImageReply(self, url):
        reply = {
            u"type" : "image",
            u"url" : url
        }
        self.replyList.append(reply)
    def addContexts(self,inputContexts):
        if self.contexts != None:
            for inputContext in inputContexts:
                self.contexts.append(inputContext)
        else:
            self.contexts = inputContexts

    def dumpResponse(self):
        self.data = {
            u"fulfillmentMessages":[
                {
                    "payload":{
                        "facebook":{
                            "text": "고생했어"
                        }
                    }

                },
                {
                    "payload":{
                        "facebook":{
                            "attachment":{
                                "type": "image",
                                "payload": {
                                    "url": "https://firebasestorage.googleapis.com/v0/b/reindeer-fulfillment.appspot.com/o/%E1%84%8F%E1%85%A1%E1%84%86%E1%85%A6%E1%84%85%E1%85%A1%E1%84%85%E1%85%B3%E1%86%AF%E1%84%86%E1%85%A5%E1%86%B7%E1%84%8E%E1%85%AE%E1%84%86%E1%85%A7%E1%86%AB%E1%84%8B%E1%85%A1%E1%86%AB%E1%84%83%E1%85%AB_8.png?alt=media&token=7cf24584-7ecc-434a-91d7-8c99fd7d1e18",
                                    "is_reusable": True
                                }
                            }

                        }
                    }
                }
            ]
        }
        # self.data["payload"]["facebook"]["text"] = self.data["fulfillmentText"]
    def addFacebookQuickReply(self, title, quickReplyList):
        reply = {
            u"type": "quickReply",
            u"title": title,
            u"quickReplyList": quickReplyList
        }
        self.replyList.append(reply)
        # facebook = {}
        # facebook["text"] = title
        # quickReplies = []
        # for reply in quickReplyList:
        #     quickReply = {
        #         "content_type": "text",
        #         "title": reply,
        #         "payload": "<POSTBACK_PAYLOAD>"
        #     }
        #     quickReplies.append(quickReply)
        #
        # facebook["quick_replies"] = quickReplies
        #
        # self.data["payload"]["facebook"] = facebook
    def addFollowupEvent(self, event, params ={}):
        # params는 dict로 들어와야 함
        # eventDict = {
        #     "name" : event,
        #     "parameters" : params
        # }
        # self.data["followupEventInput"] = eventDict

        # reply = {
        #     "type" : "event",
        #     "name" : event,
        #     "parameters": params
        # }
        self.event = {
            "name": event,
            "parameters": params
        }
    def addButton(self,url,buttonText):
        self.button = {
            "type": "web_url",
            "url" : url,
            "buttonText" : buttonText
        }
    def addWebview(self, url):
        self.webviewUrl = url

    def addContexts(self, contexts):
        #Context Class 상태로 받는다.

        for context in contexts:
            if self.contexts == None:
                self.contexts = [context.toDict()]
            else:
                self.contexts.append(context.toDict())


    def getResponse(self):
        messages = []
        for reply in self.replyList:
            print(reply)
            message = {}
            if reply[u"type"] == "text":
                message = {
                    "payload":{
                        "facebook":{
                            "text": reply[u"text"]
                        }
                    }
                }
            elif reply[u"type"] == "image":
                message = {
                    "payload":{
                        "facebook":{
                            "attachment": {
                                "type": "image",
                                "payload": {
                                    "url": reply["url"],
                                    "is_reusable": True
                                }
                            }
                        }
                    }
                }
            elif reply[u"type"] == "quickReply":
                facebook = {}
                facebook["text"] = reply["title"]
                facebook["quick_replies"] = []
                for quickReply in reply["quickReplyList"]:
                    qr = {
                        "content_type" : "text",
                        "title" : quickReply,
                        "payload": quickReply
                    }
                    facebook["quick_replies"].append(qr)

                message = {
                    "payload": {
                        "facebook": facebook
                    }
                }
            print(message)
            messages.append(message)
        print("messages:", messages)
        finalResult = {}
        print(finalResult)
        if len(messages) > 0:
            finalResult["fulfillmentMessages"] = messages
        if self.event != None:
            finalResult["followupEventInput"] = self.event
        if self.contexts !=None :
            finalResult["outputContexts"] = self.contexts
        if self.button !=None:
            # finalResult = {
            #     "payload":{
            #         "facebook":{
            #             "attachment":{
            #                 "type" : "template",
            #                 "payload":{
            #                     "template_type": "button",
            #                     "text": "어디 들어가는 문구지",
            #                     "buttons": [
            #                         {
            #                             "type": self.button["type"],
            #                             "url": self.button["url"],
            #                             "title": self.button["buttonText"]
            #                         }
            #                     ]
            #                 }
            #             }
            #         }
            #     }
            # }
            finalResult = {
                "payload":{
                    "facebook":{
                        "attachment":{
                            "type" : "template",
                            "payload":{
                                "template_type": "generic",
                                "elements":[
                                    {
                                        "image_url": "http://i.011st.com/ex_t/R/450x450/1/85/1/src/cat/19/0/7/4/1/4/5/tKtNR/19074145_1.jpg",
                                        "title": "타이틀",
                                        "subtitle": "서브타이틀",
                                        "default_action": {
                                            "type": "web_url",
                                            "url": "https://www.buymeacoffee.com/reindeer",
                                            "webview_height_ratio": "tall"
                                        },
                                        "buttons": [
                                            {
                                                "type": self.button["type"],
                                                "url": self.button["url"],
                                                "title": self.button["buttonText"]
                                            }
                                        ]
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        if self.webviewUrl != None:
            print(self.webviewUrl)
            finalResult = {
                "payload": {
                "facebook": {
                    "attachment": {
                        "type":"template",
                        "payload":{
                            "template_type":"button",
                            "text":"타이머 시작!",
                            "buttons":[
                                    {
                                        "type":"web_url",
                                        "url":self.webviewUrl,
                                        "title":"URL Button",
                                        "webview_height_ratio": "tall"
                                    }
                                ]
                            }
                        }
                    }
                }
            }


        if self.contexts != None:
            finalResult["outputContexts"] = self.contexts

        print("ffResponse Return함.")
        print(finalResult)
        return finalResult
        # return self.data

    # def addImage(self, url):
    #     facebook = {}
    #     facebook["attachment"] = {
    #         "type" : "image",
    #         "payload" : {
    #             "url" : url,
    #             "is_reusable" : True
    #         }
    #     }
    #     self.data["payload"]["facebook"] = facebook

class Context():
    def __init__(self, projectId, session, contextName, lifeSpan = 1,  parameters = {}):
        self.projectId = projectId
        self.session = session
        self.lifeSpan = lifeSpan
        self.parameters = parameters
        self.contextName = contextName
    def toDict(self):
        result = {
            "name": "projects/" + self.projectId + "/agent/sessions/" + self.session + "/contexts/" + self.contextName,
            "lifespanCount": self.lifeSpan,
            "parameters": self.parameters
        }
        return result

    @staticmethod
    def fromDict(source):
        print(source)
        projectId = source['name'].split("/")[1]
        session = source['name'].split("/")[4]
        contextName = source['name'].split("/")[6]
        if u"lifeSpanCount" in source:
            lifespan = source[u"lifeSpanCount"]
        else:
            lifeSpan = 0
        if u"parameters" in source:
            param = source[u"parameters"]
        else:
            param = {}
        context = Context(projectId = projectId, session = session, contextName= contextName, lifeSpan=lifeSpan, parameters = param)
        return context

    def extandIntentLifeSpan(self, lifespanCount):
        #generic과 System count는 연장하지 않음
        if (self.notGeneric()) & (self.notSystemCounter()):
            self.parameters[u"lifeSpanChanged"] = True
            self.lifeSpan = lifespanCount
    def addIntent(self,intent):
        if (self.notGeneric()) & (self.notSystemCounter()):
            self.parameters[u"intent"] = intent

    def notGeneric(self):
        isGeneric = True
        if self.contextName == "generic":
            isGeneric = False
        return isGeneric
    def notSystemCounter(self):
        isSystemCounter = True
        if self.contextName == "__system_counters__":
            isSystemCounter = False
        return isSystemCounter
    def getIntent(self):
        if u"intent" in self.parameters:
            return self.parameters[u"intent"]
        else:
            return None
    def addParam(self,key, value):
        self.parameters[key] = value
    def clearCount(self):
        self.lifeSpan = 0



def makeContext(projectId, session, lifeSpan, parameters,contextName):
    result = {
        "name" : "projects/"+projectId+"/agent/sessions/"+session+"/contexts/"+contextName,
        "lifespanCount" : lifeSpan,
        "parameters" : parameters
    }
    return result
def makeContextsLifespan(contexts, lifespanCount):
    for context in contexts:
        contextName = context["name"].split("/")[-1]
        if (contextName != "generic") & (contextName != "__system_counters__"):
            if u"parameters" in context:
                if u"lifeSpanChanged" in context["parameters"]:
                    # 이미 LIFESPAN 조정이 되어 있다면?
                    pass
                else:
                    context["parameters"][u"lifeSpanChanged"] = True
                    context["lifespanCount"] = lifespanCount
            else:
                context["parameters"] = {
                    u"lifeSpanChanged" : True
                }
                context["lifespanCount"] = lifespanCount

    return contexts
def addIntentToContexts(contexts,intent):
    for context in contexts:
        contextName = context["name"].split("/")[-1]
        if (contextName != "generic") & (contextName != "__system_counters__"):
            if u"parameters" in context:
                context["parameters"]["intent"] = intent
            else:
                context["parameters"] = {
                    "intent" : intent
                }
    return contexts

# EventInput의 좋은 예시
# reply = {
#             "followupEventInput": {
#             "name": paramEvents.tutorial,
#             "parameters": {
#             }
#         }

# class FacebookReply():
#     def __init__(self):
#         self.data = {}
#
#     def addTextReply(self,text):
#         self.data["text"] = text
#     def addQuickReplies(self, quickReplyList):
#         quickReplies = []
#         for reply in quickReplyList:
#             quickReply = {
#                 "content_type" : "text",
#                 "title" : reply,
#                 "payload" : "<POSTBACK_PAYLOAD>"
#             }
#             quickReplies.append(quickReply)
#
#         self.data["quick_replies"] = quickReplies
#     def getReply(self):
#         return self.data

# 성공 답변 예시
# tempReply = {
            #     "fulfillmentText": "컨택스트 없는디?",
            #     "payload" : {
            #         "facebook": {
            #             "text": "Pick a color:",
            #             "quick_replies": [
            #                 {
            #                     "content_type": "text",
            #                     "title": "Red",
            #                     "payload": "<POSTBACK_PAYLOAD>"
            #                 }, {
            #                     "content_type": "text",
            #                     "title": "Green",
            #                     "payload": "<POSTBACK_PAYLOAD>"
            #                 }
            #             ]
            #         }
            #         }
            # }

#WEBVIEW 예시
# {
#     "fulfillmentMessages": [
#         {
#         "payload": {
#         "facebook": {
#             "attachment": {
#                 "type":"template",
#                 "payload":{
#                     "template_type":"button",
#                     "text":"Try the URL button!",
#                     "buttons":[
#                         {
#                             "type":"web_url",
#                             "url":"https://www.messenger.com/",
#                             "title":"URL Button",
#                             "webview_height_ratio": "tall"
#                         }
#                     ]
#                 }
#             }
#         }}
#     }]}