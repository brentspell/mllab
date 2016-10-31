import threading
import speech_recognition as a2t

def audio_handler(rec, sample):
    try:
        print(rec.recognize_sphinx(sample))
    except a2t.UnknownValueError:
        print('sample value error')
    except a2t.RequestError as e:
        print('recognition error: {0}'.format(e))

def ambient_handler(rec):
    rec.adjust_for_ambient_noise(mic)

rec = a2t.Recognizer()
mic = a2t.Microphone()

rec.listen_in_background(mic, audio_handler)
threading.Timer(5, ambient_handler, [rec]).start()
