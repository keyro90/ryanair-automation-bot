import logging
import sys
from logging.handlers import RotatingFileHandler
from time import sleep

import telegram

from common.configuration import gc
from tours.AutoreisenNavigation import AutoreisenNavigation
from tours.RyanairNavigation import RyanairNavigation

logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.DEBUG)
fh = RotatingFileHandler('main.log', mode='w+', maxBytes=5 * 1024 * 1024, backupCount=2, encoding=None, delay=False)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
sh.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(sh)


def send(msg, chat_id, token):
    bot = telegram.Bot(token=token)
    bot.sendMessage(chat_id=chat_id, text=msg)


def send_keys_delay(elem, text, secs: float = 0):
    for c in text:
        elem.send_keys(c)
        sleep(secs)


def start_ryanair(start_wanted_str, end_wanted_str, departure, destination):
    ryan_tour = RyanairNavigation(start_wanted_str, end_wanted_str, departure, destination)
    price_start, price_end, fares_dep, fares_dest = ryan_tour.run()
    for p in gc['chat_ids'].split(","):
        send(
            f"Volo {departure} -- {destination}\nDal {start_wanted_str} al {end_wanted_str}\n\nPartenza: {price_start} {fares_dep}, Ritorno = {price_end} {fares_dest}",
            p, gc['token_bot'])


def start_autorei(start_wanted_str, end_wanted_str, departure, destination):
    autorei_tour = AutoreisenNavigation(departure, destination, start_wanted_str, end_wanted_str, gc['driver_pathname'],
                                        gc['headless'])
    car, price = autorei_tour.run()
    for p in gc['chat_ids'].split(","):
        send(
            f"Dal {start_wanted_str} al {end_wanted_str}\n\nPickup: {departure} <-> {destination}\n\nAuto: {car}, prezzo {price}",
            p, gc['token_bot'])


if __name__ == '__main__':
    print(sys.argv)
    print(gc["driver_pathname"])
    if sys.argv[1] == "ryanair":
        start_ryanair(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif sys.argv[1] == "autoreisen":
        start_autorei(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
