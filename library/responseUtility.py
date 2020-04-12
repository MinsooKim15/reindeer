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


    # def addContexts(self, contexts):
    #     print(self.data)
    #     for context in contexts:
    #         if "outputContexts" in self.data.keys():
    #             self.data["outputContexts"].append(context)
    #         else:
    #             self.data["outputContexts"] = [context]

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
                        "payload": "<POSTBACK_PAYLOAD>"
                    }
                    facebook["quick_replies"].append(qr)

                message = {
                    "payload": {
                        "facebook": facebook
                    }
                }
            messages.append(message)
        finalResult = {}
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