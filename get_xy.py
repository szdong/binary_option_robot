import pyautogui
import pyperclip


def get_xy():
    pyautogui.FAILSAFE = True
    print(pyautogui.position())


if __name__ == "__main__":
    get_xy()
