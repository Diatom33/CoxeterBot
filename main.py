import discord
from discord.ext import commands

import sys
import logging
import datetime
import traceback
import os
import re
from asyncio.exceptions import TimeoutError

from PIL import Image, ImageDraw

from src.py.cd import CD
from src.py.exceptions import CDError, RedirectCycle, TemplateError
from src.py.draw import Draw
from src.py.wiki import Wiki as WikiClass

from mwclient.errors import InvalidPageTitle

# Basic constants.
TOKEN = open("src/txt/TOKEN.txt", "r").read()
PREFIX = open("src/txt/PREFIX.txt", "r").read()

# Users to ping on unexpected error:
USER_IDS = ("370964201478553600", "581141017823019038", "442713612822380554", "253227815338508289")
            # URL                 # Diatom              # Cirro               # Galoomba

# ID of Wiki Contributor role.
ROLE_ID = "<@&699404888127569981>"

# General config.
Wiki = WikiClass()
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
    f"[Polytope Wiki]({Wiki.fullURL}). Resolves redirects automatically."
)
redirectShortExplanation = (
    "Automatically creates a redirect between two articles on the wiki. "
    f"Resolves existing redirects automatically. "
    f"Can only be used by {ROLE_ID}."
)
searchShortExplanation = "Searches for an article on the wiki."
infoShortExplanation = "Gets a shape's info from its infobox on the wiki."

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
            name = f"`{PREFIX}redirect [origin] [target]`",
            value = redirectShortExplanation,
            inline = False
        )

        helpEmbed.add_field(
            name = f"`{PREFIX}search [key]`",
            value = searchShortExplanation,
            inline = False
        )

        helpEmbed.add_field(
            name = f"`{PREFIX}info [shape]`",
            value = infoShortExplanation,
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
                f"`{PREFIX}wiki cube`: Links to the **Cube** article.\n"
                f"`{PREFIX}wiki x3o3o`: Links to the **Tetrahedron** article."
            )
        ))
    # The ?help redirect embed.
    elif command == 'redirect':
        await ctx.send(embed = commandHelpEmbed(
            command = command,
            shortExplanation = redirectShortExplanation,
            examples = (
                f"`{PREFIX}redirect x3o3o tetrahedron`: Redirects the **X3o3o** article to **Tetrahedron**.\n"
                f"`{PREFIX}redirect x3o5o ike`: Redirects the **X3o5o** article to **Icosahedron**.\n"
                f"`{PREFIX}redirect squat \"square tiling\"`: Redirects the **Squat** article to **Square tiling**."
            )
        ))
    # The ?help search embed.
    elif command == 'search':
        await ctx.send(embed = commandHelpEmbed(
            command = command,
            shortExplanation = searchShortExplanation,
            examples = (
                f"`{PREFIX}search dodecahedron`: Gets the wiki results for \"dodecahedron\".\n"
                f"`{PREFIX}search great stellated`: Gets the wiki results for \"great stellated\"."
            )
        ))
    # The ?info search embed.
    elif command == 'info':
        await ctx.send(embed = commandHelpEmbed(
            command = command,
            shortExplanation = infoShortExplanation,
            examples = (
                f"`{PREFIX}info square`: Gets the info for a square.\n"
                f"`{PREFIX}info great dodecahedron`: Gets the info for a great dodecahedron."
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
        page = Wiki.Page(title, redirect = True)

    # Title contains non-standard characters.
    except InvalidPageTitle as e:
        await error(ctx, str(e), dev = False)
        return

    # Redirect chain found.
    except RedirectCycle as e:
        await error(ctx, str(e))
        return

    # Any other unforeseen exception.
    except Exception as e:
       await error(ctx, str(e), dev = True)
       a_logger.info(f"ERROR:\n{traceback.format_exc()}")
       return

    # Formats and posts the URL.
    newTitle = page.name
    if page.exists:
        url = Wiki.titleToURL(newTitle)

        if title == newTitle:
            await ctx.send(f"Page **{title}** on Polytope Wiki:\n{url}")
        else:
            await ctx.send(f"Page **{title}** redirected to **{newTitle}** on Polytope Wiki:\n{url}")
    else:
        if title == newTitle:
            await error(ctx, f"The requested page {title} does not exist.", dev = False)
        else:
            await error(ctx, f"The requested page {title} redirected to {newTitle}, which does not exist.", dev = False)

# Creates a wiki redirect.
@client.command()
@commands.has_role('Wiki Contributor')
async def redirect(ctx, *args):
    a_logger.info(f"COMMAND: redirect {args}")

    # Shows command help.
    if len(args) == 0:
        await ctx.send("Usage: `?redirect x4o3o cube`. Run `?help redirect` for details.")
        return
    elif len(args) == 1:
        await error(ctx, f"2 arguments expected, got 1.", dev = False)
        return
    elif len(args) > 2:
        await error(ctx, f"2 arguments expected, got {len(args)}. Use \"quotation marks\" to enclose article names with more than one word.", dev = False)
        return

    originPage = Wiki.Page(args[0])
    originTitle = originPage.name
    redirectPage = Wiki.Page(args[1])
    redirectTitle = redirectPage.name

    try:
        redirectPage = Wiki.Page(args[1], redirect = True)
    except RedirectCycle as e:
        await error(ctx, str(e), dev = False)

    redirectNewTitle = redirectPage.name

    # Checks for the specific situation where you want to redirect A to B,
    # but A doesn't exist and B redirects to A.
    if originTitle == redirectNewTitle:
        await error (ctx, f"Page {redirectTitle} redirects to {redirectNewTitle}, which is the same as the origin page.", dev = False)
        return

    # Checks that the origin page exists, and the redirect doesn't.
    if originPage.exists:
        await error(ctx, f"Page {originPage.name} already exists.")
        return
    if not redirectPage.exists:
        await error(ctx, f"Page {redirectPage.name} does not exist.")
        return

    # Sends confirmation message.
    if redirectTitle == redirectNewTitle:
        await ctx.send(f"Are you sure you want to redirect **{originTitle}** to **{redirectNewTitle}**?\nType `confirm/cancel`.")
    else:
        await ctx.send(f"Page **{redirectTitle}** redirects to **{redirectNewTitle}**. Are you sure you want to redirect **{originTitle}** to **{redirectNewTitle}**?\nType `confirm/cancel`.")

    # Waits for either a confirm or cancel message.
    try:
        msg = await client.wait_for('message', check =
            lambda message: message.author == ctx.author and (message.content.lower() == 'confirm' or message.content.lower() == 'cancel'),
            timeout = 30
        )
    except TimeoutError as e:
        await error(ctx, "Redirect timed out.", dev = False)
        return

    # Creates the redirect if the user says yes.
    if msg.content.lower() == 'confirm':
        Wiki.redirect(originPage, redirectPage)
        await ctx.send(f"Redirected {Wiki.titleToURL(originTitle)} to {Wiki.titleToURL(redirectNewTitle)}.")
    else:
        await ctx.send("Redirect cancelled.")

# Creates a wiki redirect.
@client.command()
async def search(ctx, *key):
    key = ' '.join(key)
    a_logger.info(f"COMMAND: search {key}")
    resultNumber = 0

    embed = discord.Embed(
        colour = discord.Colour.blue(),
        title = f"Search Results for: {key}"
    )

    for result in Wiki.search(key):
        resultNumber += 1
        title = result.get('title')
        embed.add_field(
            name = f'Result {resultNumber}:',
            value = f"[{title}]({Wiki.titleToURL(title)})",
            inline = False
        )

        if resultNumber == 10:
            break

    if resultNumber == 0:
        await ctx.send(f"No results found for **{key}**.")
    else:
        await ctx.send(embed = embed)

# Searches for a field in a wiki page.
@client.command()
async def info(ctx, *article):
    article = ' '.join(article)
    a_logger.info(f"COMMAND: info {article}")

    # Tries to get the item info.
    try:
        result = Wiki.info(article)
    except TemplateError as e:
        await error(ctx, str(e), dev = False)
        return
    except RedirectCycle as e:
        await error(ctx, str(e), dev = False)
        return

    await ctx.send(result)

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
            msg += f"<@{user}>\n"
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

# Create log folder.
try:
    os.mkdir("logs")
except FileExistsError:
    pass

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
