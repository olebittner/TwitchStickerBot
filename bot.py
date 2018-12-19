import sys
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Sticker
from telegram.error import BadRequest
import logging
import twitch_emotes
import requests
from PIL import Image
import io
from emoji import Emoji, emoji_digits


def parse_number_to_emoji(number):
    number_str = str(number)
    emoji_str = ''
    for digit in number_str:
        emoji_str += emoji_digits[int(digit)]
    return emoji_str


def download_image(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.content
    return False


def resize_image(image, size):
    img = Image.open(io.BytesIO(image))
    img = img.resize((size, size), resample=Image.LANCZOS)
    with io.BytesIO() as output:
        img.save(output, format="PNG")
        return output.getvalue()


def create_sticker_pack(stickers, name, title, user_id, bot, sticker_set=None):
    if len(stickers) > 0:
        logging.log(logging.INFO, f"creating sticker pack '{name}' with {len(stickers)} stickers")
        for i, sticker in enumerate(stickers):
            logging.log(logging.DEBUG, f"downloading and resizing {sticker}")
            img = download_image(sticker)
            img = resize_image(img, 512)
            if i == 0 and sticker_set is None:
                logging.log(logging.DEBUG, f"creating new sticker pack {name}")
                success = bot.create_new_sticker_set(user_id, name, title, io.BytesIO(img), Emoji.digit_zero.value)
            else:
                logging.log(logging.DEBUG, f"adding sticker to existing pack {name}")
                success = bot.add_sticker_to_set(user_id, name, io.BytesIO(img), parse_number_to_emoji(i))
            if not success:
                return i
        sticker_set = bot.get_sticker_set(name)
        return sticker_set.stickers[0]


class TwitchStickersBot:
    def __init__(self, token):
        self.updater = Updater(token=token)
        self.dispatcher = self.updater.dispatcher
        self.bot = self.dispatcher.bot

        self.dispatcher.add_handler(CommandHandler('start', self.__handle_start))
        self.dispatcher.add_handler(MessageHandler(Filters.text, self.__handle_message))

        self.twitch_emotes = twitch_emotes.TwitchEmoteRequester()

    def __handle_start(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id, text=f"I'm a bot, please talk to me! {Emoji.digit_zero.value}")

    def __handle_message(self, bot, update):
        msg = update.message.text
        chat_id = chat_id=update.message.chat_id
        emotes = self.twitch_emotes.get_twitch_emotes(msg)
        if emotes is not None:
            if len(emotes) > 0:
                name = f"{msg}_by_{bot.username}"
                title = f"{msg} Twitch Emotes"
                sticker_set = self.get_sticker_set(name)
                if sticker_set is not None:
                    self.clear_sticker_set(sticker_set)
                result = create_sticker_pack(emotes, name, title, update.message.from_user.id,
                                             bot, sticker_set=sticker_set)
                if isinstance(result, Sticker):
                    bot.send_sticker(chat_id=chat_id, sticker=result)
            else:
                bot.send_message(chat_id=chat_id,
                                 text=f"Sorry, it looks like '{msg}' has no emotes!")
        else:
            bot.send_message(chat_id=chat_id, text=f"Sorry, I could not find a Twitch channel named '{msg}'")
            logging.log(logging.INFO, f"{msg} not found!")

    def get_sticker_set(self, name):
        try:
            return self.bot.get_sticker_set(name)
        except BadRequest as err:
            if err.message == 'Stickerset_invalid':
                return None
            else:
                raise err

    def clear_sticker_set(self, sticker_set):
        logging.log(logging.DEBUG, f"clearing sticker set: {sticker_set.name}")
        for sticker in sticker_set.stickers:
            self.bot.delete_sticker_from_set(sticker.file_id)

    def start_bot(self):
        logging.log(logging.INFO, 'starting bot')
        self.updater.start_polling()
        self.updater.idle()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    bot = TwitchStickersBot(sys.argv[1])
    bot.start_bot()