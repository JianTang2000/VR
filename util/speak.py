import pyttsx3
from threading import Thread
import time


# def speak(goalStr):
#     engine = pyttsx3.init()  # 初始化
#     engine.setProperty('voice', "zh")  # 设置发音人，不过我电脑似乎不起作用
#     # engine.setProperty('voice', "com.apple.speech.synthesis.voice.mei-jia")
#     rate = engine.getProperty('rate')  # 改变语速  范围为0-200   默认值为200
#     engine.setProperty('rate', rate - 40)
#     engine.setProperty('volume', 0.7)  # 设置音量  范围为0.0-1.0  默认值为1.0
#     engine.say(goalStr)  # 预设要朗读的文本数据
#     engine.runAndWait()  # 读出声音
#
#
# if __name__ == '__main__':
#     strValue = "昆明的天气情况如下：日期: 08月18日(星期二), 天气: 雨, 温度: 20℃, PM2.5: 20, 相对湿度: 92%"
#     speak(strValue)


class Speaker:
    def __init__(self):
        self.voice_engine = pyttsx3.init()

    def speak_(self, sentence):
        self.voice_engine.say(sentence)
        self.voice_engine.runAndWait()


class SpeakerThread(Thread):
    def __init__(self, thread_name):
        super(SpeakerThread, self).__init__(name=thread_name)

    def run(self) -> None:
        t1 = time.time()
        print("子线程启动")
        voice_engine = pyttsx3.init()  # init 放在run里，而不是初始化在self变量里
        voice_engine.say('花盆左20°，1米')
        voice_engine.runAndWait()
        voice_engine.say('人右30°，1.2米')
        voice_engine.runAndWait()
        print('子线程结束')
        print(f"time cosy is {time.time() - t1}")


if __name__ == "__main__":
    speaker_thread = SpeakerThread("speaker_thread")
    speaker_thread.setDaemon(True)
    speaker_thread.start()
    time.sleep(100)
