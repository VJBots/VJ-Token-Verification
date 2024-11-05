import pytz
import random
import string
from datetime import date, datetime, timedelta
from info import API, URL
from shortzy import Shortzy

# Time in seconds after which a token will expire
EXPIRE_TOKEN = 3600  # Example: 1 hour

TOKENS = {}
VERIFIED = {}

async def get_verify_shorted_link(link):
    """Shortens the verification link using Shortzy service."""
    shortzy = Shortzy(api_key=API, base_site=URL)
    return await shortzy.convert(link)

async def check_token(bot, userid, token):
    """Checks if a token for a user is valid and not used."""
    user = await bot.get_users(userid)
    user_tokens = TOKENS.get(user.id, {})
    if token in user_tokens:
        is_used = user_tokens[token]
        return is_used is False
    return False

async def get_token(bot, userid, link):
    """Generates a new verification token for the user and returns the shortened link."""
    user = await bot.get_users(userid)
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
    TOKENS.setdefault(user.id, {})[token] = (False, datetime.now(pytz.timezone('Asia/Kolkata')))
    link = f"{link}verify-{user.id}-{token}"
    return str(await get_verify_shorted_link(link))

async def verify_user(bot, userid, token):
    """Marks a token as used for the user and records the current date."""
    user = await bot.get_users(userid)
    if user.id in TOKENS and token in TOKENS[user.id]:
        TOKENS[user.id][token] = (True, TOKENS[user.id][token][1])  # Mark as used but keep the timestamp

async def check_verification(bot, userid, token):
    """Checks if the user is verified and if their verification is still valid."""
    user = await bot.get_users(userid)
    if user.id in TOKENS and token in TOKENS[user.id]:
        is_used, timestamp = TOKENS[user.id][token]
        if is_used:
            # Check if the token has expired
            expiration_time = timestamp + timedelta(seconds=EXPIRE_TOKEN)
            return datetime.now(pytz.timezone('Asia/Kolkata')) < expiration_time
    return False
