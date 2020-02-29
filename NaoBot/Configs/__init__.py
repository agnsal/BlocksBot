RedisConfig = {'host': "192.168.0.103", 'port': 6379, 'db': 0, 'password': "", 'decodedResponses': False,
               'newImagePubSubChannel': "imageReady", 'newImageMsgRoot': "image",
               'newAudioPubSubChannel': "audioReady", 'newAudioMsgRoot': "audio", 'imageHsetRoot': "image",
               'imageHsetB64Field': "b64", 'imageHsetFacialResultField': "FEA", 'imageHsetPoseResultField': "PEA",
               'audioHsetRoot': "audio", 'audioHsetB64Field': "b64", 'audioHsetVocalResultField': "VEA",
               'FacialQueue': "FEAQueue", 'PoseQueue': "PEAQueue", 'VocalChannel': "VEAReady"}

NaoConfig = {'IP': "192.168.0.100", 'PORT': 9559, 'imageFPS': 15,
             'audioFile': "/data/home/nao/recordings/microphones/audio.wav", 'audioSeconds': 5,
             'audioSampleRate': 16000, 'audioChannels': [1, 0, 0, 0], 'nAudioCh': 1}
# audioChannels = [front, rear, left, right]