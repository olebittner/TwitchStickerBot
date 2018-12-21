import requests
import logging
from datetime import datetime, timedelta


class TwitchEmoteRequester:
    def __init__(self):
        self.cache = dict()
        self.last_update = datetime.min
        self.update_json_cache(True)

    def update_json_cache(self, force=False):
        if self.last_update + timedelta(minutes=30) < datetime.now() or force:
            logging.log(logging.INFO, 'updating json cache')
            r = requests.get('https://twitchemotes.com/api_cache/v3/subscriber.json')
            if r.status_code == 200:
                self.cache = r.json()
                self.last_update = datetime.now()
                return True
        return False

    def get_twitch_emotes(self, channel_name):
        channel_name = channel_name.casefold()
        self.update_json_cache()
        for channel, details in self.cache.items():
            if details['channel_name'].casefold() == channel_name or details['display_name'].casefold() == channel_name:
                emotes = list()
                for emote in details['emotes']:
                    emotes.append(f"https://static-cdn.jtvnw.net/emoticons/v1/{emote['id']}/3.0")
                return emotes
