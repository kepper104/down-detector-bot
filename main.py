import discord
from config import TOKEN
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from os.path import exists

BASE_URL = "https://downdetector.com/status/"
tracked_games_file_name = "tracked_games.txt"

if not exists(tracked_games_file_name):
    with open(tracked_games_file_name, "w"):
        pass
    print("Created file")


tracked_games = []

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


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

    dr = webdriver.Chrome(options=options)
    dr.get(url)
    # bs = BeautifulSoup(dr.page_source, "lxml")
    with open("source_code.html", "w", encoding="utf-8") as f:
        f.write(dr.page_source)

    # print(dr.page_source)
    return dr.page_source


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

        await message.channel.send("Checking statuses of all tracked games")

        for game_name in tracked_games:
            page = get_page(BASE_URL + game_name)
            status = f"{game_name}: "

            if "User reports indicate problems" in page:
                status += "Problems"
            elif "User reports indicate possible problems" in page:
                status += "Possible problems"
            elif "User reports indicate no current problems" in page:
                status += "No problems"
            else:
                status += "No idea"

            await message.channel.send(status)

    if message.content.startswith('!ping'):
        await message.channel.send('pong')

    if message.content.startswith('!add'):
        game_name = message.content.split(" ")[1]
        with open(tracked_games_file_name, "a") as f:
            f.write(game_name + "\n")
        await message.channel.send("Added game")

client.run(TOKEN)

# User reports indicate problems
# User reports indicate possible problems
# User reports indicate no current problems