# Copyright (C) 2017 Yihui Xiong (yihui.xiong@hotmail.com).
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
import os
import json
from ctypes import (CFUNCTYPE,
                    cdll,
                    c_bool, c_char_p, c_int, c_uint, c_void_p, c_double, Structure, POINTER, pointer, byref)


ON_CALLBACK = CFUNCTYPE(None)

ON_ERROR = CFUNCTYPE(None, c_int)

ON_FINAL_TRANSCRIPTION = CFUNCTYPE(None, c_char_p)

ON_RESULT = CFUNCTYPE(None, c_char_p, c_char_p)


class HotwordHandler(Structure):
    _fields_ = [('on_hotword_detected', ON_CALLBACK)]


class SpeechClientHandler(Structure):
    _fields_ = [
        ('on_remote_silence_detected', ON_CALLBACK),
        ('on_final_transcription', ON_FINAL_TRANSCRIPTION),
        ('on_result', ON_RESULT),
        ('on_error', ON_ERROR),
        ('on_local_silence_detected', ON_CALLBACK)
    ]



class Assistant(object):
    def __init__(self):
        self._load_lib()
        self._lib.set_vlog_level(0)
        self._lib.sdk_init()

        # Shenzhen Nanshan Xili
        self._lib.set_location(22.581998, 113.96513)

    def __del__(self):
        self._lib.sdk_cleanup()

    def on_hotword_detected(self):
        self._lib.stop_hotword()
        self._lib.start_recognizer()

    def on_remote_silence_detected(self):
        print('on_remote_silence_detected')

    def on_final_transcription(self, text):
        print('on_final_transcription: {}'.format(text))

    def on_result(self, text, audio):
        response = json.loads(text)
        print(json.dumps(response, sort_keys=True, indent=4, ensure_ascii=False))

        if audio:
            #os.system('ffplay -autoexit -nodisp -loglevel quiet "{}"'.format(audio))
            os.system('mpv --vid=no "{}"'.format(audio))

        if response['status'] == 'success':
            control = response['content']['dialogue']['control']
            if control == 'start_voice':
                self._lib.start_recognizer()
            else:
                self._lib.start_hotword()

                print(control)
        else:
            self._lib.start_recognizer()
            

    def on_error(self, error_code):
        print('on_error: {}'.format(error_code))
        self._lib.start_hotword()

    def on_local_silence_detected(self):
        print('on_local_silence_detected')


    def start(self):
        self._on_hotword_detected = ON_CALLBACK(self.on_hotword_detected)
        self.hotword_handler = HotwordHandler(self._on_hotword_detected)
        self._lib.add_hotword_handler(pointer(self.hotword_handler))

        self._on_remote_silence_detected = ON_CALLBACK(self.on_remote_silence_detected)
        self._on_final_transcription = ON_FINAL_TRANSCRIPTION(self.on_final_transcription)
        self._on_result = ON_RESULT(self.on_result)
        self._on_error = ON_ERROR(self.on_error)
        self._on_local_silence_detected = ON_CALLBACK(self.on_local_silence_detected)

        self.speech_client_handler = SpeechClientHandler(
             self._on_remote_silence_detected,
             self._on_final_transcription,
             self._on_result,
             self._on_error,
             self._on_local_silence_detected
        )

        self._lib.set_recognizer_handler(pointer(self.speech_client_handler))

        self._lib.start_hotword()

    def stop(self):
        self._lib.stop_hotword()

    def start_recognizer(self):
        self._lib.start_recognizer()

    def stop_recognizer(self):
        self._lib.stop_recognizer()

    def put(self, data):
        self._lib.send_speech_frame(data, len(data))

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.stop()

    def _load_lib(self):
        lib_name = 'libmobvoisdk.so'
        lib_path = os.path.join(os.path.dirname(__file__), 'x86_64', lib_name)
        self._lib = cdll.LoadLibrary(lib_path)

        # void add_hotword_handler(struct hotword_handler_vtable* handlers)
        self._lib.add_hotword_handler.argtypes = [POINTER(HotwordHandler)]
        self._lib.add_hotword_handler.restype = None

        # void remove_hotword_handler(struct hotword_handler_vtable* handlers)
        self._lib.remove_hotword_handler.argtypes = [POINTER(HotwordHandler)]
        self._lib.remove_hotword_handler.restype = None

        # void set_recognizer_handler(struct speech_client_handler_vtable* handlers)
        self._lib.set_recognizer_handler.argtypes = [POINTER(SpeechClientHandler)]
        self._lib.set_recognizer_handler.restype = None

        # int sdk_init()
        self._lib.sdk_init.argtypes = []
        self._lib.sdk_init.restype = c_int

        # void set_vlog_level(int level)
        self._lib.set_vlog_level.argtypes = [c_int]
        self._lib.set_vlog_level.restype = None

        # int send_speech_frame(char * frame, int size)
        self._lib.send_speech_frame.argtypes = [c_char_p, c_int]
        self._lib.send_speech_frame.restype = c_int

        # int start_hotword()
        self._lib.start_hotword.argtypes = []
        self._lib.start_hotword.restype = c_int

        # int stop_hotword()
        self._lib.stop_hotword.argtypes = []
        self._lib.stop_hotword.restype = c_int

        # int start_recognizer()
        self._lib.start_recognizer.argtypes = []
        self._lib.start_recognizer.restype = c_int

        # int stop_recognizer()
        self._lib.stop_recognizer.argtypes = []
        self._lib.stop_recognizer.restype = c_int

        # int cancel_recognizer()
        self._lib.cancel_recognizer.argtypes = []
        self._lib.cancel_recognizer.restype = c_int

        # void set_location(double latitude, double longitude)
        self._lib.set_location.argtypes = [c_double, c_double]
        self._lib.set_location.restype = None

        # void sdk_cleanup()
        self._lib.sdk_cleanup.argtypes = []
        self._lib.sdk_cleanup.restype = None


def main():
    import pyaudio

    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = int(RATE / 100)
    RECORD_SECONDS = 1000

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    with Assistant() as assistant:
        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            try:
                data = stream.read(CHUNK)
                assistant.put(data)
            except KeyboardInterrupt:
                break

    stream.stop_stream()
    stream.close()
    p.terminate()


if __name__ == '__main__':
    main()
