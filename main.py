from config import *

import discord
from discord.ext import commands
from discord.embeds import Embed

import traceback
from func_timeout import func_timeout, FunctionTimedOut

from requests.exceptions import ReadTimeout
import os

import src.py.wiki as Wiki
from src.py.cd import CD
from src.py.exceptions import CDError, TemplateError
from src.py.draw import Draw
from src.py.node import Graph
import src.py.explanation as explanation
from mwclient.errors import MwClientError

# Configures the bot.
client = commands.Bot(command_prefix = PREFIX)

# Runs on client ready.
@client.event
async def on_ready() -> None:
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

@client.command(pass_context = True)
async def help(ctx, *args: str) -> None:
    command = ' '.join(args)
    log(ctx, f"COMMAND: help {command}")

    # Configures the main help embed.
    if command == '':
        helpEmbed = discord.Embed(
            colour = discord.Colour.blue(),
            title = "Coxeter Bot Help"
        )

        helpEmbed.add_field(
            name = f"`{PREFIX}help`",
            value = explanation.help,
            inline = False
        )

        helpEmbed.add_field(
            name = f"`{PREFIX}cd [linearized diagram]`",
            value = explanation.cd,
            inline = False
        )

        helpEmbed.add_field(
            name = f"`{PREFIX}wiki [article name]`",
            value = explanation.wiki,
            inline = False
        )

        helpEmbed.add_field(
            name = f"`{PREFIX}redirect [origin] [target]`",
            value = explanation.redirect,
            inline = False
        )

        helpEmbed.add_field(
            name = f"`{PREFIX}search [key]`",
            value = explanation.search,
            inline = False
        )

        helpEmbed.add_field(
            name = f"`{PREFIX}info [shape]`",
            value = explanation.info,
            inline = False
        )

        helpEmbed.add_field(
            name = f"`{PREFIX}space [linearized diagram]`",
            value = explanation.space,
            inline = False
        )

        await ctx.send(embed = helpEmbed)
    # The ?help help embed.
    elif command == 'help':
        await ctx.send(embed = commandHelpEmbed(
            command = command,
            shortExplanation = explanation.help,
            examples = (
                f"`{PREFIX}help help`: Shows this embed.\n"
                f"`{PREFIX}help cd`: Shows help for the `cd` command."
            )
        ))
    # The ?help cd embed.
    elif command == 'cd' or command == ':cd:' or command == '💿':
        await ctx.send(embed = commandHelpEmbed(
            command = command,
            shortExplanation = explanation.cd,
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
            shortExplanation = explanation.wiki,
            examples = (
                f"`{PREFIX}wiki cube`: Links to the **Cube** article.\n"
                f"`{PREFIX}wiki x3o3o`: Links to the **Tetrahedron** article."
            )
        ))
    # The ?help redirect embed.
    elif command == 'redirect':
        await ctx.send(embed = commandHelpEmbed(
            command = command,
            shortExplanation = explanation.redirect,
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
            shortExplanation = explanation.search,
            examples = (
                f"`{PREFIX}search dodecahedron`: Gets the wiki results for \"dodecahedron\".\n"
                f"`{PREFIX}search great stellated`: Gets the wiki results for \"great stellated\"."
            )
        ))
    # The ?help info embed.
    elif command == 'info':
        await ctx.send(embed = commandHelpEmbed(
            command = command,
            shortExplanation = explanation.info,
            examples = (
                f"`{PREFIX}info square`: Gets the info for a square.\n"
                f"`{PREFIX}info great dodecahedron`: Gets the info for a great dodecahedron."
            )
        ))
    # The ?help space embed.
    elif command == 'space':
        await ctx.send(embed = commandHelpEmbed(
            command = command,
            shortExplanation = explanation.space,
            examples = (
                f"`{PREFIX}space x3o3o`: Returns the dimension and curvature of a tetrahedron.\n"
                f"`{PREFIX}space x3o3o4x`: Returns the dimension and curvature of \"sidpith\".\n"
                f"`{PREFIX}space x∞o6o`: Returns the dimension and curvature of an order 6 apierogonal tiling."
            )
        ))
    else:
        await ctx.send(f"Command `{command}` not recognized.")

# Shows a Coxeter-Dynkin diagram.
@client.command(aliases = [":cd:", "💿"])
async def cd(ctx, *args: str) -> None:
    try:
        cd = ' '.join(args)
        log(ctx, f"COMMAND: cd {cd}")

        if cd == '':
            await ctx.send(f"Usage: `{PREFIX}cd x4o3o`. Run `{PREFIX}help cd` for details.")
        elif cd == 'play':
            await ctx.send(":cd: :play_pause:")
        elif cd == "c":
            await ctx.send("https://cdc.gov")
        else:
            try:
                graph = CD(cd).toGraph()
                temp = Draw(graph).toImage()
            except CDError as e:
                await error(ctx, str(e), dev = False)
                return

            global fileCount
            fileName = f"temp{fileCount}.png"
            fileCount += 1

            temp.save(fileName)
            log(ctx, f"INFO: Created {fileName} file.")
            await ctx.send(file = discord.File(fileName))

            os.remove(fileName)
            log(ctx, f"INFO: Removed {fileName} file.")

    # Unexpected error.
    except Exception as e:
        await error(ctx, str(e), dev = True)

