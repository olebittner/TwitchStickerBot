from telegram.error import BadRequest
import logging
from Utils import image_util
from Utils.emoji import Emoji, parse_number_to_emoji
import io


def get_sticker_set(bot, name):
    try:
        return bot.get_sticker_set(name)
    except BadRequest as err:
        if err.message == 'Stickerset_invalid':
            return None
        else:
            raise err


def clear_sticker_set(bot, sticker_set):
    logging.log(logging.DEBUG, f"clearing sticker set: {sticker_set.name}")
    for sticker in sticker_set.stickers:
        bot.delete_sticker_from_set(sticker.file_id)


def create_sticker_pack(stickers, name, title, user_id, bot, sticker_set=None):
    if len(stickers) > 0:
        logging.log(logging.INFO, f"creating sticker pack '{name}' with {len(stickers)} stickers")
        for i, sticker in enumerate(stickers):
            logging.log(logging.DEBUG, f"downloading and resizing {sticker}")
            img = image_util.download_image(sticker)
            img = image_util.resize_image(img, 512)
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
