import pyautogui
import pyperclip
from binance.websockets import BinanceSocketManager
from binance.client import Client

delta = 2

avg = 0
position_count = 0
que_number = 100
price_que = []

max_position = 5

def order(text: str):
    pyautogui.FAILSAFE = True

    defalut_lot = "1"

    buy_xy = {
        "x": 2405,
        "y": 620
    }

    sell_xy = {
        "x": 2400,
        "y": 692
    }

    amount_xy = {
        "x": 2344,
        "y": 476
    }

    # while True:
    try:
        # text = input("Command: ")
        if text[0] == "b":
            if len(text) == 1:
                pyautogui.click(amount_xy["x"],amount_xy["y"],button='left')
                pyautogui.click(amount_xy["x"],amount_xy["y"],button='left')
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.hotkey('ctrl', 'c')
                # Mac OS
                # pyautogui.hotkey('command', 'a')
                # pyautogui.hotkey('command', 'c')

                if pyperclip.paste() != defalut_lot:
                    pyautogui.click(amount_xy["x"],amount_xy["y"],button='left')
                    pyautogui.hotkey('ctrl', 'a')
                    # Mac OS
                    # pyautogui.hotkey('command', 'a')
                    pyautogui.typewrite(defalut_lot)

                pyautogui.click(buy_xy["x"],buy_xy["y"],button='left')
            else:
                if text[1:].isdigit:
                    pyautogui.click(amount_xy["x"],amount_xy["y"],button='left')
                    pyautogui.click(amount_xy["x"],amount_xy["y"],button='left')
                    pyautogui.hotkey('ctrl', 'a')
                    # Mac OS
                    # pyautogui.hotkey('command', 'a')
                    pyautogui.typewrite(text[1:])
                    pyautogui.click(buy_xy["x"],buy_xy["y"],button='left')
        elif text[0] == "s":
            if len(text) == 1:
                pyautogui.click(amount_xy["x"],amount_xy["y"],button='left')
                pyautogui.click(amount_xy["x"],amount_xy["y"],button='left')
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.hotkey('ctrl', 'c')
                # Mac OS
                # pyautogui.hotkey('command', 'a')
                # pyautogui.hotkey('command', 'c')
                if pyperclip.paste() != defalut_lot:
                    pyautogui.click(amount_xy["x"],amount_xy["y"],button='left')
                    pyautogui.hotkey('ctrl', 'a')
                    # Mac OS
                    # pyautogui.hotkey('command', 'a')
                    pyautogui.typewrite(defalut_lot)

                pyautogui.click(sell_xy["x"],sell_xy["y"],button='left')
            else:
                if text[1:].isdigit:
                    pyautogui.click(amount_xy["x"],amount_xy["y"],button='left')
                    pyautogui.click(amount_xy["x"],amount_xy["y"],button='left')
                    pyautogui.hotkey('ctrl', 'a')
                    # Mac OS
                    # pyautogui.hotkey('command', 'a')
                    pyautogui.typewrite(text[1:])
                    pyautogui.click(sell_xy["x"],sell_xy["y"],button='left')
        
        pyautogui.hotkey('alt', 'tab')

        # Mac OS
        # pyautogui.hotkey('command', 'tab')

    except Exception as e:
        print(e)


def process_m_message(msg):
    global avg, price_que, position_count

    print("stream: {} data: {}".format(msg['stream'], msg['data']))
    

    if len(price_que) >= que_number:
        if msg['data']['E'] % 60000 < 50000:
            if msg['data']['m'] == False:
                if float(msg['data']['p']) - avg >= delta:
                    if position_count < max_position:
                        order('b')
                        position_count += 1
            else:
                if avg - float(msg['data']['p']) >= delta:
                    if position_count < max_position:
                        order('s')
                        position_count += 1
        else:
            position_count = 0
        
        price_que.pop(0)
    
    price_que.append(float(msg['data']['p']))
    avg = sum(price_que) / len(price_que)


def main():
    # Binance API
    api_key = ""
    api_secret = ""

    client = Client(api_key=api_key, api_secret=api_secret)

    bm = BinanceSocketManager(client)
    conn_key = bm.start_multiplex_socket(['btcusdt@trade'], process_m_message)
    bm.start()


if __name__ == "__main__":
    main()
