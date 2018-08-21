// Copyright 2016 Mobvoi Inc. All Rights Reserved.

#ifndef SPEECH_SDK_H_
#define SPEECH_SDK_H_

#ifdef __cplusplus
extern "C" {
#endif

typedef struct hotword_handler_vtable hotword_handler_vtable;
typedef struct speech_client_handler_vtable speech_client_handler_vtable;

struct hotword_handler_vtable {
  void (*on_hotword_detected)();
};

struct speech_client_handler_vtable {
  /**
   * Callback when remote silence detected.
   */
  void (*on_remote_silence_detected)();

  /**
   * The final result, for example, the "what's the weather" is a partial transcription of query
   * "what's the weather today?", and "what's the weather today?" is final result.
   *
   * @param result The final result.
   */
  void (*on_final_transcription)(const char * result);

  /**
   * The search response.
   *
   * @param result The search response.
   */
  void (*on_result)(const char * result, const char* tts);

  /**
   * Callback when error happen.
   *
   * @param error_code The error code.
   */
  void (*on_error)(int error_code);

  /**
   * Callback when local silence detected.
   */
  void (*on_local_silence_detected)();
};

enum error_code {
  NO_ERROR = 0,
  SERVER_ERROR = 1,
  NETWORK_ERROR = 2,
  AUDIO_ERROR = 3,
  NO_SPEECH = 4,
  INTERNAL_ERROR = 5,
};

typedef struct {
  double latitude;
  double longitude;
} simple_location;

void add_hotword_handler(struct hotword_handler_vtable* handlers);
void remove_hotword_handler(struct hotword_handler_vtable* handlers);
void set_recognizer_handler(struct speech_client_handler_vtable* handlers);

int sdk_init();
void set_vlog_level(int level);
int send_speech_frame(char * frame, int size);
int start_hotword();
int stop_hotword();
int start_recognizer();
int stop_recognizer();
int cancel_recognizer();
void set_location(double latitude, double longitude);
void sdk_cleanup();

#ifdef __cplusplus
}
#endif

#endif  // SPEECH_SDK_H_
