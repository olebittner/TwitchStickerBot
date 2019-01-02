import signal
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Sticker
import logging
from Utils import telegram_util, twitch_util, config_util


class TwitchStickersBot:
    def __init__(self, token):
        signal.signal(signal.SIGINT, self.__soft_exit)
        signal.signal(signal.SIGTERM, self.__soft_exit)

        self.updater = Updater(token=token)
        self.dispatcher = self.updater.dispatcher

        self.dispatcher.add_handler(CommandHandler('start', self.__handle_start))
        self.dispatcher.add_handler(MessageHandler(Filters.text, self.__handle_message))

        self.twitch_emotes = twitch_util.TwitchEmoteRequester()

    def __handle_start(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id, text=f"Hi I'm the @TwitchStickersBot.\nSend me the name of "
                            f"a Twitch Channel and I will send you a sticker set containing its emotes.")

    def __handle_message(self, bot, update):
        msg = update.message.text
        chat_id = update.message.chat_id
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

    def __soft_exit(self, signum, frame):
        self.stop_bot()

    def start_bot(self):
        logging.log(logging.INFO, 'starting bot')
        self.updater.start_polling()
        self.updater.idle()

    def stop_bot(self):
        logging.log(logging.INFO, 'stopping bot')
        self.updater.stop()


if __name__ == '__main__':
    config = config_util.get_config()
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    if config_util.token_key in config and config[config_util.token_key] is not '':
        bot = TwitchStickersBot(token=config[config_util.token_key])
        bot.start_bot()
    else:
        logging.log(logging.ERROR, f"{config_util.token_key} not in {config_util.config_path}!")
