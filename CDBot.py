import discord
from discord.ext import commands
import sys
import logging
import datetime
from PIL import Image, ImageDraw
import os
import re
from cd import CD
from draw import Draw

invite_link = "https://discord.com/api/oauth2/authorize?client_id=795909275880259604&permissions=34816&scope=bot"
token = ""
prefix = '?'

client = commands.Bot(command_prefix = prefix)

# Runs on client ready.
@client.event
async def on_ready():
    await client.change_presence(
        status = discord.Status.online,
        activity = discord.Activity(
            type = discord.ActivityType.watching,
            name = prefix + "help"
        )
    )

    a_logger.info("INFO: Bot is ready.")

# Shows a help screen with a command list.
client.remove_command("help")
@client.command(pass_context = True)
async def help(ctx):
    await ctx.send(embed = helpEmbed)
    a_logger.info("COMMAND: help")

# Dev command, shows the client latency.
@client.command()
async def ping(ctx):
    a_logger.info(f"COMMAND: ping")

    latency = round(client.latency * 1000)
    a_logger.info(f"INFO: Latency {latency}ms.")
    await ctx.send(f"Ping: {latency}ms.")

# Gets the bot invite link.
@client.command()
async def invite(ctx):
    a_logger.info("COMMAND: invite")
    await ctx.send(invite_link)

# Shows a Coxeter-Dynkin diagram.
@client.command()
async def cd(ctx, *cd):
    cd = ' '.join(cd)
    a_logger.info(f"COMMAND: cd {cd}.")

    if cd == '':
        await ctx.send(f"Usage: `{prefix}cd x4o3o`. Run `{prefix}help cd` for details.")    
    elif cd == 'c': # Dumb easter egg.
        await ctx.send(f"https://www.cdc.gov/")
    else:
        try:
            temp = Draw(CD(cd).toGraph()).draw()
        except Exception as e:
            await error(ctx, e)
            return

    temp.save("temp.png")
    await ctx.send(file = discord.File("temp.png"))
    os.remove("temp.png")

# Logs an error and posts it.
async def error(ctx, e):
    a_logger.info(f"ERROR: {str(e)}")
    await ctx.send(f"`ERROR: {str(e)}`")

# Configures logger.
a_logger = logging.getLogger()
a_logger.setLevel(logging.INFO)
output_file_handler = logging.FileHandler("logs/log " +
    datetime.datetime.now().strftime("%Y-%m-%d %H-%M") + ".txt")
stdout_handler = logging.StreamHandler(sys.stdout)
a_logger.addHandler(output_file_handler)
a_logger.addHandler(stdout_handler)

# Configures help embed.
helpEmbed = discord.Embed(
    title = "Coxeter Bot Help",
    colour = discord.Colour.blue()
)

helpEmbed.set_author(name = "by Cirro, Diatom, & URL")
helpEmbed.add_field(name = f"`{prefix}help`", value = "You said this.", inline = False)
helpEmbed.add_field(name = f"`{prefix}cd [linearized diagram]`",
    value = ("Renders a Coxeter–Dynkin Diagram, based on [Richard Klitzing's notation]"
    "(https://bendwavy.org/klitzing/explain/dynkin-notation.htm).\n"
    "URL and/or Cirro still have to code this."), inline = False)

# Runs the bot.
client.run(token)
