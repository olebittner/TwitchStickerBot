import sys
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Sticker
import logging
import twitch_emotes
from Utils import telegram_util


class TwitchStickersBot:
    def __init__(self, token):
        self.updater = Updater(token=token)
        self.dispatcher = self.updater.dispatcher

        self.dispatcher.add_handler(CommandHandler('start', self.__handle_start))
        self.dispatcher.add_handler(MessageHandler(Filters.text, self.__handle_message))

        self.twitch_emotes = twitch_emotes.TwitchEmoteRequester()

    def __handle_start(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id, text=f"I'm a bot, please talk to me!")

    def __handle_message(self, bot, update):
        msg = update.message.text
        chat_id = chat_id=update.message.chat_id
        emotes = self.twitch_emotes.get_twitch_emotes(msg)
        if emotes is not None:
            if len(emotes) > 0:
                name = f"{msg}_by_{bot.username}"
                title = f"{msg} Twitch Emotes"
                sticker_set = telegram_util.get_sticker_set(bot, name)
                if sticker_set is not None:
                    telegram_util.clear_sticker_set(bot, sticker_set)
                result = telegram_util.create_sticker_pack(emotes, name, title, update.message.from_user.id,
                                                           bot, sticker_set=sticker_set)
                if isinstance(result, Sticker):
                    bot.send_sticker(chat_id=chat_id, sticker=result)
            else:
                bot.send_message(chat_id=chat_id,
                                 text=f"Sorry, it looks like '{msg}' has no emotes!")
        else:
            bot.send_message(chat_id=chat_id, text=f"Sorry, I could not find a Twitch channel named '{msg}'")
            logging.log(logging.INFO, f"{msg} not found!")

    def start_bot(self):
        logging.log(logging.INFO, 'starting bot')
        self.updater.start_polling()
        self.updater.idle()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    bot = TwitchStickersBot(sys.argv[1])
    bot.start_bot()
