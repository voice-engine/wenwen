

import subprocess
import types
import wave


def play(data, rate=16000, channels=1, width=2):
    """
    play raw audio (string or generator)
    Args:
        data: raw audio data, str or iterator
        rate: sample rate, only for raw audio
        channels: channel number, only for raw data
        width: raw audio data width, 16 bit is 2, only for raw data
    """
    format_list = (None, 'S8', 'S16_LE', 'S24_LE', 'S32_LE')
    command = 'aplay -c {} -r {} -f {} -'.format(channels, rate, format_list[width])
    
    p = subprocess.Popen(command, stdin=subprocess.PIPE, shell=True)
    if isinstance(data, types.GeneratorType):
        for d in data:
            p.stdin.write(d)
    else:
        p.stdin.write(data)

    p.stdin.close()


def play_wav(wav):
    f = wave.open(wav, 'rb')
    rate = f.getframerate()
    channels = f.getnchannels()
    width = f.getsampwidth()

    def gen(w):
        d = w.readframes(1024)
        while d:
            yield d
            d = w.readframes(1024)
        w.close()

    data = gen(f)

    play(data, rate, channels, width)



def main():
    import sys

    if len(sys.argv) < 2:
        print('Usage: python {} music.wav'.format(sys.argv[0]))
        sys.exit(1)

    play_wav(sys.argv[1])


if __name__ == '__main__':
    main()
