# -*- coding: utf-8 -*-
# Copyright (C) 2018 Yihui Xiong (yihui.xiong@hotmail.com).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
import threading
import os
import json
import sys
if sys.version_info < (3, 0):
    import Queue as queue
else:
    import queue
from ctypes import (cdll, create_string_buffer,
                    CFUNCTYPE, ARRAY, Structure, POINTER, pointer,
                    c_char_p, c_int, c_float, c_void_p)

import player


ON_NONE = CFUNCTYPE(None)
ON_STRING = CFUNCTYPE(None, c_char_p)
ON_VOLUME = CFUNCTYPE(None, c_float)
ON_ERROR = CFUNCTYPE(None, c_int)

class HotwordHandler(Structure):
    _fields_ = [('on_hotword_detected', ON_NONE)]


class RecognizerHandler(Structure):
    _fields_ = [
        ('on_local_silence_detected', ON_NONE),
        ('on_remote_silence_detected', ON_NONE),
        ('on_partial_transcription', ON_STRING),
        ('on_final_transcription', ON_STRING),
        ('on_result', ON_STRING),
        ('on_volume', ON_VOLUME),
        ('on_error', ON_ERROR)
    ]

class Assistant(object):
    def __init__(self, key):
        self._load_lib()
        # self._lib.mobvoi_set_vlog_level(1)
        self._lib.mobvoi_recognizer_set_params('mobvoi_folder', os.path.join(os.path.dirname(__file__), '.mobvoi'))
        # self._lib.mobvoi_recognizer_set_params("location", "中国,北京市,北京市,海淀区,苏州街,3号,39.989602,116.316568")
        
        # Shenzhen Nanshan Xili
        self._lib.mobvoi_recognizer_set_params("location", "中国,深圳市,深圳市,南山区,留仙大道,1183号,22.581998,113.96513")

        self._lib.mobvoi_sdk_init(key)
        self._lib.mobvoi_recognizer_init_offline()
        self._lib.mobvoi_tts_init()

        self._on_hotword_detected = ON_NONE(self.on_hotword_detected)
        self.hotword_handler = HotwordHandler(self._on_hotword_detected)
        self._lib.mobvoi_hotword_add_handler(pointer(self.hotword_handler))

        self._on_local_silence_detected = ON_NONE(self.on_local_silence_detected)
        self._on_remote_silence_detected = ON_NONE(self.on_remote_silence_detected)
        self._on_partial_transcription = ON_STRING(self.on_partial_transcription)
        self._on_final_transcription = ON_STRING(self.on_final_transcription)
        self._on_result = ON_STRING(self.on_result)
        self._on_volume = ON_VOLUME(self.on_volume)
        self._on_error = ON_ERROR(self.on_error)

        self.recognizer_handler = RecognizerHandler(
             self._on_local_silence_detected,
             self._on_remote_silence_detected,
             self._on_partial_transcription,
             self._on_final_transcription,
             self._on_result,
             self._on_volume,
             self._on_error
        )

        self._lib.mobvoi_recognizer_set_handler(pointer(self.recognizer_handler))

        self.queue = queue.Queue(maxsize=1024)
        self.done = False

    def __del__(self):
        self._lib.mobvoi_sdk_cleanup()

    def hotword_start(self):
        self._lib.mobvoi_hotword_start()

        # self.set_keywords(['开灯', '关灯', '播放音乐', '几点了', '暂停', '魔镜'])
        # self._lib.mobvoi_recognizer_start(5)

    def hotword_stop(self):
        self._lib.mobvoi_hotword_stop()

    def recognizer_start(self):
        # RECOGNIZER_ONLINE_ASR = 0
        # RECOGNIZER_ONLINE_SEMANTIC = 1
        # RECOGNIZER_ONLINE_ONEBOX = 2
        # RECOGNIZER_OFFLINE = 3
        # RECOGNIZER_MIX = 4
        # RECOGNIZER_KEYWORDS = 5
        self._lib.mobvoi_recognizer_start(2)

    def recognizer_stop(self):
        self._lib.mobvoi_recognizer_stop()

    def on_hotword_detected(self):
        self.recognizer_start()

    def on_local_silence_detected(self):
        print('on_local_silence_detected')

    def on_remote_silence_detected(self):
        print('on_remote_silence_detected')

    def on_partial_transcription(self, text):
        print('on_partial_transcription: {}'.format(text))

    def on_final_transcription(self, text):
        print('on_final_transcription: {}'.format(text))

    def on_result(self, text):
        print('on_result:')
        response = json.loads(text)
        print(json.dumps(response, sort_keys=True, indent=4, ensure_ascii=False))

        if response['status'] == 'success':
            if 'languageOutput' in response:
                text = response['languageOutput']['displayText']
                speech = self.synthesize(text)
                self.on_speech(speech)

    def on_speech(self, speech):
        player.play(speech)

    def on_volume(self, volume):
        # print('on_volume: {}'.format(volume))
        pass
            

    def on_error(self, error_code):
        print('on_error: {}'.format(error_code))

    def start(self):
        self.done = False
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

        self.hotword_start()

    def stop(self):
        self.done = True
        self.queue.put('')

        # self._lib.mobvoi_recognizer_stop()

        self.hotword_stop()

    def put(self, data):
        self.queue.put(data)

        # self._lib.mobvoi_send_speech_frame(data, len(data))

    def _run(self):
        while not self.done:
            data = self.queue.get()
            self._lib.mobvoi_send_speech_frame(data, len(data))

    def set_keywords(self, keywords):
        StringPointer = ARRAY(c_char_p, len(keywords)) 
        c_keywords = StringPointer()
        for i in range(len(keywords)):
            c_keywords[i] = c_char_p(keywords[i])

        self._lib.mobvoi_recognizer_set_keywords(len(keywords), c_keywords, 'multi_keywords')
        self._lib.mobvoi_recognizer_set_params('offline_model', 'multi_keywords')
        self._lib.mobvoi_recognizer_build_keywords('multi_keywords')

    # tts type: 1 - online, 2 - offline, 3 - mix
    def synthesize(self, text, tts_type=2):
        if type(text) is not str:
            text = text.encode('utf-8')
        self._lib.mobvoi_tts_start_synthesis(tts_type, text)

        size = 1024
        buffer = create_string_buffer(size)
        ret = self._lib.mobvoi_tts_read_data(buffer, size)
        while ret > 0:
            # print('{} bytes'.format(ret))
            yield buffer.raw[:ret]
            ret = self._lib.mobvoi_tts_read_data(buffer, size)

        self._lib.mobvoi_tts_cancel_synthesis()


    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.stop()

    def _load_lib(self):
        os_name = os.uname()[0]
        platform = os.uname()[4]

        if platform.startswith('armv'):
            platform = platform[:5]

        lib_name = 'libmobvoisdk.so'
        lib_path = os.path.join(os.path.dirname(__file__), 'lib', platform, lib_name)

        if os_name != 'Linux' or not os.path.isfile(lib_path):
            raise OSError('{} {} is not supported.'.format(os_name, platform))

        self._lib = cdll.LoadLibrary(lib_path)

        # int mobvoi_sdk_init(const char* appkey)
        self._lib.mobvoi_sdk_init.argtypes = [c_char_p]
        self._lib.mobvoi_sdk_init.restype = c_int

        # void mobvoi_sdk_cleanup()
        self._lib.mobvoi_sdk_cleanup.argtypes = []
        self._lib.mobvoi_sdk_cleanup.restype = None

        # void mobvoi_hotword_add_handler(mobvoi_hotword_handler_vtable* handlers)
        self._lib.mobvoi_hotword_add_handler.argtypes = [POINTER(HotwordHandler)]
        self._lib.mobvoi_hotword_add_handler.restype = None

        # void mobvoi_hotword_remove_handler(mobvoi_hotword_handler_vtable* handlers)
        self._lib.mobvoi_hotword_remove_handler.argtypes = [POINTER(HotwordHandler)]
        self._lib.mobvoi_hotword_remove_handler.restype = None

        # void mobvoi_recognizer_set_handler(mobvoi_recognizer_handler_vtable* handlers)
        self._lib.mobvoi_recognizer_set_handler.argtypes = [POINTER(RecognizerHandler)]
        self._lib.mobvoi_recognizer_set_handler.restype = None

        # void mobvoi_set_vlog_level(int level)array
        self._lib.mobvoi_set_vlog_level.argtypes = [c_int]
        self._lib.mobvoi_set_vlog_level.restype = None

        # int mobvoi_send_speech_frame(char * frame, int size)
        self._lib.mobvoi_send_speech_frame.argtypes = [c_char_p, c_int]
        self._lib.mobvoi_send_speech_frame.restype = c_int

        # int mobvoi_hotword_start()
        self._lib.mobvoi_hotword_start.argtypes = []
        self._lib.mobvoi_hotword_start.restype = c_int

        # int mobvoi_hotword_stop()
        self._lib.mobvoi_hotword_stop.argtypes = []
        self._lib.mobvoi_hotword_stop.restype = c_int

        # int mobvoi_recognizer_init_offline()
        self._lib.mobvoi_recognizer_init_offline.argtypes = []
        self._lib.mobvoi_recognizer_init_offline.restype = c_int

        # void mobvoi_recognizer_set_params(const char* key, const char* value)
        self._lib.mobvoi_recognizer_set_params.argtypes = [c_char_p, c_char_p]
        self._lib.mobvoi_recognizer_set_params.restype = None

        # void mobvoi_recognizer_set_data(mobvoi_recognizer_offline_data_type type, int num, const char* data[])
        # TODO: char *data[]
        self._lib.mobvoi_recognizer_set_data.argtypes = [c_int, c_int, c_void_p]
        self._lib.mobvoi_recognizer_set_data.restype = None


        # void mobvoi_recognizer_set_keywords(int num, const char* keywords[], const char* model_name)
        self._lib.mobvoi_recognizer_set_keywords.argtypes = [c_int, c_void_p, c_char_p]
        self._lib.mobvoi_recognizer_set_keywords.restype = None

        # void mobvoi_recognizer_build_data()
        self._lib.mobvoi_recognizer_build_data.argtypes = []
        self._lib.mobvoi_recognizer_build_data.restype = None


        # void mobvoi_recognizer_build_keywords(const char* model_name)
        self._lib.mobvoi_recognizer_build_keywords.argtypes = [c_char_p]
        self._lib.mobvoi_recognizer_build_keywords.restype = None

        # int mobvoi_recognizer_start(mobvoi_recognizer_type recognizer_type)
        self._lib.mobvoi_recognizer_start.argtypes = [c_int]
        self._lib.mobvoi_recognizer_start.restype = c_int

        # int mobvoi_recognizer_stop()
        self._lib.mobvoi_recognizer_stop.argtypes = []
        self._lib.mobvoi_recognizer_stop.restype = c_int

        # int mobvoi_recognizer_cancel()
        self._lib.mobvoi_recognizer_cancel.argtypes = []
        self._lib.mobvoi_recognizer_cancel.restype = c_int


        # int mobvoi_tts_init()
        self._lib.mobvoi_tts_init.argtypes = []
        self._lib.mobvoi_tts_init.restype = None

        # void mobvoi_tts_set_params(const char* key, const char* value)
        self._lib.mobvoi_tts_set_params.argtypes = [c_char_p, c_char_p]
        self._lib.mobvoi_tts_set_params.restype = None

        # int mobvoi_tts_start_synthesis(mobvoi_tts_type type, const char* text)
        self._lib.mobvoi_tts_start_synthesis.argtypes = [c_int, c_char_p]
        self._lib.mobvoi_tts_start_synthesis.restype = c_int

        # int mobvoi_tts_cancel_synthesis()
        self._lib.mobvoi_tts_cancel_synthesis.argtypes = []
        self._lib.mobvoi_tts_cancel_synthesis.restype = None

        # int mobvoi_tts_read_data(char* data, int length)
        self._lib.mobvoi_tts_read_data.argtypes = [c_void_p, c_int]
        self._lib.mobvoi_tts_read_data.restype = c_int


def main():
    from voice_engine.source import Source

    # TODO: Get a key from https://ai.chumenwenwen.com
    KEY = ''

    src = Source(rate=16000, channels=1)
    
    assistant = Assistant(KEY)
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
