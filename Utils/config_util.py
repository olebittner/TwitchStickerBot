import os
import configparser

config_path = 'config.ini'

section_key = 'TwitchStickerBot'
token_key = 'token'

config = configparser.ConfigParser()


def create_default_config():
    if not os.path.exists(config_path):
        config[section_key] = {token_key: ''}
        with open(config_path, 'w') as file:
            config.write(file)


def get_config():
    create_default_config()
    
    config.read(config_path)
    if section_key in config:
        return config[section_key]

    return None
