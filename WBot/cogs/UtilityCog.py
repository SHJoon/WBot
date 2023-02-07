import random
import itertools
import discord
import asyncio
from discord.ext import commands

class AliasHelpCommand(commands.DefaultHelpCommand):
    def __init__(self):
        super().__init__(
            command_attrs={"name": "help", "aliases": ["command", "commands"]}
        )

class UtilityCog(commands.Cog):
    def __init__(self, bot):
        bot.help_command = AliasHelpCommand()
        bot.help_command.cog = self

        self.flip_count = 0
        self.keyboard_array = [
            "1234567890-=",
            "qwertyuiop[",
            "asdfghjkl;'",
            "zxcvbnm,./"
        ]
        self.lookup_table = {
            letter: [row_idx, col_idx]
            for row_idx, row in enumerate(self.keyboard_array)
            for col_idx, letter in enumerate(row)
        }
        self.typo_replace_chance = 10
        self.typo_add_chance = 10
        self.bot = bot
    
    @commands.command()
    async def flip(self, ctx):
        """ Heads or Tails """
        flip = ["Heads", "Tails"]
        ranflip = random.choice(flip)
        if random.randrange(50) == 49:
            ranflip = "Sides"
            self.flip_count = 0
        elif self.flip_count == 50:
            ranflip = "Sides"
            self.flip_count = 0

        embed = discord.Embed(title=ranflip)

        if ranflip == "Heads":
            pics_url = [
                "https://cdn.discordapp.com/attachments/688598474861707304/689666020834803712/unknown.png",
                "https://cdn.discordapp.com/attachments/602376454491078659/659905323217322021/image0.jpg"
            ]
            ranpic = random.choice(pics_url)
            embed.set_image(url=ranpic)
            embed.colour = discord.Colour.orange()
        elif ranflip == "Tails":
            pics_url = [
                "https://cdn.discordapp.com/attachments/623390018991292426/681340369912201264/tails_gif.gif",
                "https://cdn.discordapp.com/attachments/623390018991292426/680682916220895276/unknown.png",
                "https://cdn.discordapp.com/attachments/663534641164320801/663956797048225804/unknown.png"
            ]
            ranpic = random.choice(pics_url)
            embed.set_image(url=ranpic)
            embed.colour = discord.Colour.blue()
        else:
            pics_url = [
                "https://cdn.discordapp.com/attachments/224084353779630080/674848939085922364/EQEaufMUUAIM0aW.png",
                "https://i.imgur.com/P3EbqRH.gif"
            ]
            ranpic = random.choice(pics_url)
            embed.set_image(
                url=ranpic
            )
            embed.colour = discord.Colour.green()
        
        self.flip_count += 1
        await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    async def choose(self, ctx, *choices: str):
        """ Randomly choose from your own provided list of choices """
        await ctx.send(random.choice(choices))
    
    @commands.command()
    async def roll(self, ctx, dice: str):
        """ AdX format only(A=number of die, X=number of faces) """
        try:
            rolls, limit = map(int, dice.split("d"))
        except Exception:
            await ctx.send("AdX format only(A=number of die, X=number of faces)")
            return

        result = ", ".join(str(random.randint(1, limit)) for r in range(rolls))
        await ctx.send(result)

    @commands.command(pass_context=True)
    async def captains(self, ctx):
        """ Randomizes captains list from General Voice channel"""
        members = ctx.message.author.voice.channel.members
        random.shuffle(members)
        message = ""
        for place, member in enumerate(members):
            name = member.nick if member.nick else member.name
            message += f"**#{place+1}** : {name}\n"
        if not message:
            message = "No voice lobby for captains draft"
        await ctx.send(message)

    @commands.command(pass_context=True)
    async def lulcaptains(self, ctx):
        """ Like !captains, but like when Danny drinks"""
        members = ctx.message.author.voice.channel.members
        random.shuffle(members)
        message = ""

        for place, member in enumerate(members):
            name = member.nick if member.nick else member.name
            danny_name = ""
            # Lets typo our name
            for letter_substring in ["".join(g) for _, g in itertools.groupby(name)]:
                # No support for shift+char typos or other non present keys atm, so just pass them to stop
                # us key error indexing on our table
                if letter_substring[0].lower() not in self.lookup_table:
                    danny_name += letter_substring
                elif (
                    random.randrange(100) <= self.typo_replace_chance
                ):  # 10% to REPLACE w/ typo by default
                    typo = await self.generate_typo(letter_substring[0])  # Get the typo
                    danny_name += typo * len(letter_substring)
                elif (
                    random.randrange(100) <= self.typo_add_chance
                ):  # 10% to ADD w/ typo by default
                    # I only want to add like 1 extra character, so don't need
                    # to handle sequences!
                    typo = await self.generate_typo(letter_substring[0])
                    danny_name += letter_substring + typo
                else:
                    danny_name += letter_substring  # this already is stretched out

            message += f"**#{place+1}** : {danny_name}\n"

        if not message:
            message = "No voice lobby for captains draft"

        await ctx.send(message)
        