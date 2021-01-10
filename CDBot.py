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

client.remove_command("help")

# Configures logger.
a_logger = logging.getLogger()
a_logger.setLevel(logging.INFO)
output_file_handler = logging.FileHandler("logs/log " +
    datetime.datetime.now().strftime("%Y-%m-%d %H-%M") + ".txt")
stdout_handler = logging.StreamHandler(sys.stdout)
a_logger.addHandler(output_file_handler)
a_logger.addHandler(stdout_handler)

# Shows a help screen with a command list.
@client.command(pass_context = True)
async def help(ctx):
    embed = discord.Embed(
        title = "Coxeter Bot Help",
        colour = discord.Colour.blue()
    )

    embed.set_author(name="by Cirro, Diatom, & URL")
    embed.add_field(name = '`' + prefix + "help`", value = "You said this.", inline = False)
    embed.add_field(name = '`' + prefix + "cd [linearized diagram]`",
        value = ("Renders a Coxeter–Dynkin Diagram, based on [Richard Klitzing's notation]"
        "(https://bendwavy.org/klitzing/explain/dynkin-notation.htm).\n"
        "URL and/or Cirro still have to code this."), inline = False)

    await ctx.send(embed = embed)
    a_logger.info("COMMAND: help")

# Dev command, shows the client latency.
@client.command()
async def ping(ctx):
    a_logger.info(f"COMMAND: ping")

    latency = round(client.latency * 1000)
    await ctx.send(f"Ping: {latency}ms.")

    a_logger.info(f"INFO: Latency {latency}ms.")

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
        temp = Image.new('RGB', (60, 30), color = 'white')
    else:
        try:
            temp = Draw(CD(cd).toGraph()).draw()
        except Exception as e:
            a_logger.info("ERROR: " + str(e))
            return

    temp.save("temp.png")
    await ctx.send(file = discord.File("temp.png"))
    os.remove("temp.png")

client.run(token)
