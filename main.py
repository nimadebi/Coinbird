import os
import discord
from api import database as db
from api import coingecko as cg
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="cb ")

# Initialize list of top 500 coins. This to prevent the capture of low cap coins with similar name.
if not os.path.isfile("coins_markets.txt"):
    cg.update_coins_markets_file()

# Initialize database.
if not os.path.isfile("coinlist.db"):
    db.create_table()

@bot.command(
    name="add",
    help="Adds a coin to the list. Correct usage: ... "
)
async def add_to_coinlist(ctx, arg):
    coin_ticker = arg

    db.add_coin(coin_ticker)

    await ctx.channel.send("Added " + coin_ticker)


@bot.command(
    name="remove",
    help="Removes a coin from the list. Correct usage: ..."
)
async def remove_from_coinlist(ctx, arg):
    coin_ticker = arg

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

                # Should possibly clean this up, someday.
                hourly_and_daily_change = cg.get_hourly_and_daily_change(coin[0])
                hourly_change = hourly_and_daily_change[0]
                daily_change = hourly_and_daily_change[1]

                hourly_trend = "<:green_circle:872494804641153045>"
                daily_trend = "<:green_circle:872494804641153045>"

                if hourly_change is None:
                    hourly_trend = ""
                    daily_trend = ""
                else:
                    if hourly_change < 0:
                        hourly_trend = "<:red_circle:872495146795679815>"

                    if daily_change < 0:
                        daily_trend = "<:red_circle:872495146795679815>"

                list = list + str(shitcoin_list.index(coin) + 1) + ": " + coin[0] + " = $" + str(price) + " >> " + \
                           hourly_trend + str(hourly_change) + "% <> " + daily_trend + str(daily_change) + "%\n"

        else:
            list = "Empty mate"

    await send_embed(ctx.channel, list, "Coinlist")

async def send_embed(channel, message, title):
    embed = discord.Embed(
        title=title,
        description=message,
        colour=discord.Colour.dark_purple()
    )

    embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/812061601862647818/"
                            "a6a1cf799a1379e3e6f5378c46a0c303.png?size=256")

    await channel.send(embed=embed)

bot.run(DISCORD_TOKEN)
