import signal
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Sticker, InlineKeyboardButton, InlineKeyboardMarkup
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
        channel_name = twitch_util.extract_channel_name(msg)
        chat_id = update.message.chat_id
        if channel_name:
            emotes = self.twitch_emotes.get_twitch_emotes(channel_name)
            if emotes is not None:
                if len(emotes) > 0:
                    bot.send_message(chat_id=chat_id, text=f"{channel_name} has {len(emotes)} emotes.\nI will now create your sticker "
                                     f"set. This will take some time, up to a few minutes. Feel free to switch chats or "
                                     f"close Telegram. I'll message you when your set is ready!")
                    name = f"{channel_name}_by_{bot.username}"
                    title = f"{channel_name} Twitch Emotes"
                    sticker_set = telegram_util.get_sticker_set(bot, name)
                    if sticker_set is not None:
                        telegram_util.clear_sticker_set(bot, sticker_set)
                    result = telegram_util.create_sticker_pack(emotes, name, title, update.message.from_user.id,
                                                               bot, sticker_set=sticker_set)
                    if isinstance(result, Sticker):
                        bot.send_sticker(chat_id=chat_id, sticker=result)
                        bot.send_message(chat_id=chat_id, text="Your sticker set is ready. Tap or click on the sticker "
                                                               "above this message to add it to your stickers!",
                                         reply_markup=InlineKeyboardMarkup([[
                                             InlineKeyboardButton(text=f"Subscribe to {channel_name} on Twitch",
                                                                  url=f"https://www.twitch.tv/subs/{channel_name}")]]))
                    else:
                        bot.send_message(chat_id=chat_id, text="Something went wrong during the creation of your set, sorry.")
                else:
                    bot.send_message(chat_id=chat_id,
                                     text=f"Sorry, it looks like '{channel_name}' has no emotes!")
            else:
                bot.send_message(chat_id=chat_id, text=f"Sorry, I could not find a Twitch channel named '{channel_name}'")
                logging.log(logging.DEBUG, f"{channel_name} not found!")
        else:
            bot.send_message(chat_id=chat_id, text=f"Whoopsie, that does not look like a channel name!")

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
