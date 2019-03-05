from fluidsynth import Synth, raw_audio_string
import wave
import numpy

channel = 0
pitch = 60
velocity = 80
duration = 1
sampling_rate = 44100

for instrument in range(128):
    synth = Synth(gain = 1)
    sfid = synth.sfload('/Users/hongyu/SoundFonts/timbres of heaven.sf2')
    synth.program_select(channel, sfid, 0, instrument)
    
    synth.noteon(channel, pitch, velocity)
    samples = synth.get_samples(int(duration * sampling_rate))
    synth.noteoff(channel, pitch)
    tails = synth.get_samples(int(duration * 0.2 * sampling_rate))
    samples = numpy.append(samples, tails)
    
    synth.sfunload(1)
    synth.delete()

    fout = wave.open('./sounds/instrument_' + str(instrument).zfill(3) + '.wav', 'wb')
    fout.setnchannels(2)
    fout.setsampwidth(2)
    fout.setframerate(44100)
    fout.writeframes(samples.tostring())
    fout.close()