# coding : utf-8

RedisConfig = {'host': "192.168.0.103", 'port': 6379, 'db': 0, 'password': "", 'decodedResponses': False,
               'newImagePubSubChannel': "imageReady",
               'newAudioPubSubChannel': "audioReady", 'imageHsetRoot': "image_",
               'imageHsetB64Field': "b64", 'imageHsetFacialResultField': "FEA", 'imageHsetPoseResultField': "PEA",
               'audioHsetRoot': "audio_", 'audioHsetB64Field': "b64", 'audioHsetParamsField': "params",
               'audioHsetVocalResultField': "VEA",
               'FacialQueue': "FEAQueue", 'PoseQueue': "PEAQueue", 'VocalChannel': "VEAReady",
               'DecisionSet': "decision", 'newDecisionPubSubChannel': "decisionReady", 'StartStopChannel': "StartStop"}

NaoConfig = {'IP': "192.168.0.100", 'PORT': 9559, 'imageFPS': 15,
             'audioFile': "/home/nao/recordings/microphones/audio.wav", 'audioSeconds': 5,
             'audioSampleRate': 16000, 'audioChannels': [1, 0, 0, 0], 'nAudioCh': 1, 'reactionSleepSec': 1,
             'videoSleepSec': 1.6}
# audioChannels = [front, rear, left, right]

EmotionConfig = {'emotions': ['happiness', 'neutral', 'sadness', 'fear', 'angry'],
                 'NaoReactions': {
                     'happiness': "animations/Stand/Gestures/Enthusiastic",
                     'neutral': "animations/Stand/Gestures/IDontKnow",
                     'sadness': "animations/Stand/Gestures/No",
                     'fear': "animations/Stand/Gestures/No",
                     'angry': "animations/Stand/Gestures/No",
                 },
                 'NaoTranslate': {
                     'happiness': "felice",
                     'neutral': "neutro",
                     'sadness': "triste",
                     'fear': "impaurito",
                     'angry': "arrabbiato",
                 }
}

RunnerConfig = {'RunnableAgents': ["ReactionNaoBotManager.py"]}
# "AudioNaoBotManager.py", "VideoNaoBotManager.py",

DeployPath = "/home/nao/NaoBot/"

PythonExecutable = "/usr/bin/python"
