# -*- coding: utf-8 -*-

import time
import json
import datetime

from assistant import Assistant
import player

import yeelight
import gpiozero


led = gpiozero.LED(5)
led.on()

lamp = yeelight.Bulb('192.168.0.104')


weekday = ('1', '2', '3', '4', '6', '天')


class Mirror(Assistant):
    def __init__(self, key=''):
        super(Mirror, self).__init__(key)

        self.set_keywords(['开灯', '关灯', '播放音乐', '几点了', '现在几点', '今天几号', '今天星期几', '暂停', '小呆', '今天的天气怎么样', '会下雨吗'])

        self.listening = False

    def start(self):
        super(Mirror, self).start()

    def stop(self):
        super(Mirror, self).stop()

    def put(self, data):
        if self.listening:
            self.queue.put(data)

    def hotword_start(self):
        # recognize keywords offline
        self._lib.mobvoi_recognizer_start(5)
        self.listening = True

    def hotword_stop(self):
        self.listening = False
        # self._lib.mobvoi_recognizer_stop()

    def on_partial_transcription(self, text):
        self.listening = False
        led.on()
        try:
            if text.find('开灯') >= 0:
                lamp.turn_on()
            elif text.find('关灯') >= 0:
                lamp.turn_off()
            elif text.find('几点了') >= 0 or text.find('现在几点') >= 0:
                now = datetime.datetime.now()
                player.play(self.synthesize('现在是{}点{}分'.format(now.hour, now.minute)))
            elif text.find('今天星期几') >= 0 or text.find('今天几号') >= 0:
                now = datetime.datetime.now()
                player.play(self.synthesize('今天是{}月{}号，星期{}'.format(now.month, now.day, weekday[now.weekday()])))
            else:
                player.play(self.synthesize(text))
                time.sleep(1)
        except Exception as e:
            print(e)

        led.off()
        self.listening = True

        
        print('on_partial_transcription: {}'.format(text))
        

def main():
    from voice_engine.source import Source
    from voice_engine.ns import NS
    from bf import BF

    src = Source(rate=16000, channels=8)
    bf = BF()
    ns = NS()
    assistant = Mirror()

    src.pipeline(bf, ns, assistant)
    src.pipeline_start()

    led.off()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

    src.pipeline_stop()

if __name__ == '__main__':
    main()


