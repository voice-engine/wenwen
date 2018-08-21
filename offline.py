# -*- coding: utf-8 -*-

import time
import json

from assistant import Assistant
import player


class Mirror(Assistant):
    def __init__(self, key=''):
        super(Mirror, self).__init__(key)

        self.set_keywords(['开灯', '关灯', '播放音乐', '几点了', '暂停', '魔镜', '今天的天气怎么样', '会下雨吗'])

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
        print('on_partial_transcription: {}'.format(text))

        self.listening = False
        player.play(self.synthesize(text))
        self.listening = True
        

def main():
    from voice_engine.source import Source

    src = Source(rate=16000, channels=1)
    assistant = Mirror()

    src.pipeline(assistant)
    src.pipeline_start()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

    src.pipeline_stop()

if __name__ == '__main__':
    main()