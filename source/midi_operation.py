from midi import NoteOnEvent, NoteOffEvent, ProgramChangeEvent
from midi import EndOfTrackEvent, SetTempoEvent, TimeSignatureEvent, KeySignatureEvent
from midi import Pattern, Track, read_midifile, write_midifile

# pitch: number, 60 is middle C
# start: number, measured in the number of beats
# duration: number, measured in the number of beats
# dynamic: number
# channel: number
class Note:
    
    def __init__(self, pitch = 0, start = 0, duration = 0, dynamic = 0, channel = 0):
        self.pitch = pitch
        self.start = start
        self.duration = duration
        self.dynamic = dynamic
        self.channel = channel
        self.revise()
    
    def __str__(self):
        if self.pitch != 0:
            return 'pitch = ' + str(self.pitch) + ', start = ' + str(self.start) + ', duration = ' + str(self.duration) + ', dynamic = ' + str(self.dynamic)
        else:
            return 'rest, start = ' + str(self.start) + ', duration = ' + str(self.duration)
        
    def __cmp__(self, other):
        if self.start < other.start:
            return -1
        elif self.start > other.start:
            return 1
        # if two notes start at the same time, put the higher one ahead 
        elif self.pitch > other.pitch:
            return -1
        elif self.pitch < other.pitch:
            return 1
        else:
            return 0
        
    def copy(self):
        return Note(self.pitch, self.start, self.duration, self.dynamic, self.channel)
    
    def is_rest(self):
        if self.pitch == 0 or self.dynamic == 0:
            return True
        else:
            return False
        
    def revise(self):
        self.pitch = int(self.pitch)
        self.dynamic = int(self.dynamic)
        if self.pitch < 0:
            self.pitch = 0
        if self.pitch > 0 and self.pitch < 12:
            self.pitch = self.pitch + 12
        if self.pitch > 120:
            self.pitch = 108 + (self.pitch % 12)
        if self.start < 0:
            self.start = 0
        if self.duration < 0:
            self.duration = 0
        if self.dynamic < 0:
            self.dynamic = 0
        if self.dynamic > 120:
            self.dynamic = 120
        if self.channel < 0:
            self.channel = 0
        if self.channel > 15:
            self.channel = 15
            
