from telegram_send import configure
from telegram_send import send


configure("./conf", channel=False, group=False, fm_integration=False)
send(messages="test")