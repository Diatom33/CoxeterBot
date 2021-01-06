import discord
from discord.ext import commands
import sys
import logging
import datetime
from PIL import Image, ImageDraw
import os

invite_link = "https://discord.com/api/oauth2/authorize?client_id=795909275880259604&permissions=34816&scope=bot"
token = ""

client = commands.Bot(command_prefix="&")


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="=help"))
    a_logger.info("bot is ready")
client.remove_command("help")

a_logger = logging.getLogger()
a_logger.setLevel(logging.INFO)

output_file_handler = logging.FileHandler("Logs/log" +
datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") +
 ".txt")
stdout_handler = logging.StreamHandler(sys.stdout)

a_logger.addHandler(output_file_handler)
a_logger.addHandler(stdout_handler)


@client.command(pass_context=True)
async def help(ctx):

    embed = discord.Embed(
        colour=discord.Colour.blue()
    )

    embed.set_author(name="Help")
    embed.add_field(name="`=help`",
                    value="you said this", inline=False)
    embed.add_field(name="`=cd [linearized diagram]`",
                    value="Coxeter-Dynkin Diagram\nURL needs to make this still", inline=False)
    

    await ctx.send(embed=embed)
    a_logger.info("helped")


@client.command()
async def ping(ctx):
    await ctx.send(f"pong {round(client.latency*1000)}ms")
    a_logger.info(f"pong {round(client.latency*1000)}ms")


@client.command()
async def invite(ctx):
    await ctx.send(invite_link)
    a_logger.info("invite sent")

@client.command()
async def cd(ctx, *, cd = "x"):
    a_logger.info(f"cd: {cd}")
    #Image making info here
    img = Image.new('RGB', (60, 30), color = 'red')
    #
    img.save("temp.png")
    await ctx.send(file=discord.File("temp.png"))
    os.remove("temp.png")

client.run(token)
