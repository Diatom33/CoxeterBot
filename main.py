import discord
from discord.ext import commands
import sys
import logging
import datetime
import traceback
from PIL import Image, ImageDraw
import os
import re
from src.py.cd import CD
from src.py.cdError import CDError
from src.py.draw import Draw
from mwclient import Site
from mwclient.page import Page
from mwclient.errors import InvalidPageTitle

# Basic constants.
INVITE_LINK = "https://discord.com/api/oauth2/authorize?client_id=795909275880259604&permissions=34816&scope=bot"
POLYTOPE_WIKI = "https://polytope.miraheze.org/wiki/"
TOKEN = open("src/txt/TOKEN.txt", "r").read()
PREFIX = open("src/txt/PREFIX.txt", "r").read()
WIKI_PW = open("src/txt/WIKI_PW.txt", "r").read()

# Configures mwclient.
USER_AGENT = 'CoxeterBot (eric.ivan.hdz@gmail.com)'
WIKI_SITE = Site('polytope.miraheze.org')
WIKI_SITE.login('OfficialURL@CoxeterBot', WIKI_PW)
MAX_REDIRECTS = 5

# Users to ping on unexpected error:
USER_IDS = ("370964201478553600", "581141017823019038", "442713612822380554", "253227815338508289")
            # URL                 # Diatom              # Cirro               # Galoomba

client = commands.Bot(command_prefix = PREFIX)
fileCount = 0

# Runs on client ready.
@client.event
async def on_ready():
    await client.change_presence(
        status = discord.Status.online,
        activity = discord.Activity(
            type = discord.ActivityType.watching,
            name = PREFIX + "help"
        )
    )

    a_logger.info("INFO: Bot is ready.")
    a_logger.info(f"INFO: Prefix is {PREFIX}")

# Shows a help screen with a command list.
client.remove_command("help")

helpShortExplanation = "Shows in-depth help for a given command."
cdShortExplanation = (
    "Renders a [Coxeter–Dynkin Diagram](https://polytope.miraheze.org/wiki/Coxeter_diagram), "
    "based on [Richard Klitzing's notation]"
    "(https://bendwavy.org/klitzing/explain/dynkin-notation.htm)."
)
wikiShortExplanation = (
    "Searches for a given article within the "
    f"[Polytope Wiki]({POLYTOPE_WIKI})."
)
inviteShortExplanation = f"Posts the bot [invite link]({INVITE_LINK})."

@client.command(pass_context = True)
async def help(ctx, *command):
    command = ' '.join(command)
    a_logger.info(f"COMMAND: help {command}")

    # Configures the main help embed.
    if command == '':
        helpEmbed = discord.Embed(
            colour = discord.Colour.blue(),
            title = "Coxeter Bot Help"
        )

        helpEmbed.add_field(
            name = f"`{PREFIX}help`",
            value = helpShortExplanation,
            inline = False
        )

        helpEmbed.add_field(
            name = f"`{PREFIX}cd [linearized diagram]`",
            value = cdShortExplanation,
            inline = False
        )

        helpEmbed.add_field(
            name = f"`{PREFIX}wiki [article name]`",
            value = wikiShortExplanation,
            inline = False
        )

        helpEmbed.add_field(
            name = f"`{PREFIX}invite`",
            value = inviteShortExplanation,
            inline = False
        )

        await ctx.send(embed = helpEmbed)
    # The ?help help embed.
    elif command == 'help':
        await ctx.send(embed = commandHelpEmbed(
            command = command,
            shortExplanation = helpShortExplanation,
            examples = (
                f"`{PREFIX}help help`: Shows this embed.\n"
                f"`{PREFIX}help cd`: Shows help for the `cd` command."
            )
        ))
    # The ?help cd embed.
    elif command == 'cd':
        await ctx.send(embed = commandHelpEmbed(
            command = command,
            shortExplanation = wikiShortExplanation,
            examples = (
                f"`{PREFIX}cd x3o3o`: A simple diagram.\n"
                f"`{PREFIX}cd s3s4o3x`: A diagram with various node types.\n"
                f"`{PREFIX}cd x3x3x3*a`: A diagram with loops.\n"
                f"`{PREFIX}cd *-c3x3x3x o3o3o3o3o`: A branching diagram."
            )
        ))
    # The ?help wiki embed.
    elif command == 'wiki':
        await ctx.send(embed = commandHelpEmbed(
            command = command,
            shortExplanation = wikiShortExplanation,
            examples = (
                f"`{PREFIX}wiki x3o3o`: Searches for the tetrahedron.\n"
                f"`{PREFIX}wiki cube`: Searches for a cube."
            )
        ))
    # The ?help invite embed.
    elif command == 'invite':
        await ctx.send(embed = commandHelpEmbed(
            command = command,
            shortExplanation = inviteShortExplanation,
            examples = (
                f"`{PREFIX}invite`"
            )
        ))
    else:
        await ctx.send(f"Command `{command}` not recognized.")