@client.command(aliases = ["radius", "cr"])
async def circumradius(ctx, *args: str) -> None:
    try:
        cd = ' '.join(args)
        log(ctx, f"COMMAND: circumradius {cd}")
        mode = 'plain'

        # Posts circumradius
        try:
            circ = func_timeout(10, lambda x: CD(x).toGraph().circumradius(), args = (cd,))
        except CDError as e:
            await error(ctx, str(e), dev = False)
            return
        except FunctionTimedOut as e:
            await error(ctx, "Calculation timed out after 10s.", dev = False)
            return

        await longSend(ctx, f"**Circumradius**: {Graph.format(circ, mode)}\n**Decimal approximation:** {Graph.format(circ.evalf(), 'plain')}")
    # Unexpected error.
    except Exception as e:
        await error(ctx, str(e), dev = True)

# Shows a CD's emnompassing space.
@client.command()
async def space(ctx, *args: str) -> None:
    try:
        cd = ' '.join(args)
        log(ctx, f"COMMAND: space {cd}")

        if cd == '':
            await ctx.send(f"Usage: `{PREFIX}space x4o3o`. Run `{PREFIX}help space` for details.")
        else:
            try:
                graph = CD(cd).toGraph()
                space = func_timeout(10, lambda x: graph.spaceOf(), args = (cd,))
                await ctx.send(f"{cd} is a {graph.dimensions()}D {space} polytope.")
            except CDError as e:
                await error(ctx, str(e), dev = False)
                return
            except FunctionTimedOut as e:
                await error(ctx, "Calculation timed out after 10s.", dev = False)
                return

    # Unexpected error.
    except Exception as e:
        await error(ctx, str(e), dev = True)

# Posts the link to a wiki article.
@client.command()
async def wiki(ctx, *args: str) -> None:
    try:
        title = ' '.join(args)

        # Displays help.
        if title == '':
            await ctx.send(f"Usage: `{PREFIX}wiki cube`. Run `{PREFIX}help wiki` for details.")
            return

        log(ctx, f"COMMAND: wiki {title}")
        title = title[0].capitalize() + title[1:]

        # Tries to load the page.
        try:
            page = Wiki.page(title, redirect = True)

        # Any of the possible errors when reading a page.
        except (MwClientError, ReadTimeout) as e:
            await error(ctx, str(e), dev = False)
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

    # Unexpected error.
    except Exception as e:
        await error(ctx, str(e), dev = True)

# Creates a wiki redirect.
@client.command()
@commands.has_role('Wiki Contributor')
async def redirect(ctx, *args: str):
    try:
        log(ctx, f"COMMAND: redirect {args}")

        # Shows command help.
        if len(args) == 0:
            await ctx.send(f"Usage: `{PREFIX}redirect x4o3o cube`. Run `{PREFIX}help redirect` for details.")
            return
        elif len(args) == 1:
            await error(ctx, f"2 arguments expected, got 1.", dev = False)
            return
        elif len(args) > 2:
            await error(ctx, f"2 arguments expected, got {len(args)}. Use \"quotation marks\" to enclose article names with more than one word.", dev = False)
            return

        # Tries to load the pages.
        try:
            originPage = Wiki.page(args[0])
            originTitle = originPage.name
            redirectPage = Wiki.page(args[1])
            redirectTitle = redirectPage.name
            redirectPage = Wiki.page(args[1], redirect = True)

        # Any of the possible errors when reading a page.
        except (MwClientError, ReadTimeout) as e:
            await error(ctx, str(e), dev = False)
            return

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
        # Neither confirmed nor denied.
        except TimeoutError as e:
            await error(ctx, "Redirect timed out.", dev = False)
            return

        # Creates the redirect if the user says yes.
        if msg.content.lower() == 'confirm':
            Wiki.redirect(originPage, redirectPage)
            await ctx.send(f"Redirected {Wiki.titleToURL(originTitle)} to {Wiki.titleToURL(redirectNewTitle)}.")
        else:
            await ctx.send("Redirect cancelled.")

    # Unexpected error.
    except Exception as e:
        await error(ctx, str(e), dev = True)

# Creates a wiki redirect.
@client.command()
async def search(ctx, *args: str) -> None:
    try:
        key = ' '.join(args)
        log(ctx, f"COMMAND: search {key}")
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

    # Unexpected error.
    except Exception as e:
        await error(ctx, str(e), dev = True)

