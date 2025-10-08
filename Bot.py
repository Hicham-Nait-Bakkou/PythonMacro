from pynput import keyboard, mouse
import pyautogui
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget
from PyQt5.QtCore import QRunnable, QThreadPool, pyqtSlot
from PyQt5.uic import loadUi
import sys
import json
import UI.images

keys = []
wait_time = 3
macro_path = "macro.txt"
playing = False
settings: dict = {"ExitKey": "f6"}


def on_press(key):
    if hasattr(key, "name"):
        if key == keyboard.Key[settings["ExitKey"]]:
            mouse_listener.stop()
            return False
    elif hasattr(key, "char"):
        if key.char == settings["ExitKey"]:
            mouse_listener.stop()
            return False
    if hasattr(key, "char"):
        print(f'\nkey "{key.char}" pressed')
        if key.char is not None:
            keys.append(key.char + " pressed")
    elif hasattr(key, "name"):
        print(f'\nkey "{key}" pressed')
        if key.name == "cmd" and key.name is not None:
            keys.append("win pressed")
        elif key.name is not None:
            keys.append(key.name + " pressed")


def on_release(key):
    if hasattr(key, "char"):
        print(f'\nkey "{key.char}" released')
        if key.char is not None:
            keys.append(key.char + " released")
    elif hasattr(key, "name"):
        print(f'\nkey "{key}" released')
        if key.name == "cmd" and key.name is not None:
            keys.append("win released")
        elif key.name is not None:
            keys.append(f"{key.name} released")


def on_move(x, y):
    print(f"Pointer moved to {(x, y)}", end="\r")
    if f"Pointer to {x},{y}" not in keys:
        keys.append(f"Pointer to {x},{y}")


def on_click(x, y, button: mouse.Button, pressed):
    print(f"\n{button.name} {'Pressed' if pressed else 'Released'} at {(x, y)}")
    keys.append(f"mouse {button.name} {'pressed' if pressed else 'released'}")


def on_scroll(x, y, dx, dy):
    print(f"\nScrolled {'down' if dy < 0 else 'up'} at {(x, y)}", end="\r")
    keys.append(f"Scrolled {dx}&{dy}")


def on_play_exit(key):
    global playing
    if playing and key == keyboard.Key.f6:
        playing = False


