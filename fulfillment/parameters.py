# intent와 action에 대한 정의 정리

class Actions:
    def __init__(self):
        self.welcome = "general.welcome_trigger"
        self.tutorialFeedback = "general.tutorial_feedback"
        self.newMission = "general.newMission"
        self.missionFeedback = "mission.feedback"
        self.selectMission = "general.selectMission" #이거 안필요할듯 수정하자
        self.missiondoodleGiveImage = "mission.doodle_giveImage"
        #요거는 Mission 다음에 하겠다고 하면!
        self.later = "later" # lastIntent parameter 값을 쓰자
        self.fallback = "input.unknown"
        self.feelGood = "general.feelgood"
        self.feelBad = "general.feelbad"
        self.feelSoso = "general.feelsoso"
        self.missionStart = "mission.start"
        self.generalMissionDone = "general.missionDone"
        self.emotionBad = "emotion.bad"
        self.emotionNeutral = "emotion.neutral"
        self.emotionGood = "emotion.good"
        self.greeting = "general.greeting"



class Events:
    def __init__(self):
        self.tutorial = "mission_tutorial"
        self.selectMission = "actions_intent_SELECTMISSION"
        self.newMission = "actions_intent_NEWMISSION"
        self.finalFeedback = "actions_intent_FINALFEEDBACK"
        self.welcome = "actions_intent_WELCOME"

class Intents:
    def __init__(self):
        self.finalFeedback = "general.finalFeedback"
        self.newMission = "general.newMission"
        self.selectMission = "general.selectMission"
        self.tutorial = "general.tutorial"
        self.welcome = "general.welcome"
class Contexts:
    def __init__(self):
        self.missionGoLibraryDone = "missiongolibrary_done"
        self.missionBreath = "missionbreath_done"

class Scenarios:
    def __init__(self):
        self.fallback = "fallback"
        self.feelgood = "feelgood"
        self.feelbad = "feelbad"
        self.feelsoso = "feelsoso"