# Shows a Coxeter-Dynkin diagram.
@client.command()
async def cd(ctx, *cd):
    cd = ' '.join(cd)
    a_logger.info(f"COMMAND: cd {cd}")

    if cd == '':
        await ctx.send(f"Usage: `{PREFIX}cd x4o3o`. Run `{PREFIX}help cd` for details.")
    elif cd == 'play':
        await ctx.send(":cd: :play_pause:")
    else:
        try:
            temp = Draw(CD(cd).toGraph()).draw()
        except CDError as e:
            await error(ctx, str(e), dev = False)
            return
        except Exception as e:
            await error(ctx, str(e), dev = True)
            a_logger.info(f"ERROR:\n{traceback.format_exc()}")
            return

        global fileCount
        fileName = f"temp{fileCount}.png"
        fileCount += 1

        temp.save(fileName)
        a_logger.info(f"INFO: Created {fileName} file.")
        await ctx.send(file = discord.File(fileName))

        os.remove(fileName)
        a_logger.info(f"INFO: Removed {fileName} file.")

# Posts the link to a wiki article.
@client.command()
async def wiki(ctx, *title):
    title = ' '.join(title)

    # Displays help.
    if title == '':
        await ctx.send("Usage: `?wiki cube`. Run `?help wiki` for details.")
        return

    a_logger.info(f"COMMAND: wiki {title}")
    title = title[0].capitalize() + title[1:]

    # Tries to load the page.
    try:
        page = Page(WIKI_SITE, title)

        # If the page exists, go through the entire redirect chain.
        if page.exists:
            redirectNumber = 0
            redirect = page.resolve_redirect()
            while page != redirect and page.exists:
                page = redirect
                redirect = page.resolve_redirect()

                redirectNumber += 1
                if redirectNumber > MAX_REDIRECTS:
                    await error(ctx, f"Cyclic redirect chain.")
                    return

        # Formats and posts the URL.
        newTitle = page.name
        if page.exists:
            url = titleToURL(newTitle)

            if title == newTitle:
                await ctx.send(f"Page **{title}** on Polytope Wiki:\n{url}")
            else:
                await ctx.send(f"Page **{title}** redirected to **{newTitle}** on Polytope Wiki:\n{url}")
        else:
            if title == newTitle:
                await error(ctx, f"The requested page {title} does not exist.", dev = False)
            else:
                await error(ctx, f"The requested page {title} redirected to {newTitle}, which does not exist.", dev = False)

    # Title contains non-standard characters.
    except InvalidPageTitle as e:
        await error(ctx, str(e), dev = False)
        return

    # Any other unforeseen exception.
    except Exception as e:
       await error(ctx, str(e), dev = True)
       a_logger.info(f"ERROR:\n{traceback.format_exc()}")
       return

