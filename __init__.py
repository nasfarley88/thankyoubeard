import re
import aiohttp

from skybeard.beards import BeardChatHandler


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


async def is_being_thanked(bot, msg):
    thank_yous = ['thank', 'thanks', 'thx']
    me = await get_me()

    try:
        thank_you_matches = (
            re.match(r"\b{}\b".format(x), msg['text'].lower())
            for x in thank_yous)
        name_or_username_matches = [
            me['first_name'] in msg['text'],
            me['username'] in msg['text']
        ]
        if any(thank_you_matches) and any(name_or_username_matches):
            return True
    except AttributeError:
        pass


class ThankYouBeard(BeardChatHandler):

    __userhelp__ = """A simple echo beard. Echos whatever it is sent."""

    __commands__ = [
        (is_being_thanked, 'say_thank_you', None)
    ]

    async def say_thank_you(self, msg):
        await self.sender.sendMessage(
            "No problem, {}.".format(msg['from']['first_name']))
