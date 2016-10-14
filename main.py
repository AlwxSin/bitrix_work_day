import sys

from bitrix import Bitrix


if __name__ == '__main__':
    action = sys.argv[1]
    try:
        headless = sys.argv[2] and False
    except IndexError:
        headless = True

    b = Bitrix(headless=headless)
    if action == 'close':
        print('Closing day')
        b.close_day()
    elif action == 'open':
        print('Open day')
        b.open_day()
    else:
        print('wrong arguments')
    sys.exit()