def titleToURL(title):
    return POLYTOPE_WIKI + title.translate({32: '_'})

# Creates a wiki redirect.
@client.command()
@commands.has_role('Wiki Contributor')
async def redirect(ctx, *args):
    a_logger.info(f"COMMAND: redirect {args}")

    if len(args) < 2:
        await ctx.send("Usage: `?redirect x4o3o cube`. Run `?help redirect` for details.")
        return

    originPage = Page(WIKI_SITE, args[0])
    redirectPage = Page(WIKI_SITE, args[1])

    msg = await client.wait_for('message', check = 
        lambda message: message.author == ctx.author and (message.content == 'confirm' or message.content == 'cancel')
    )
    
    confirm = (msg.content == 'confirm')

    if originPage.exists:
        await error(ctx, f"Page {originPage.name} already exists.")
        return
    if not redirectPage.exists:
        await error(ctx, f"Page {redirectPage.name} does not exist.")
        return
    if confirm:
        originPage.edit(f"#REDIRECT [[{args[1]}]]", minor = False, bot = True, section = None)
        await ctx.send(f"Redirected {titleToURL(args[0])} to {titleToURL(args[1])}.")

# Gets the bot invite link.
@client.command()
async def invite(ctx):
    a_logger.info("COMMAND: invite")
    await ctx.send(INVITE_LINK)

# Dev command, shows the client latency.
@client.command()
async def ping(ctx):
    a_logger.info(f"COMMAND: ping")

    latency = round(client.latency * 1000)
    a_logger.info(f"INFO: Latency {latency}ms.")
    await ctx.send(f"Ping: {latency}ms.")

# Changes the bot prefix.
@commands.has_permissions(administrator = True)
@client.command()
async def prefix(ctx, *newPrefix):
    newPrefix = ' '.join(newPrefix)
    a_logger.info(f"COMMAND: prefix {newPrefix}")

    global PREFIX
    PREFIX = newPrefix
    client.command_prefix = PREFIX

    try:
        open("../txt/PREFIX.TXT", "w").write(PREFIX)
    except Exception as e:
        await error(ctx, str(e), dev = True)
        a_logger.info(f"ERROR:\n{traceback.format_exc()}")
        return

    a_logger.info(f"INFO: prefix changed to {newPrefix}")
    await ctx.send(f"Prefix changed to {PREFIX}")

# Throws an error. For testing purposes only.
@commands.has_permissions(administrator = True)
@client.command()
async def error(ctx):
    await error(ctx, "Test error!", dev = True)

# Logs an error and posts it.
# dev signifies that the error is on the developers' fault.
# Otherwise, the error is a user error.
async def error(ctx, text, dev = False):
    if dev:
        logMsg = f"UNEXPECTED ERROR: {text}"
        msg = f"```UNEXPECTED ERROR: {text}```\n"

        # Pings all devs in case of a dev error.
        for user in USER_IDS:
            msg += f"<@{user}> "
    else:
        logMsg = f"ERROR: {text}"
        msg = f"```ERROR: {text}```"

    a_logger.info(logMsg)
    await ctx.send(msg)

# Creates a help embed for a given command.
def commandHelpEmbed(command, shortExplanation, examples):
    embed = discord.Embed(
        colour = discord.Colour.blue(),
        title = f"Command Help: {command}"
    )

    embed.add_field(name = "Explanation", value = shortExplanation, inline = True)
    embed.add_field(name = "Examples", value = examples, inline = False)

    return embed

# Configures logger.
a_logger = logging.getLogger()
a_logger.setLevel(logging.INFO)
output_file_handler = logging.FileHandler("logs/log " +
    datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") + ".txt", 'w', 'utf-8')
stdout_handler = logging.StreamHandler(sys.stdout)
a_logger.addHandler(output_file_handler)
a_logger.addHandler(stdout_handler)

# Runs the bot.
client.run(TOKEN)
