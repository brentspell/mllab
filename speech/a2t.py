import threading
import speech_recognition as a2t

def ambient_handler(rec, mic):
    while True:
        rec.adjust_for_ambient_noise(mic, 5)

def audio_handler(rec, sample):
    try:
        print(rec.recognize_sphinx(sample))
    except a2t.UnknownValueError:
        print('sample value error')
    except a2t.RequestError as e:
        print('recognition error: {0}'.format(e))

rec = a2t.Recognizer()
mic = a2t.Microphone()

rec.dynamic_energy_adjustment_ratio = 2
rec.listen_in_background(mic, audio_handler)
threading.Thread(target=ambient_handler, args=[rec, mic]).start()
