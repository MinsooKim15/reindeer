from firebase_admin import firestore
from fulfillment.models import *
import google.cloud.exceptions

class FirebaseQuery(object):

    def get_user(self,id,sourceService):
        db = firestore.client()
        userId = "a"
        print("getUser입니다.")
        print("id:",id)
        print("sourceService", sourceService)
        if sourceService == "facebook":
            userId = u"fb_" + id
        else:
            userId = id
        print(userId)
        doc_ref =  db.collection(u"users").document(userId)
        doc = doc_ref.get()
        if doc.exists:
            user = User.from_dict(doc.to_dict())
            user.set_id(userId)
        else:
            user = None
        # 사용시 None 체크로 없는지 있는지 보자
        return user
    def set_user(self,user):

        db = firestore.client()
        doc_ref = db.collection(u"users").document(user.get_id())
        doc_ref.set(user.to_dict())
    def get_mission_list(self):
        # 모든 mission 리스트를 가져온다.
        db = firestore.client()
        docs = db.collection(u"missions").stream()
        missionList = []
        for doc in docs:
            mission = Mission.from_dict(doc.to_dict())
            mission.set_id(doc.id)
            missionList.append(mission)
        return missionList
    def get_stamp_list(self):
        db = firestore.client()
        docs = db.collection(u"stamps").stream()
        stampList = []
        for doc in docs:
            stamp = Stamp.from_dict(doc.to_dict())
            stamp.set_id(doc.id)
            stampList.append(stamp)
        return stampList
    def get_mission_by_intent(self, intent):
        db = firestore.client()
        doc_ref = db.collection(u"missions").where(u"intent", u"==", intent)
        docs = doc_ref.stream()
        missionList = []
        for doc in docs:
            mission = Mission.from_dict(doc.to_dict())
            mission.set_id(doc.id)
            missionList.append(mission)
        print(missionList)

        if len(missionList) == 1:
            mission = missionList[0]
        else:
            mission = None
        return mission