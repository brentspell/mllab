import pyttsx

t2a = pyttsx.init()
t2a.setProperty('rate', 150)

t2a.say(text)
t2a.runAndWait()