# Searches for a field in a wiki page.
@client.command()
async def get(ctx, *args: str) -> None:
    try:
        log(ctx, f"COMMAND: redirect {args}")

        # Shows command help.
        if len(args) == 0:
            await ctx.send(f"Usage: `{PREFIX}get obsa Tetrahedron`. Run `{PREFIX}help get` for details.")
            return
        elif len(args) == 1:
            await error(ctx, f"2 arguments expected, got 1.", dev = False)
            return
        elif len(args) > 2:
            await error(ctx, f"2 arguments expected, got {len(args)}. Use \"quotation marks\" to enclose article names with more than one word.", dev = False)
            return

        field, title = args[0], args[1]

        try:
            page = Wiki.page(title, redirect = True)
            fieldName, value = Wiki.getField(page, field)

        # Any of the possible errors when reading a template.
        except (MwClientError, ReadTimeout, TemplateError) as e:
            await error(ctx, str(e), dev = False)
            return

        if fieldName == 'Coxeter diagram':
            await cd(ctx, value)
        else:
            embed = discord.Embed(
                colour = discord.Colour.blue(),
                title = f"Polytope info for {page.name}:"
            )

            embed.add_field(name = fieldName, value = value)
            await ctx.send(embed = embed)

    # Unexpected error.
    except Exception as e:
        await error(ctx, str(e), dev = True)
        return

# Posts all fields in a wiki page.
@client.command()
async def info(ctx, *args: str) -> None:
    try:
        title = ' '.join(args)
        log(ctx, f"COMMAND: info {title}")

        # Shows command help.
        if title == '':
            await ctx.send("Usage: `?info dodecahedron`. Run `?help info` for details.")
            return

        # Tries to get the item info.
        try:
            page = Wiki.page(title, redirect = True)
            fieldList = Wiki.getFields(page)

        # Title contains non-standard characters.
        except (MwClientError, TemplateError) as e:
            await error(ctx, str(e), dev = False)
            return
        
        embed = discord.Embed(
            colour = discord.Colour.blue(),
            title = f"Polytope info for {page.name}:"
        )

        empty = True
        for fieldName, value in fieldList.items():
            embed.add_field(name = fieldName, value = value)    
            empty = False

        if empty:
            await error(ctx, str("No valid fields found on the infobox."), dev = False)
        else:
            await ctx.send(embed = embed)

    # Unexpected error.
    except Exception as e:
        await error(ctx, str(e), dev = True)

# Dev command, shows the client latency.
@client.command(aliases = [":ping_pong:", "🏓"])
async def ping(ctx) -> None:
    log(ctx, f"COMMAND: ping")

    latency = round(client.latency * 1000)
    log(ctx, f"INFO: Latency {latency}ms.")
    await ctx.send(f"Ping: {latency}ms.")

# Changes the bot prefix.
@commands.has_permissions(administrator = True)
@client.command()
async def prefix(ctx, *args: str) -> None:
    try:
        newPrefix = ' '.join(args)
        log(ctx, f"COMMAND: prefix {newPrefix}")

        global PREFIX
        PREFIX = newPrefix
        client.command_prefix = PREFIX

        open("src/txt/PREFIX.txt", "w").write(PREFIX)

        await client.change_presence(
            status = discord.Status.online,
            activity = discord.Activity(
                type = discord.ActivityType.watching,
                name = PREFIX + "help"
            )
        )

        log(ctx, f"INFO: prefix changed to {newPrefix}")
        await ctx.send(f"Prefix changed to {PREFIX}")

    # Unexpected error.
    except Exception as e:
        await error(ctx, str(e), dev = True)
        return

# Logs an error and posts it.
# dev signifies that the error is on the developers' fault.
# Otherwise, the error is a user error.
async def error(ctx, text: str, dev: bool = False) -> None:
    if dev:
        logMsg = f"UNEXPECTED ERROR: {text}"
        msg = f"```UNEXPECTED ERROR: {text}\n\nPlease report this issue on the GitHub repository.```\n"
        log(ctx, f"ERROR:\n{traceback.format_exc()}")

        # Pings all devs in case of a dev error.
        if not DEBUG:
            for user in USER_IDS:
                msg += f"<@{user}> "
    else:
        logMsg = f"ERROR: {text}"
        msg = f"```ERROR: {text}```"

    log(ctx, logMsg)
    await ctx.send(msg)

# Sends a message, posting it as a text file in case it is too long.
async def longSend(ctx, text: str):
    if len(text) <= 2000:
        await ctx.send(text)
    else:
        global fileCount
        fc = fileCount
        fileCount += 1

        with open(f"result{fc}.txt", "w") as fileW:
            fileW.write(text)

        with open(f"result{fc}.txt", "rb") as fileR:
            await ctx.send("Result too long, posted as a text file:", file = discord.File(fileR, "result.txt"))
            os.remove(f"result{fc}.txt")

def log(ctx, text: str) -> None:
    a_logger.info(f'<@{ctx.message.author.id}> {text}')

# Creates a help embed for a given command.
def commandHelpEmbed(command: str, shortExplanation: str, examples: str) -> Embed:
    embed = discord.Embed(
        colour = discord.Colour.blue(),
        title = f"Command Help: {command}"
    )

    embed.add_field(name = "Explanation", value = shortExplanation, inline = True)
    embed.add_field(name = "Examples", value = examples, inline = False)

    return embed

# Logs into the wiki.
a_logger.info("INFO: Logging into the wiki...")
Wiki.login()
a_logger.info("INFO: Succesfully logged in.")

# Runs the bot.
client.run(TOKEN)