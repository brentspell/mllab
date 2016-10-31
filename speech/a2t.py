import threading
import speech_recognition as a2t

def audio_handler(rec, audio):
   try:
      print(rec.recognize_sphinx(audio))
   except a2t.UnknownValueError:
      print('audio value error')
   except a2t.RequestError as e:
      print('recognition error: {0}'.format(e))

def ambient_handler():
   rec.adjust_for_ambient_noise(src)

rec = a2t.Recognizer()
src = a2t.Microphone()

rec.listen_in_background(src, audio_handler)
threading.Timer(5, ambient_handler).start()
