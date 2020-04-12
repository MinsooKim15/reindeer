# TODO : Event를 돌려준 거 만들자
# TODO : Contexts 클래스 만들기
# TODO : Input을 하나의 Agent Class로 만들기

class FulfillmentResponse():
    def __init__(self):
        self.data = {"fulfillmentText" : "",
                     "payload": {}
                }
    def addTextReply(self, text):
        self.data["fulfillmentText"] = text
    def dumpResponse(self):
        self.data = {
            "fulfillmentMessages":[
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
        facebook = {}
        facebook["text"] = title
        quickReplies = []
        for reply in quickReplyList:
            quickReply = {
                "content_type": "text",
                "title": reply,
                "payload": "<POSTBACK_PAYLOAD>"
            }
            quickReplies.append(quickReply)

        facebook["quick_replies"] = quickReplies

        self.data["payload"]["facebook"] = facebook
    def addFollowupEvent(self, event, params ={}):
        # params는 dict로 들어와야 함
        eventDict = {
            "name" : event,
            "parameters" : params
        }
        self.data["followupEventInput"] = eventDict
    def addContexts(self, contexts):
        print(self.data)
        for context in contexts:
            if "outputContexts" in self.data.keys():
                self.data["outputContexts"].append(context)
            else:
                self.data["outputContexts"] = [context]

    def getResponse(self):
        return self.data
    def addImage(self, url):
        facebook = {}
        facebook["attachment"] = {
            "type" : "image",
            "payload" : {
                "url" : url,
                "is_reusable" : True
            }
        }
        self.data["payload"]["facebook"] = facebook



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