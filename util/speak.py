# import pyttsx3
#
#
# class Speaker:
#     def __init__(self):
#         self.voice_engine = pyttsx3.init()
#
#     def say(self, sentence):
#         self.voice_engine.say(sentence)
#         self.voice_engine.runAndWait()
#
#
# if __name__ == "__main__":
#     speaker = Speaker()
#     speaker.say("花盆左20°，1米")
#     speaker.say("人右30°，1.2米")
#     speaker.say("花盆左20°，1.5米")
#     speaker.say("人右30°，1.6米")
#     speaker.say("花盆左20°，1.04米")
#     speaker.say("人右30°，1.266米")

import win32com.client
from threading import Thread
import time


class SpeakerThread(Thread):
    def __init__(self, thread_name):
        super(SpeakerThread, self).__init__(name=thread_name)

    def run(self) -> None:
        # time.sleep(2)
        print("子线程启动")
        speak = win32com.client.Dispatch('SAPI.SPVOICE')
        speak.Speak('进入子线程')
        speak.Speak('花盆左20°，1米')
        speak.Speak('人右30°，1.2米')
        speak.Speak('花盆左20°，1.5米')
        speak.Speak('人右30°，1.6米')
        speak.Speak('花盆左20°，1.04米')
        speak.Speak('人右30°，1.266米')
        speak.Speak('子线程结束')
        print('子线程结束')


if __name__ == "__main__":
    speak = win32com.client.Dispatch('SAPI.SPVOICE')
    speak.Speak('程序开始运行!')  # 这两行必须有,不然speak会报错

    speaker_thread = SpeakerThread("speaker_thread")
    speaker_thread.setDaemon(True)
    speaker_thread.start()
    time.sleep(100)
