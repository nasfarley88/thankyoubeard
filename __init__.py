import re
import random
import aiohttp
from fuzzywuzzy import fuzz
import logging

from skybeard.beards import BeardChatHandler

logger = logging.getLogger(__name__)


async def get_key():
    return BeardChatHandler.key


BOT_JSON = None
THANK_YOUS = ['thank', 'thanks', 'thx', 'ty']
YOUR_WELCOMES = [
    'No problem, {name}.',
    'You\'re welcome, {name}.',
    'I have your back, {name}.',
    'Glad to be of service, {name}.',
    'I only wish I could do more, {name}.',
]


async def get_me():
    global BOT_JSON
    if not BOT_JSON:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    "https://api.telegram.org/bot{}/getMe".format(
                        BeardChatHandler.key)) as resp:
                BOT_JSON = (await resp.json())['result']

    return BOT_JSON


async def is_being_thanked(bot, msg):
    me = await get_me()

    try:
        thank_you_matches = (
            re.match(r"\b{}\b".format(x), msg['text'].lower())
            for x in THANK_YOUS)
        partial_ratio_cut = 75.0
        name_or_username_matches = [
            fuzz.partial_ratio(me['first_name'].lower(), msg['text'].lower()) > partial_ratio_cut,
            fuzz.partial_ratio(me['username'].lower(), msg['text'].lower()) > partial_ratio_cut,
        ]
        if any(thank_you_matches) and any(name_or_username_matches):
            return True
    except AttributeError:
        pass
    except Exception as e:
        logger.error(e)
        raise e


class ThankYouBeard(BeardChatHandler):

    __userhelp__ = """A simple thank you beard. Replies when thanked."""

    __commands__ = [
        (is_being_thanked, 'say_thank_you', None)
    ]

    async def say_thank_you(self, msg):
        await self.sender.sendMessage(
            random.choice(YOUR_WELCOMES).format(name=msg['from']['first_name']))
