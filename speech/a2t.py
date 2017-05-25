from pprint import pprint
import threading

import pyaudio
import speech_recognition as a2t

# find the desired microphone or the first input in the list
mic_index = -1
spk_index = -1
audio = pyaudio.PyAudio()
for i in range(audio.get_device_count()):
    info = audio.get_device_info_by_index(i)
    print(info['name'])
    if (info['maxInputChannels'] > 0):
        if (info['name'] == 'USB audio CODEC' or mic_index == -1):
            mic_index = i
    if (info['maxOutputChannels'] > 0 and spk_index == -1):
        spk_index = i

print("microphone:")
pprint(audio.get_device_info_by_index(mic_index))
print()
print("speaker:")
pprint(audio.get_device_info_by_index(spk_index))


def ambient_handler(rec, mic):
    while True:
        try:
            rec.adjust_for_ambient_noise(mic, 5)
        except Exception as e:
            print("ambient_handler: unknown error - {0}".format(e))


def audio_handler(rec, sample):
    wake = None
    text = None
    try:
        # print("sample", sample.sample_rate, sample.sample_width)
        # fmt = audio.get_format_from_width(sample.sample_width)
        # chs = audio.get_device_info_by_index(mic_index)['maxInputChannels']
        # spk = audio.open(output=True,
        #                  output_device_index=spk_index,
        #                  format=fmt,
        #                  channels=chs,
        #                  rate=sample.sample_rate)
        # try:
        #     spk.write(sample.frame_data)
        #     spk.stop_stream()
        # finally:
        #     spk.close()
        wake = rec.recognize_sphinx(sample,
                                    keyword_entries=[("computer", 0.5)])
        text = rec.recognize_sphinx(sample)
    except a2t.UnknownValueError:
        print("audio_handler: sample value error")
    except a2t.RequestError as e:
        print("audio_handler: recognition error - {0}".format(e))
    except Exception as e:
        print("audio_handler: unknown error - {0}".format(e))
    print("wake: \"{}\", text: \"{}\"".format(wake or "", text or ""))


rec = a2t.Recognizer()
mic = a2t.Microphone(mic_index)

"""
rec.dynamic_energy_adjustment_ratio = 2
closer = rec.listen_in_background(mic, audio_handler, 3)
closer()
threading.Thread(target=ambient_handler, args=[rec, mic]).start()
rec.adjust_for_ambient_noise(mic, 5)
"""
