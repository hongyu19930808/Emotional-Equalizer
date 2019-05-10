from os import listdir
from wave import open as waveopen
from fluidsynth import raw_audio_string
from numpy import zeros
from struct import unpack


def read_samples(path_str):
    wavefile = waveopen(path_str, 'r')
    num_frames = wavefile.getnframes()
    frame_rate = wavefile.getframerate()
    channels = wavefile.getnchannels()
    samples = zeros(num_frames * 2)
    all_value_str = wavefile.readframes(num_frames)
    for i in xrange(num_frames):
        left = all_value_str[i*4:i*4+2]
        right = all_value_str[i*4+2:i*4+4]
        value_left = unpack('h', left)[0]
        value_right = unpack('h', right)[0]
        samples[i*2] = value_left
        samples[i*2+1] = value_right
    wavefile.close()
    return samples

def add_fade_in_fade_out(samples):
    len_sample = len(samples)
    index = len_sample - 2
    while True:
        if abs(samples[index]) > 10 or abs(samples[index+1]) > 10:
            break
        else:
            index -= 2
    len_sample_refined = index + 2
    samples = samples[:len_sample_refined]
    for i in xrange(44100 * 2):
        samples[i] = int(samples[i] * int(i / 2) / 44100.0)
        samples[len_sample_refined - i - 1] = int(samples[len_sample_refined - i - 1] * int(i / 2) / 44100.0)
    return samples

def main():
    path_dir = '/Users/hongyu/Desktop/Test/excerpts/'
    output_dir = '/Users/hongyu/Desktop/Test/excerpts-refined/'
    filenames = listdir(path_dir)
    for name in filenames:
        if name.endswith('.wav'):
            samples = read_samples(path_dir + name)
            samples = add_fade_in_fade_out(samples)
            fout = waveopen(output_dir + name, 'w')
            fout.setframerate(44100)
            fout.setnchannels(2)
            fout.setsampwidth(2)
            fout.writeframes(raw_audio_string(samples))
            fout.close()
    return

if __name__ == '__main__':
    main()