class MainUI(QMainWindow):
    def __init__(self):
        super(MainUI, self).__init__()
        global settings

        loadUi("UI/Bot.ui", self)
        with open("settings.json", "r") as file:
            settings = json.load(file)
        self.threadpool = QThreadPool()
        exit_listener = keyboard.Listener(on_press=on_play_exit)
        exit_listener.start()
        self.recordButton.clicked.connect(self.record_macro)
        self.playButton.clicked.connect(self.play_macro)
        self.actionhotkey.triggered.connect(self.select_hotkey)

    def select_hotkey(self):
        self.hotkeyWindow = PopupWindow()
        self.hotkeyWindow.show()

    def record_macro(self):
        self.recordButton.setEnabled(False)
        self.playButton.setEnabled(False)
        worker1 = Worker(key_func=self.key_listener)
        self.threadpool.start(worker1)

    def play_macro(self):
        global playing
        self.playButton.setEnabled(False)
        self.recordButton.setEnabled(False)
        playing = True
        worker2 = Worker(key_func=self.key_inputer)
        self.threadpool.start(worker2)

    def key_listener(self):
        global mouse_listener

        mouse_listener = mouse.Listener(
            on_move=on_move, on_click=on_click, on_scroll=on_scroll
        )
        mouse_listener.start()

        keyboard_listener = keyboard.Listener(
            on_press=on_press, on_release=on_release)
        keyboard_listener.start()

        keyboard_listener.join()

        print("\n")

        with open(macro_path, "w") as macro:
            for key in keys:
                macro.write(key)
                macro.write("\n")
            print(f"macro at {macro_path} has been created ")
        self.recordButton.setEnabled(True)
        self.playButton.setEnabled(True)

    def key_inputer(self):
        try:
            with open(macro_path, "r") as macro:
                lines = macro.readlines()
                for line in lines:
                    keys.append(
                        line.removeprefix("Pointer to ")
                        .removeprefix("Scrolled ")
                        .removesuffix("\n")
                    )
        except FileNotFoundError:
            print("Macro Not Found")
        except PermissionError:
            print("You Don't have permission to read the macro file")
        if keys != []:
            key: str
            pointer = None
            is_win_pressed = False
            for key in keys:
                if not playing:
                    break
                if key.replace(",", "").isnumeric():
                    pointer = key.split(",", 2)
                    pyautogui.moveTo(int(pointer[0]), int(pointer[1]))
                elif key.replace("&", "").isnumeric():
                    pointer = key.split("&", 2)
                    print(pointer)
                    pyautogui.scroll(int(pointer[0]))
                    pyautogui.hscroll(int(pointer[1]))
                elif key.startswith("mouse"):
                    if key.endswith("pressed"):
                        key = key.removeprefix(
                            "mouse ").removesuffix(" pressed")
                        pyautogui.mouseDown(button=key)
                    elif key.endswith("released"):
                        key = key.removeprefix(
                            "mouse ").removesuffix(" released")
                        pyautogui.mouseUp(button=key)
                elif key.endswith("pressed"):
                    key = key.removesuffix(" pressed")
                    if key == "win":
                        is_win_pressed = True
                    elif is_win_pressed:
                        match key:
                            case "&":
                                key = "1"
                            case "é":
                                key = "2"
                            case '"':
                                key = "3"
                            case "'":
                                key = "4"
                            case "()":
                                key = "5"
                            case "-":
                                key = "6"
                            case "è":
                                key = "7"
                            case "_":
                                key = "8"
                            case "ç":
                                key = "9"
                            case "à":
                                key = "0"
                    pyautogui.keyDown(key, duration=0.1)
                elif key.endswith("released"):
                    key = key.removesuffix(" released")
                    if is_win_pressed:
                        match key:
                            case "&":
                                key = "1"
                            case "é":
                                key = "2"
                            case '"':
                                key = "3"
                            case "'":
                                key = "4"
                            case "()":
                                key = "5"
                            case "-":
                                key = "6"
                            case "è":
                                key = "7"
                            case "_":
                                key = "8"
                            case "ç":
                                key = "9"
                            case "à":
                                key = "0"
                    elif key == "win":
                        is_win_pressed = False
                    pyautogui.keyUp(key, duration=0.1)

            self.recordButton.setEnabled(True)
            self.playButton.setEnabled(True)


class Worker(QRunnable):
    def __init__(self, key_func):
        super().__init__()
        self.key_func = key_func

    @pyqtSlot()
    def run(self):
        self.key_func()


def on_hotkey_press(key):
    if hasattr(key, "char"):
        settings["ExitKey"] = key.char
    elif hasattr(key, "name"):
        settings["ExitKey"] = key.name
    return False


class PopupWindow(QWidget):
    def __init__(self):
        super().__init__()

        loadUi("UI/BotPopup.ui", self)
        self.threadpool = QThreadPool()
        self.hotkeyButton.setText(settings["ExitKey"].capitalize())
        self.hotkeyButton.clicked.connect(self.on_change_hotkey_clicked)

    def hotkeylisten(self):
        hotkey_listener = keyboard.Listener(on_press=on_hotkey_press)
        hotkey_listener.start()
        hotkey_listener.join()
        self.hotkeyButton.setEnabled(True)
        self.hotkeyButton.setText(settings["ExitKey"].capitalize())
        with open("settings.json", "w") as file:
            json.dump(settings, file, indent=3)

    def on_change_hotkey_clicked(self):
        self.hotkeyButton.setEnabled(False)
        self.hotkeyButton.setText("...")
        worker4 = Worker(self.hotkeylisten)
        self.threadpool.start(worker4)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = MainUI()
    ui.show()
    app.exec_()
