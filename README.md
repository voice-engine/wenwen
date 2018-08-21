Python版`你好问问`
================

极简的语音交互应用，采用ctypes封装出门问问Linux SDK，目前（2018-8-21）是1.2.0版，支持“你好问问”热词唤醒，支持离线语音识别。

### 依赖
+ arecord
+ [voice-engine](https://github.com/voice-engine/voice-engine.git)

### 运行
1. 安装`voice-engine`，下载代码

   ```
   sudo pip install voice-engine
   git clone https://github.com/voice-engine/wenwen.git
   cd wenwen
   ```
2. 下载[出门问问Linux SDK](https://ai.chumenwenwen.com/pages/document/intro?id=download)，把压缩包中`lib`和`.mobvoi`解压到`wenwen`目录

   ```
    wenwen
    ├── .mobvoi
    ├── lib
    ├── assistant.py
    ├── offline.py
    └── player.py
   ```
3. 离线模式，运行`python offline.py`离线识别“开灯”、“关灯”、“播放音乐”等语音命令
4. 在线模式，在https://ai.chumenwenwen.com，注册出门问问开发者帐号，创建一个应用，获得应用的KEY，并填入`wenwen/assistan.py`
5. 运行`python wenwen/assistant.py`，用”你好问问“唤醒，然后语音对话。

### 代码示例
```python
import time
from assistant import Assistant
from voice_engine.source import Source

# TODO: Get a key from https://ai.chumenwenwen.com
KEY = ''

def main():
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
```

### 说明
出门问问Linux SDK来自http://ai.chumenwenwen.com/pages/document/intro。


