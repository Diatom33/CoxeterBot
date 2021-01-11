import discord
from discord.ext import commands
import sys
import logging
import datetime
import traceback
from PIL import Image, ImageDraw
import os
import re
from cd import CD
from cdError import CDError
from draw import Draw

INVITE_LINK = "https://discord.com/api/oauth2/authorize?client_id=795909275880259604&permissions=34816&scope=bot"
TOKEN = open("../txt/TOKEN.txt", "r").read()
PREFIX = open("../txt/PREFIX.txt", "r").read()

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
            await error(ctx, e, expected = True)
            return
        except Exception as e:
            await error(ctx, e, expected = False)
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

# Shows a help screen with a command list.
client.remove_command("help")
@client.command(pass_context = True)
async def help(ctx, *args):
    args = ' '.join(args)

    if args == '':
        await ctx.send(embed = helpEmbed())
    elif args == 'help':
        await ctx.send(embed = commandHelpEmbed(
            command = args,
            shortExplanation = "Shows in-depth help for a given command.",
            examples = (
                f"`{PREFIX}help help`: Shows this embed.\n"
                f"`{PREFIX}help cd`: Shows help for the `cd` command."
            )
        ))
    elif args == 'cd':
        await ctx.send(embed = commandHelpEmbed(
            command = args,
            shortExplanation = "Renders the [Coxeter–Dynkin](https://polytope.miraheze.org/wiki/Coxeter_diagram) diagram corresponding to a string.",
            examples = (
                f"`{PREFIX}cd x3o3o`: A simple diagram.\n"
                f"`{PREFIX}cd s3s4q3x`: A diagram with various node types.\n"
                f"`{PREFIX}cd x3x3x3*a`: A diagram with loops."
            )
        ))
    elif args == 'invite':
        await ctx.send(embed = commandHelpEmbed(
            command = args,
            shortExplanation = f"Posts the bot [invite link]({INVITE_LINK}).",
            examples = (
                f"`{PREFIX}invite`"
            )
        ))
    else:
        await ctx.send(f"Command `{args}` not recognized!")

    a_logger.info(f"COMMAND: help {args}")

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
    open("../txt/PREFIX.TXT", "w").write(PREFIX)

    a_logger.info(f"INFO: prefix changed to {newPrefix}")
    await ctx.send(f"Prefix changed to {PREFIX}")

# Logs an error and posts it.
async def error(ctx, e, expected):
    if expected:
        expectedStr = ""
    else:
        expectedStr = "UNEXPECTED "

    msg = f"{expectedStr}ERROR: {str(e)}"
    a_logger.info(msg)
    await ctx.send(f"`{msg}`")

# Configures the general help embed.
def helpEmbed():
    helpEmbed = discord.Embed(
        colour = discord.Colour.blue(),
        title = "Coxeter Bot Help"
    )

    helpEmbed.add_field(
        name = f"`{PREFIX}help`",
        value = "Shows help for a given command.",
        inline = False
    )

    helpEmbed.add_field(
        name = f"`{PREFIX}cd [linearized diagram]`",
        value = (
            "Renders a [Coxeter–Dynkin Diagram](https://polytope.miraheze.org/wiki/Coxeter_diagram), "
            "based on [Richard Klitzing's notation]"
            "(https://bendwavy.org/klitzing/explain/dynkin-notation.htm)."
        ),
        inline = False
    )

    helpEmbed.add_field(
        name = f"`{PREFIX}invite`",
        value = f"Posts the bot [invite link]({INVITE_LINK}).",
        inline = False
    )

    return helpEmbed

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
output_file_handler = logging.FileHandler("../../logs/log " +
    datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") + ".txt", 'w', 'utf-8')
stdout_handler = logging.StreamHandler(sys.stdout)
a_logger.addHandler(output_file_handler)
a_logger.addHandler(stdout_handler)

# Runs the bot.
client.run(TOKEN)
