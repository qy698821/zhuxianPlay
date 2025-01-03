import time
import ParseMidiFIle as MidiParse
from pynput.keyboard import Controller

# 键盘控制器实例
keyboard = Controller()

# 音符到按键的映射
note_to_key = {
    48: "a",
    50: "s",
    52: "d",
    53: "f",
    55: "g",
    57: "h",
    59: "j",  # C3 - B3
    60: "q",
    62: "w",
    64: "e",
    65: "r",
    67: "t",
    69: "y",
    71: "u",  # C4 - B4
    72: "1",
    74: "2",
    76: "3",
    77: "4",
    79: "5",
    81: "6",
    83: "7",  # C5 - B5
}


# 模拟演奏
def simulate_playing(time_notes_array, note_to_key):
    last_time = 0

    for currenttime, notes in time_notes_array:
        # 计算到下一个音符的等待时间
        wait_time = currenttime - last_time
        if wait_time > 0:
            time.sleep(wait_time)  # 等待到下一个时间点

        # 模拟按键
        for note in notes:
            if note in note_to_key:
                key = note_to_key[note]
                keyboard.press(key)
                keyboard.release(key)  # 模拟按下和释放
                print(f"Played: {key} (Note: {note})")

        last_time = currenttime


def adjust_average_pitch(midi_data):
    """
    计算整个乐曲的平均音高，并将其调整到 C4 - B4 (MIDI 60-71) 范围。
    """
    total_notes = 0
    total_tone = 0  # 用于计算音符的平均音高

    # 统计所有音符的数量和音高
    for track in midi_data.tracks:
        for note in track:
            total_notes += 1
            total_tone += note.tone

    # 计算音符的平均音高
    average_tone = total_tone / total_notes
    print(f"平均音高: {average_tone}")

    # 计算需要升降几个八度
    shift = 0
    if average_tone < 60:  # 平均音高低于C4，需要升高
        shift = (60 - average_tone) // 12 + 1  # 计算需要升高的八度数
    elif average_tone > 71:  # 平均音高高于B4，需要降低
        shift = (average_tone - 71) // 12 + 1  # 计算需要降低的八度数

    print(f"需要调整的八度数: {shift}")

    # 根据计算出的shift，统一调整音符的音高
    for track in midi_data.tracks:
        for note in track:
            note.tone += shift * 12  # 调整音符的音高

    return midi_data


time.sleep(2)
test_midi_music = MidiParse.MidiMusic("midiFiles/晴天.mid")
adjust_average_pitch(test_midi_music)
test_time_dic = test_midi_music.to_time_notes_array()
# 调用函数模拟演奏
simulate_playing(test_time_dic, note_to_key)
