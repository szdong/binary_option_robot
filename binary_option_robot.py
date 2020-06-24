import pyautogui
import pyperclip
from binance.websockets import BinanceSocketManager
from binance.client import Client
from pygame import mixer
import json

price_que = []
volume_que = []
wam_avg = 0
simple_avg = 0
volume_wam_avg = 0
position_count = 0
position_b = 0
position_s = 0
buy_position = 0
sell_position = 0
counter = None
color = "y"


delta = 3  # 价格大于or小于平均价多少下单
que_number = 200  # 统计过去多少个tick
max_position = 1  # 最多开几单
lot = 2  #  每次开几张
two_way = False  # 如果有不同方向的信号，能不能开
judge_way = 2 # 0: wam_avg, 1: simple_avg, 2: volume_wam_avg
monitor_mode = True  # 是否开启监视模式（监视模式不会触发下单，只会喊单）

if monitor_mode:
    mixer.init()



class pycolor:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    COLOR_DEFAULT = '\033[39m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    INVISIBLE = '\033[08m'
    REVERCE = '\033[07m'
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    BG_DEFAULT = '\033[49m'
    END = '\033[0m'


def order(text: str):
    pyautogui.FAILSAFE = True

    defalut_lot = "1"

    # 买入按钮的坐标
    buy_xy = {
        "x": 2405,
        "y": 620
    }

    # 卖出按钮的坐标
    sell_xy = {
        "x": 2400,
        "y": 692
    }

    # 输入张数的坐标
    amount_xy = {
        "x": 2344,
        "y": 476
    }

    # 浏览器上任意一处空白处的坐标
    blank_xy = {
        "x": 2404,
        "y": 828
    }

    try:
        if text[0] == "b":
            if len(text) == 1:
                pyautogui.click(amount_xy["x"], amount_xy["y"], button='left')
                pyautogui.click(amount_xy["x"], amount_xy["y"], button='left')
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.hotkey('ctrl', 'c')
                # Mac OS
                # pyautogui.hotkey('command', 'a')
                # pyautogui.hotkey('command', 'c')

                if pyperclip.paste() != defalut_lot:
                    pyautogui.click(amount_xy["x"], amount_xy["y"], button='left')
                    pyautogui.hotkey('ctrl', 'a')
                    # Mac OS
                    # pyautogui.hotkey('command', 'a')
                    pyautogui.typewrite(defalut_lot)

                pyautogui.click(blank_xy["x"], blank_xy["y"], button='left')
                pyautogui.click(buy_xy["x"], buy_xy["y"], button='left')
            else:
                if text[1:].isdigit:
                    pyautogui.click(amount_xy["x"], amount_xy["y"], button='left')
                    pyautogui.click(amount_xy["x"], amount_xy["y"], button='left')
                    pyautogui.hotkey('ctrl', 'a')
                    # Mac OS
                    # pyautogui.hotkey('command', 'a')
                    pyautogui.typewrite(text[1:])
                    pyautogui.click(blank_xy["x"], blank_xy["y"], button='left')
                    pyautogui.click(buy_xy["x"], buy_xy["y"], button='left')
        elif text[0] == "s":
            if len(text) == 1:
                pyautogui.click(amount_xy["x"], amount_xy["y"], button='left')
                pyautogui.click(amount_xy["x"], amount_xy["y"], button='left')
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.hotkey('ctrl', 'c')
                # Mac OS
                # pyautogui.hotkey('command', 'a')
                # pyautogui.hotkey('command', 'c')
                if pyperclip.paste() != defalut_lot:
                    pyautogui.click(amount_xy["x"], amount_xy["y"], button='left')
                    pyautogui.hotkey('ctrl', 'a')
                    # Mac OS
                    # pyautogui.hotkey('command', 'a')
                    pyautogui.typewrite(defalut_lot)

                pyautogui.click(blank_xy["x"], blank_xy["y"], button='left')
                pyautogui.click(sell_xy["x"], sell_xy["y"], button='left')
            else:
                if text[1:].isdigit:
                    pyautogui.click(amount_xy["x"], amount_xy["y"], button='left')
                    pyautogui.click(amount_xy["x"], amount_xy["y"], button='left')
                    pyautogui.hotkey('ctrl', 'a')
                    # Mac OS
                    # pyautogui.hotkey('command', 'a')
                    pyautogui.typewrite(text[1:])
                    pyautogui.click(blank_xy["x"], blank_xy["y"], button='left')
                    pyautogui.click(sell_xy["x"], sell_xy["y"], button='left')

        # pyautogui.hotkey('alt', 'tab')

        # Mac OS
        # pyautogui.hotkey('command', 'tab')

    except Exception as e:
        print(e)

# 加权平均
def wam(lst):
    n = len(lst)
    weight = 0.5 * (n + 1)
    weight_sum = 0
    for i in range(n):
        weight_sum += lst[i] * ((i + 1) / n)

    return weight_sum / weight


# 成交量加权平均
def volume_wam(price_lst, volume_lst):
    n = len(price_lst)
    weight = sum(volume_lst)
    weight_sum = 0
    for i in range(n):
        weight_sum += price_lst[i] * volume_lst[i]

    return weight_sum / weight


def process_m_message(msg):
    global wam_avg, price_que, position_count, volume_wam_avg, simple_avg, buy_position, sell_position, counter
    global position_b, position_s, color

    print("stream: {}".format(msg['stream']))
    print(json.dumps(msg['data'], indent=4))

    if len(price_que) >= que_number:
        if msg['data']['E'] % 60000 < 50000:
            if msg['data']['m'] == False:
                if float(msg['data']['p']) - counter >= delta:
                    if position_b < max_position:
                        if monitor_mode == False:
                            if lot == 1:
                                order('b')
                            else:
                                order("b{}".format(lot))
                        position_count += 1
                        buy_position += 1
                        color = 'g'
                        print(pycolor.GREEN + "BUY" + pycolor.END)
                        if monitor_mode:
                            mixer.music.load("buy.mp3")
                            mixer.music.play(1)
                    color = 'g'
                else:
                    color = 'y'
            else:
                if counter - float(msg['data']['p']) >= delta:
                    if position_s < max_position:
                        if monitor_mode == False:
                            if lot == 1:
                                order('s')
                            else:
                                order("s{}".format(lot))
                        position_count += 1
                        sell_position += 1
                        print(pycolor.RED + "SELL" + pycolor.END)
                        if monitor_mode:
                            mixer.music.load("sell.mp3")
                            mixer.music.play(1)
                    color = 'r'
                else:
                    color = 'y'
        else:
            position_count = 0
            buy_position = 0
            sell_position = 0

        price_que.pop(0)
        volume_que.pop(0)

    price_que.append(float(msg['data']['p']))
    volume_que.append(float(msg['data']['q']))
    wam_avg = wam(price_que)
    simple_avg = sum(price_que) / len(price_que)
    volume_wam_avg = volume_wam(price_que, volume_que)

    if judge_way == 0:
        counter = wam(price_que)
    elif judge_way == 1:
        counter = sum(price_que) / len(price_que)
    elif judge_way == 2:
        counter = volume_wam(price_que, volume_que)

    if two_way:
        position_b, position_s = buy_position, sell_position
    else:
        position_b, position_s = position_count, position_count


    print("============WAM:{0}=====".format(round(wam_avg, 5)))
    print("=====Simple_AVG:{0}=====".format(round(simple_avg, 5)))
    print("=====Volume_WAM:{0}=====".format(round(volume_wam_avg, 5)))
    if color == 'y':
        print(pycolor.YELLOW + "==========Delta:{0}=====".format(round(abs(volume_wam_avg - float(msg['data']['p'])), 5)) + pycolor.END)
    elif color == 'g':
        print(pycolor.GREEN + "==========Delta:{0}=====".format(round(abs(volume_wam_avg - float(msg['data']['p'])), 5)) + pycolor.END)
    elif color == 'r':
        print(pycolor.RED + "==========Delta:{0}=====".format(round(abs(volume_wam_avg - float(msg['data']['p'])), 5)) + pycolor.END)
    print("=======Que Size:{0}=====".format(len(price_que)))


def main():
    # Binance API
    api_key = ""
    api_secret = ""

    if monitor_mode == False:
        blank_xy = {
            "x": 2404,
            "y": 828
        }

        pyautogui.click(blank_xy["x"], blank_xy["y"], button='left')

    client = Client(api_key=api_key, api_secret=api_secret)

    bm = BinanceSocketManager(client)
    conn_key = bm.start_multiplex_socket(['btcusdt@trade'], process_m_message)
    bm.start()


if __name__ == "__main__":
    main()

