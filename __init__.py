import re
import random
import aiohttp
from fuzzywuzzy import fuzz
import logging

from . import config

from skybeard.beards import BeardChatHandler

logger = logging.getLogger(__name__)


async def get_key():
    return BeardChatHandler.key


BOT_JSON = None


async def get_me():
    global BOT_JSON
    if not BOT_JSON:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    "https://api.telegram.org/bot{}/getMe".format(
                        BeardChatHandler.key)) as resp:
                BOT_JSON = (await resp.json())['result']

    return BOT_JSON


async def passes_partial_ratio(s1, s2, min_partial_ratio=75.0):
    """Returns True if lowercase s1 and s2 matches enough."""
    return fuzz.partial_ratio(
        s1.lower(),
        s2.lower()
    ) > min_partial_ratio


async def is_being_thanked(bot, msg):
    me = await get_me()

    try:
        thank_you_matches = (
            re.match(
                r"\b{}\b".format(x).lower(), msg['text'].lower())
                for x in config.thank_yous)
        partial_ratio_cut = 75.0
        name_or_username_matches = [
            await passes_partial_ratio(me['first_name'], msg['text']),
            await passes_partial_ratio(me['username'], msg['text']),
        ]
        if any(thank_you_matches) and any(name_or_username_matches):
            return True
    except KeyError:
        pass


class ThankYouBeard(BeardChatHandler):

    __userhelp__ = """A simple thank you beard. Replies when thanked."""

    __commands__ = [
        (is_being_thanked, 'say_thank_you', None)
    ]

    async def say_thank_you(self, msg):
        await self.sender.sendMessage(
            random.choice(config.your_welcomes).format(name=msg['from']['first_name']))
