import discord
from config import TOKEN, DRIVER_PATH
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from os.path import exists
from threading import Thread
import asyncio
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "https://downdetector.com/status/"
tracked_games_file_name = "tracked_games.txt"
WRITE_SOURCE_TO_FILE = False

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def create_file():
    if not exists(tracked_games_file_name):
        with open(tracked_games_file_name, "w"):
            pass
        print("Created file")


def format_game_name(game_name):
    return " ".join(game_name.split("-")).title()


def read_file():
    global tracked_games
    tracked_games.clear()
    with open(tracked_games_file_name, "r") as f:
        print("Reading file")
        for line in f:
            tracked_games.append(line.strip())
            print(line)
        print("Done reading file")


def get_page(url):
    options = Options()
    options.add_argument("--headless=new")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--disable-gpu")
    print("Starting driver")
    dr = webdriver.Chrome(DRIVER_PATH, options=options)
    dr.get(url)
    print("Got page")

    if WRITE_SOURCE_TO_FILE:
        with open("source_code.html", "w", encoding="utf-8") as f:
            f.write(dr.page_source)

    # print(dr.page_source)
    return dr.page_source


def get_game_status(game_name):
    page = get_page(BASE_URL + game_name)

    if "User reports indicate problems" in page:
        return "Problems"
    elif "User reports indicate possible problems" in page:
        return "Possible problems"
    elif "User reports indicate no current problems" in page:
        return "No problems"
    else:
        return "No idea"


async def send_game_status(game_name, channel):
    print(f"Getting status for {game_name}")
    status = get_game_status(game_name)
    print(f"Got status for {game_name}")

    status = f"{format_game_name(game_name)}: {status}"
    print(status)

    # asyncio.run(channel.send(status))
#     WHAT TO DO HERE
    await channel.send(status)


@client.event
async def on_ready():
    print("Ready")
    print(f"Logged in as user {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!status'):
        read_file()
        print(tracked_games)

        msg_len = len(message.content.split())
        if msg_len == 1:
            await message.channel.send("Checking statuses of all tracked games")

            for game_name in tracked_games:
                Thread(target=lambda: asyncio.run_coroutine_threadsafe(send_game_status(game_name, message.channel),
                                                                       client.loop)).start()

        elif msg_len > 1:
            game_name = message.content.split(" ")[1]
            Thread(target=lambda: asyncio.run_coroutine_threadsafe(send_game_status(game_name, message.channel),
                                                                   client.loop)).start()

    if message.content.startswith('!ping'):
        await message.channel.send('pong')

    if message.content.startswith('!add'):
        game_name = message.content.split(" ")[1]
        with open(tracked_games_file_name, "a") as f:
            f.write(game_name + "\n")
        await message.channel.send("Added game")

    if message.content.startswith('!remove'):
        game_name = message.content.split(" ")[1]
        with open(tracked_games_file_name, "r") as f:
            lines = f.readlines()
        with open(tracked_games_file_name, "w") as f:
            for line in lines:
                if line.strip() != game_name:
                    f.write(line)
        await message.channel.send("Removed game" + game_name)

    if message.content.startswith('!list'):
        read_file()
        await message.channel.send("List of tracked games")
        for game_name in tracked_games:
            await message.channel.send(game_name)

    if message.content.startswith('!clear'):
        with open(tracked_games_file_name, "w"):
            pass
        await message.channel.send("Cleared file")

    if message.content.startswith('!help'):
        await message.channel.send("Commands: !status, !ping, !add, !remove, !list, !help, !clear")


create_file()
tracked_games = []

executor = ThreadPoolExecutor()

client.run(TOKEN)

# Statuses:
# User reports indicate problems
# User reports indicate possible problems
# User reports indicate no current problems