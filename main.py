import os
import discord
import asyncio
from api import database as db
from api import coingecko as cg
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="cb ")

channel = 0 # Needed for automatic signals, separate thread.

# Initialize list of top 500 coins. This to prevent the capture of low cap coins with similar name.
if not os.path.isfile("coins_markets.txt"):
    cg.update_coins_markets_file()

# Initialize database.
if not os.path.isfile("coinlist.db"):
    db.create_table()


@bot.event
async def on_message(message):
    if channel == 0 and message.content.startswith("cb "):
        set_channel(message.channel)

    await bot.process_commands(message)

@bot.command(
    name="add",
    help="Adds a coin to the list. Correct usage: ... "
)
async def add_to_coinlist(ctx, arg):
    coin_ticker = arg.lower()

    db.add_coin(coin_ticker)

    await ctx.channel.send("Added " + coin_ticker)


@bot.command(
    name="remove",
    help="Removes a coin from the list. Correct usage: ..."
)
async def remove_from_coinlist(ctx, arg):
    coin_ticker = arg.lower()

    db.remove_coin(coin_ticker)

    await ctx.channel.send("Removed " + coin_ticker)

@bot.command(
    name="list",
    help="Shows the list"
)
async def show_coinlist(ctx):
    shitcoin_list = db.query_all_coins()

    list = ""
    async with ctx.typing():
        if len(shitcoin_list) > 0:
            for coin in shitcoin_list:
                price = cg.get_price(coin[0])
                signal = ""

                if len(coin[1]) > 0:
                    signal = "<:alarm_clock:873148072304193598>: " + coin[1]

                daily_change = cg.get_daily_change(coin[0], price)
                daily_trend = "<:green_circle:872494804641153045>"

                if daily_change is None:
                    daily_trend = ""
                else:
                    if daily_change < 0:
                        daily_trend = "<:red_circle:872495146795679815>"


                list = list + str(shitcoin_list.index(coin) + 1) + ": " + coin[0] + " = $" + str(price) + \
                       " (" + daily_trend + str(daily_change) + "%) " + signal + "\n"
        else:
            list = "Empty mate"

    await send_embed(ctx.channel, list, "Coinlist")


@bot.command(
    name="signal",
    help="Add signal trigger price to coin"
)
async def add_signal(ctx, *arg):
    if len(arg) != 3:
        await ctx.channel.send("Please use correct format: cb signal btc > 40000.75")
        return

    coin_ticker = arg[0].lower()
    signal_type = arg[1]
    signal_price = arg[2]

    if (not signal_price.replace('.', '', 1).isdigit() or float(signal_price) <= 0) and signal_price != "max":
        await ctx.channel.send(str(ctx.author) + ", enter positive numeric amount please. No commas, use dots.")
        return

    if signal_type not in "><":
        await ctx.channel.send("Please use correct format: cb signal btc > 40000.75")
        return

    if dict(db.query_all_coins()).get(coin_ticker) is None:
        await add_to_coinlist(ctx, coin_ticker)

    signal = signal_type + signal_price

    db.update_signal(coin_ticker, signal)
    await  ctx.channel.send(coin_ticker + ": added signal " + signal)

async def send_embed(channel, message, title):
    embed = discord.Embed(
        title=title,
        description=message ,
        colour=discord.Colour.dark_purple()
    )

    embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/872176661804777543/"
                            "96245f47c1e2f2d402b10d75159b316b.png?size=256")

    await channel.send(embed=embed)

async def check_coins_thread():
    await bot.wait_until_ready()

    while not bot.is_closed():
        if channel == 0:
            await asyncio.sleep(20)
            continue

        for coin in db.query_all_coins():
            coin_ticker = coin[0]
            signal_price = coin[1]

            if len(signal_price) <= 0:
                continue

            price = cg.get_price(coin[0])

            signal_type = signal_price[:1]
            if signal_type == "<":
                if price <= float(signal_price[1:]):
                    db.update_signal(coin_ticker, "")
                    await send_embed(channel, "PRICE TARGET HIT! " + coin_ticker + signal_price, "SIGNAL")

            else:
                if price >= float(signal_price[1:]):
                    db.update_signal(coin_ticker, "")
                    await send_embed(channel, "PRICE TARGET HIT! " + coin_ticker + signal_price, "SIGNAL")

        await asyncio.sleep(20)

def set_channel(c):
    global channel
    channel = c

bot.loop.create_task(check_coins_thread())
bot.run(DISCORD_TOKEN)
