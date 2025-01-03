import mido
from collections import defaultdict

OneOctave = 12

class MidiNote:
    def __init__(self, tone=0, time=0, duration=0):
        self.tone = tone  # 音高
        self.time = time  # 开始时间
        self.duration = duration  # 持续时间

    def __repr__(self):
        return f"MidiNote(tone={self.tone}, time={self.time}, duration={self.duration})"


class MidiMusic:

    def __init__(self, path):
        self.file_path = path
        self.tracks = []
        self.speed = 1.0
        self.bpm = 0
        self.ticks_per_beat = 0
        self.parseFile()
        self.convertTime()

    def parseFile(self):
        origin_mid = mido.MidiFile(self.file_path)  # 读取 MIDI 文件

        self.ticks_per_beat = origin_mid.ticks_per_beat

        for i, track in enumerate(origin_mid.tracks):
            #print(f"Parsing track {i}: {track.name}")
            current_time = 0
            notes = []  # 用于存储当前音轨的所有音符
            active_notes = {}  # 用于跟踪正在播放的音符

            for msg in track:
                current_time += msg.time  # 更新全局时间
                if msg.type == "note_on" and msg.velocity > 0:
                    # 记录音符开始
                    active_notes[msg.note] = current_time
                elif msg.type == "note_off" or (
                    msg.type == "note_on" and msg.velocity == 0
                ):
                    # 记录音符结束，计算持续时间
                    if msg.note in active_notes:
                        start_time = active_notes.pop(msg.note)
                        duration = current_time - start_time
                        notes.append(
                            MidiNote(tone=msg.note, time=start_time, duration=duration)
                        )
                elif msg.type == "set_tempo" and msg.tempo > 0 and self.bpm == 0:
                    self.bpm = 60 * 1_000_000 / msg.tempo
            if len(notes) != 0:
                self.tracks.append(notes)  # 将音轨添加到总轨道列表

    def convertTime(self):
        # 计算每个 tick 的时长（秒）
        seconds_per_beat = 60  / self.bpm  # 每个节拍的时长（秒）
        seconds_per_tick = seconds_per_beat / self.ticks_per_beat  # 每个 tick 的时长（秒）

        # 遍历所有音轨及其音符，将时间转换为秒
        for track in self.tracks:
            for note in track:
                note.time *= round(seconds_per_tick, 4)  # 转换开始时间为秒
                note.duration *= seconds_per_tick  # 转换持续时间为秒

    def to_time_notes_array(self):
        """
        将所有音轨的音符按时间点整理为二维数组。
        格式：{时间: [按下的音符]}
        """
        time_notes_map = defaultdict(list)

        # 遍历所有轨道和音符
        for track in self.tracks:
            for note in track:
                time_notes_map[note.time].append(note.tone)

        # 按时间点排序并转为列表
        sorted_time_notes = sorted(time_notes_map.items())  # 按时间点排序
        return sorted_time_notes

