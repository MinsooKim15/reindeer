# TODO : Event를 돌려준 거 만들자

class FulfillmentResponse():
    def __init__(self):
        self.data = {"fulfillmentText" : "",
                     "payload": {}
                }
    def addTextReply(self, text):
        self.data["fulfillmentText"] = text
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

    def getResponse(self):
        return self.data

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