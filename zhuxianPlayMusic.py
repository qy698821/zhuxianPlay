import time
import ParseMidiFIle as MidiParse
from pynput.keyboard import Controller
import tkinter
from tkinter import *
from tkinter import ttk
import os
import _thread

# 键盘控制器实例
keyboard = Controller()


# 音符到按键的映射(诛仙只支持C3 - B5的全音，差评！)
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

Auto_upDownKey = 1
# 0表示已经停止，1表示正在播放，2表示准备停止
matchine_state = 0
file_floder = "midiFiles/"


def load_midi_files(directory):
    """读取指定目录下的所有 .mid 文件"""
    try:
        return [f for f in os.listdir(directory) if f.endswith(".mid")]
    except FileNotFoundError:
        return []

def begin_playing(filePath):
    global Auto_upDownKey
    test_midi_music = MidiParse.MidiMusic(filePath)
    if Auto_upDownKey == 1:
        adjust_average_pitch(test_midi_music)
    test_time_dic = test_midi_music.to_time_notes_array()
    # 调用函数模拟演奏
    simulate_playing(test_time_dic, note_to_key)

# 模拟演奏
def simulate_playing(time_notes_array, note_to_key):
    global matchine_state
    last_time = 0

    for currenttime, notes in time_notes_array:
        # 计算到下一个音符的等待时间

        if matchine_state == 2:
            break

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

    matchine_state = 0



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
            note.tone += shift * 12  # 调整音符的音高（一个八度有12个音哦~）

    return midi_data

def CreateWindow(file_list):
    def on_check():
        global Auto_upDownKey
        Auto_upDownKey = var

    def on_select(event):
        """当选择下拉框中的文件时，打印选中的文件名"""
        selected_file = combo.get()
        print(f"选中的文件: {selected_file}")

    def begin():
        global file_floder
        global matchine_state
        time.sleep(2)
        if matchine_state == 0:
            matchine_state = 1
            file_path = file_floder + combo.get()
            _thread.start_new_thread(begin_playing, (file_path,))


    def stop():
        global matchine_state
        if matchine_state == 1:
            matchine_state = 2
        

    def Cancel():
        global matchine_state
        matchine_state = 2
        top.destroy()


    top = tkinter.Tk()
    top.title("残月十四的演奏器~~")
    top.geometry("300x300")
    confirm = Button(top,text ="开始演奏",command = begin)
    pause = Button(top,text ="停止演奏",command = stop)
    cancel = Button(top,text ="关闭",command = Cancel)

    var = tkinter.IntVar(value=1)
    check = tkinter.Checkbutton(top, text="自动调整音域", variable=var, command=on_check)
    combo = ttk.Combobox(top, values=file_list)
    combo.set("请选择一个 MIDI 文件")  # 设置默认值
    combo.bind("<<ComboboxSelected>>", on_select)
    combo.pack(pady=20)
    check.pack(pady=20)
    confirm.pack()
    pause.pack()
    cancel.pack()
    top.mainloop()

if __name__ == "__main__":
    file_floder = "midiFiles/"
    midi_files = load_midi_files(file_floder)
    CreateWindow(midi_files)
    
