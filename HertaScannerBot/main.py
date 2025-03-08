import discord
from discord.ext import tasks
import tweepy
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Fetch credentials from environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")


API_KEY = os.getenv("API_KEY")
API_SECRET_KEY = os.getenv("API_SECRET_KEY")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

# Twitter accounts to monitor
TWITTER_ACCOUNTS = ["elonmusk"]
LAST_TWEET_ID = {}

# Initialize Twitter API
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET_KEY, ACCESS_TOKEN,
                                ACCESS_TOKEN_SECRET)
twitter_api = tweepy.API(auth)

# Initialize Discord bot
intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)


@tasks.loop(minutes=1)
async def check_tweets():
    global LAST_TWEET_ID
    channel = client.get_channel(DISCORD_CHANNEL_ID)
    if channel is None:
        print("Invalid Discord channel ID!")
        return

    for account in TWITTER_ACCOUNTS:
        try:
            tweets = twitter_api.user_timeline(screen_name=account, count=1, tweet_mode="extended")
            if tweets:
                latest_tweet = tweets[0]
                if account not in LAST_TWEET_ID or latest_tweet.id > LAST_TWEET_ID[
                        account]:
                    LAST_TWEET_ID[account] = latest_tweet.id
                    await channel.send(
                        f"New tweet from {account}: {latest_tweet.full_text}\n{latest_tweet.entities['urls'][0]['url']}"
                    )
        except Exception as e:
            print(f"Error fetching tweets for {account}: {e}")


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    check_tweets.start()


client.run(DISCORD_TOKEN)
