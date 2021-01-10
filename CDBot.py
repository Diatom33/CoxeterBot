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
    await client.change_presence( \
        status = discord.Status.online, \
        activity = discord.Activity(type = discord.ActivityType.watching, \
        name = prefix + "help" \
    ))

    a_logger.info("Bot is ready.")

client.remove_command("help")

a_logger = logging.getLogger()
a_logger.setLevel(logging.INFO)
output_file_handler = logging.FileHandler("logs/log" +
    datetime.datetime.now().strftime("%Y-%m-%d %H-%M") + ".txt")
stdout_handler = logging.StreamHandler(sys.stdout)
a_logger.addHandler(output_file_handler)
a_logger.addHandler(stdout_handler)

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
    a_logger.info("Helped.")

@client.command()
async def ping(ctx):
    await ctx.send(f"Ping: {round(client.latency * 1000)}ms")
    a_logger.info(f"Ping: {round(client.latency * 1000)}ms")

@client.command()
async def invite(ctx):
    await ctx.send(invite_link)
    a_logger.info("Invite sent")

@client.command()
async def cd(ctx, *cd):
    cd = ' '.join(cd)
    a_logger.info(f"cd: {cd}.")

    if cd == '':
        temp = Image.new('RGB', (60, 30), color = 'white')
    else:
        temp = Draw(CD(cd).toGraph()).draw()

    temp.save("temp.png")
    await ctx.send(file = discord.File("temp.png"))
    os.remove("temp.png")

client.run(token)
