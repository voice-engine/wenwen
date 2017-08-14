Python版`你好问问`
================

极简的语音交互应用，采用ctypes封装出门问问Linux SDK，支持“你好问问”热词唤醒。

### 依赖
+ pyaudio
+ mpv (或ffplay，在代码里把mpv切换为ffplay)

### 运行
```
sudo apt-get install mpv python-pyaudio
git clone https://github.com/voice-engine/wenwen.git
cd wenwen
LD_LIBRARY_PATH=x86_64 python assistant.py
```

>`LD_LIBRARY_PATH=x86_64`是设置依赖的动态链接库位置

运行成功后，用”你好问问“唤醒，然后语音对话。

### 说明
出门问问Linux SDK来自http://ai.chumenwenwen.com/pages/document/intro。

目前，只支持x86_64(在Ubuntu 16.04 x86_64上测试的)，ARM版和MIPS版没有在Raspberry Pi 3（Raspbian）和MT7688（ReSpeaker Core，OpenWrt 15.05）上运行成功，出门问问居然不说明SDK的编译环境和工具链，特地去问也没告诉！-_-