class MIDI:
    default_resolution = 220
    
    # track: track with absolute tick
    # pitch: note pitch, described by integer
    # loudness: note dynamic, described by integer
    # start: absolute time
    # end: absolute time
    @staticmethod
    def add_note_abs(track, pitch, start, end, loudness, channel, resolution = default_resolution):
        MIDI.add_note_on_abs(track, pitch, start, loudness, channel, resolution)
        MIDI.add_note_off_abs(track, pitch, end, channel, resolution)
        return track
    
    # only add note on event
    @staticmethod
    def add_note_on_abs(track, pitch, start, loudness, channel, resolution = default_resolution):
        on = NoteOnEvent(tick = int(resolution * start),
                         channel = channel,
                         velocity = loudness,
                         pitch = pitch)
        track.append(on)
        return track
    
    # only add note off event
    @staticmethod
    def add_note_off_abs(track, pitch, end, channel, resolution = default_resolution):
        off = NoteOffEvent(tick = int(resolution * end), 
                           channel = channel,
                           pitch = pitch)
        track.append(off)
        return track
    
    @staticmethod
    def new_track(tempo = 100):
        track = Track()
        set_tempo_event = SetTempoEvent()
        set_tempo_event.set_bpm(tempo)
        track.append(set_tempo_event)
        return track
    
    @staticmethod
    def new_pattern():
        return Pattern(resolution = MIDI.default_resolution)
    
    # assume the melody track is located before the harmony track
    # find the first track where the note on event exists
    @staticmethod
    def read_melody(path):
        if path.endswith('.mid') or path.endswith('.midi'):
            pattern = read_midifile(path)
        else:
            pattern = read_midifile(path + '.mid')
        
        index = 0
        found = False
        while True:
            for event in pattern[index]:
                if type(event) is NoteOnEvent and event.channel != 9:
                    found = True
                    break
            if found == True:
                break
            index = index + 1
        
        if index == len(pattern):
            return (Track(), 220)
        else:
            return (pattern[index], pattern.resolution)
    
    @staticmethod
    def list_notes(track, resolution = default_resolution):
        notes = []
        key_status = {}
        current_tick = 0
        for event in track:
            if (type(event) is NoteOnEvent or type(event) is NoteOffEvent) and event.channel == 9:
                continue
            if type(event) is NoteOnEvent and event.data[0] != 0 and event.data[1] != 0:
                current_tick += event.tick
                pitch = event.data[0]
                dynamic = event.data[1]
                key_status[pitch] = {'pressed': True, 
                                     'start': MIDI.quantify(float(current_tick) / float(resolution)),
                                     'dynamic': dynamic}
            else:
                note_off_condition_1 = type(event) is NoteOffEvent and event.data[0] != 0
                note_off_condition_2 = type(event) is NoteOnEvent and event.data[0] != 0 and event.data[1] == 0
                if note_off_condition_1 or note_off_condition_2:
                    current_tick += event.tick
                    pitch = event.data[0]
                    if key_status.has_key(pitch) and key_status[pitch]['pressed'] == True:
                        start = MIDI.quantify(key_status[pitch]['start'])
                        duration = MIDI.quantify(float(current_tick) / float(resolution) - start)
                        note = Note(pitch = pitch, 
                                    start = start,
                                    duration = duration,
                                    dynamic = key_status[pitch]['dynamic'])
                        key_status[pitch]['pressed'] = False
                        key_status[pitch]['start'] = 0
                        key_status[pitch]['dynamic'] = 0
                        if note.duration != 0:
                            notes.append(note)
                # rest note
                else:
                    start = MIDI.quantify(float(current_tick) / float(resolution))
                    duration = MIDI.quantify(float(event.tick) / float(resolution))
                    current_tick += event.tick
                    note = Note(pitch = 0, start = start, duration = duration, dynamic = 0)
                    if note.duration != 0:
                        notes.append(note)
        return notes
    
    @staticmethod
    def quantify(time):
        return round(time * 24) / 24

    # write the generated music score
    @staticmethod
    def write_patterns(path, patterns, unit, tonalities, instruments):
        
        if len(patterns) == 0:
            return
        keys = patterns.keys()
        keys.sort()
        resolution = patterns[keys[0]].resolution
        pattern = Pattern(resolution = resolution)
        
        last_index = -1
        key_signature_map = [0, -5, 2, -3, 4, -1, -6, 1, -4, 3, -2, 5]
        for excerpt_index in keys:
            excerpt = patterns[excerpt_index]
            # if there is no note event, then ignore that bar
            has_note_event = False
            for track in excerpt:
                for event in track:
                    if type(event) is NoteOnEvent or type(event) is NoteOffEvent:
                        has_note_event = True
                        break
                if has_note_event == True:
                    break
            if has_note_event == False:
                continue
            
            for track_index in range(len(excerpt)):
                if len(pattern) <= track_index:
                    new_track = Track(tick_relative = False)
                    pattern.append(new_track)
                    
                    time_signature = TimeSignatureEvent()
                    denominator = 4
                    numerator = unit
                    while abs(round(numerator) - numerator) >= 1.0 / 24.0 and numerator <= 16:
                        denominator *= 2
                        numerator *= 2
                    time_signature.set_denominator(denominator)
                    time_signature.set_numerator(int(round(numerator)))
                    time_signature.tick = 0
                    new_track.append(time_signature)
                    
                if last_index == -1 or \
                   tonalities[excerpt_index]['mode'] != tonalities[last_index]['mode'] or \
                   tonalities[excerpt_index]['key'] != tonalities[last_index]['key']:                
                    key_signature = KeySignatureEvent()
                    if tonalities[excerpt_index]['mode'] == 'Major':
                        value = key_signature_map[tonalities[excerpt_index]['key']]
                        minor = 0
                    else:
                        value = key_signature_map[(tonalities[excerpt_index]['key'] + 3) % 12]
                        minor = 1
                    key_signature.set_alternatives(value)
                    key_signature.set_minor(minor)
                    key_signature.tick = int(excerpt_index * unit * resolution)
                    pattern[track_index].append(key_signature)
                
                num_instruments = len(instruments[excerpt_index])
                current_instrument_id = instruments[excerpt_index][min(track_index, num_instruments - 1)]['ID']
                if last_index != -1:
                    last_instrument_id = instruments[last_index][min(track_index, num_instruments - 1)]['ID']
                if last_index == -1 or current_instrument_id != last_instrument_id:
                    program_change = ProgramChangeEvent()
                    program_change.set_value(current_instrument_id)
                    program_change.tick = int(excerpt_index * unit * resolution)
                    program_change.channel = track_index
                    pattern[track_index].append(program_change)
                    
                track = excerpt[track_index]
                track.make_ticks_abs()
                for event in track:
                    new_event = MIDI.copy_event(event)
                    new_event.tick = int(event.tick) + int(excerpt_index * unit * resolution)
                    pattern[track_index].append(new_event)
                track.make_ticks_rel()
            last_index = excerpt_index
        
        for track in pattern:
            track.sort()
            track.make_ticks_rel()
            track.append(EndOfTrackEvent(tick = resolution))
        MIDI.write_pattern(path, pattern)
    
    @staticmethod
    def write_pattern(path, pattern):
        if path.endswith('.mid'):
            write_midifile(path, pattern)
        else:
            write_midifile(path + '.mid', pattern)
        return
    
    @staticmethod
    def copy_event(event):
        if type(event) is SetTempoEvent:
            new_event = SetTempoEvent()
            new_event.tick = event.tick
            new_event.data[0] = event.data[0]
            new_event.data[1] = event.data[1]
            new_event.data[2] = event.data[2]
            return new_event
        elif type(event) is NoteOnEvent:
            new_event = NoteOnEvent()
            new_event.tick = event.tick
            new_event.channel = event.channel
            new_event.data[0] = event.data[0]
            new_event.data[1] = event.data[1]
            return new_event
        elif type(event) is NoteOffEvent:
            new_event = NoteOffEvent()
            new_event.tick = event.tick
            new_event.channel = event.channel
            new_event.data[0] = event.data[0]
            new_event.data[1] = event.data[1]
            return new_event
        elif type(event) is ProgramChangeEvent:
            new_event = ProgramChangeEvent
            new_event.tick = event.tick
            new_event.channel = event.channel
            new_event.data[0] = event.data[0]
            return new_event
        else:
            raise('Not Supported')
        
    @staticmethod
    def copy_track(original_track, channel_offset = 1, default_tempo = 100):
        set_tempo_event = SetTempoEvent()
        set_tempo_event.set_bpm(default_tempo)
        for event in original_track:
            if type(event) is SetTempoEvent:
                set_tempo_event = event
        
        new_track = Track(events = [MIDI.copy_event(set_tempo_event)], tick_relative = True)
        for event in original_track:
            if type(event) is NoteOnEvent or type(event) is NoteOffEvent:
                copied_event = MIDI.copy_event(event)
                copied_event.channel += channel_offset
                new_track.append(copied_event)
        return new_track
        
    @staticmethod
    def separate_track(original_track, num_track = 1, default_tempo = 100):
        set_tempo_event = SetTempoEvent()
        set_tempo_event.set_bpm(default_tempo)
        original_track.make_ticks_abs()
        channel_set = set()
        for event in original_track:
            if type(event) is NoteOnEvent or type(event) is NoteOffEvent:
                channel_set.add(event.channel)
            if type(event) is SetTempoEvent:
                set_tempo_event = event
        
        channel_track_map = {}
        index = 0
        for channel in channel_set:
            channel_track_map[channel] = index
            index += 1
        
        tracks = []
        for i in range(max(num_track, len(channel_set))):
            tracks.append(Track(events = [MIDI.copy_event(set_tempo_event)], tick_relative = False))
        
        for event in original_track:
            if type(event) is NoteOnEvent or type(event) is NoteOffEvent:
                copied_event = MIDI.copy_event(event)
                tracks[channel_track_map[copied_event.channel]].append(copied_event)
        
        for track in tracks:
            track.sort()
            track.make_ticks_rel()
        
        original_track.make_ticks_rel()
        return tracks