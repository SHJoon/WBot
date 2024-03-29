import discord
from discord import app_commands
from discord.ext import commands
from util import load_db

supabase = load_db.load_db()

class QueueCog(commands.Cog):
    def __init__(self, bot):
        res = supabase.table('queue').select('discord_id, name').execute()
        self.queue = [x['discord_id'] for x in res.data]
        self.queue_msg = None
        self.queue_time = 'None set yet'

    @commands.hybrid_command(name="queue", aliases=["lobby", "q"])
    async def _queue(self, ctx):
        """ View the queue """
        if self.queue_msg is not None:
            try:
                await self.queue_msg.delete()
            except Exception:
                pass
        
        server = ctx.guild
        message = f"**Gaming time**: {self.queue_time}\n"
        for place, member_id in enumerate(self.queue):
            member = discord.utils.get(server.members, id=member_id)
            name = member.nick if member.nick else member.name
            message += f"**#{place+1}** : {name}\n"
        if len(self.queue) == 0:
            message += "Queue is empty"

        embed = discord.Embed(description=message, color=discord.Color.blue())
        embed.set_footer(text="Join the queue with !add / Leave the queue with !leave")
        self.queue_msg = await ctx.send(embed=embed)

        # Attempt to delete user message if possible
        try:
            await ctx.message.delete()
        except Exception:
            pass
    
    @commands.hybrid_command(name="join", aliases=["add"])
    async def join(self, ctx, member: discord.Member = None):
        """ Add yourself to the queue """
        target_user = ctx.message.author
        if member:
            target_user = member
        name = target_user.nick if target_user.nick else target_user.name

        if target_user.id not in self.queue:
            self.queue.append(target_user.id)
            supabase.table('queue').insert({'discord_id': target_user.id, 'name': target_user.name}).execute()
        else:
            if member:
                await ctx.send(f"{name} is already in the queue.")
            else:
                await ctx.send("You are already in the queue.")
        
        await ctx.invoke(self._queue)
    
    @commands.hybrid_command(name="drop", aliases=["leave", "remove"])
    async def drop(self, ctx, member: discord.Member = None):
        """ Remove yourself from the queue """
        target_user = ctx.message.author
        if member:
            target_user = member
        name = target_user.nick if target_user.nick else target_user.name
        
        if target_user.id in self.queue:
            self.queue.remove(target_user.id)
            supabase.table('queue').delete().eq("discord_id", target_user.id).execute()
            await ctx.send(f"{name} has been removed from the queue.")
        else:
            if member:
                await ctx.send(f"{name} was not in the queue")
            else:
                await ctx.send("You were not in the queue")
        
        await ctx.invoke(self._queue)

    @commands.hybrid_command(name="clear")
    async def clear(self, ctx):
        """ Clears the queue """
        self.queue.clear()
        supabase.table('queue').delete().neq('discord_id', 0).execute()
        await ctx.send("Queue has been cleared")
    
    @commands.hybrid_command(name="ready", aliases=['go'])
    async def ready(self, ctx):
        """ Call this when 10 people are ready """
        if len(self.queue) < 10:
            await ctx.send("Not enough people in the queue...")
            return
        
        msg = ""
        for i in range(10):
            member = discord.utils.get(ctx.guild.members, id=self.queue[i])
            msg += member.mention
            supabase.table('queue').delete().eq('discord_id', self.queue[i]).execute()
        for i in range(10):
            self.queue.pop(0)
        await ctx.send(msg)
        await ctx.send("GAMING TIME LET'S GOOOOO")

        await ctx.invoke(self._queue)

    @commands.hybrid_command(name="next")
    async def _next(self, ctx, num=1):
        """ Call the next member in the queue """
        if len(self.queue) == 0:
            await ctx.send("No one left in the queue :(")
            return
        
        if num > len(self.queue):
            num = len(self.queue)
        
        msg = ""
        for i in range(num):
            member = discord.utils.get(ctx.guild.members, id=self.queue[i])
            msg += f"You're up **{member.mention}**! Have fun!\n"
            supabase.table('queue').delete().eq('discord_id', self.queue[i]).execute()
        for i in range(num):
            self.queue.pop(0)
        
        await ctx.send(msg)
        await ctx.invoke(self._queue)

    @commands.hybrid_command(name="ping_queue", aliases=['pingq', 'pq'])
    async def ping_queue(self, ctx):
        """ Ping only the people currently in the queue """
        message = ""
        if len(self.queue):
            for member_id in self.queue:
                member = discord.utils.get(ctx.guild.members, id=member_id)
                message += member.mention
        else:
            message += 'No one in queue to ping'
        
        await ctx.send(message)
    
    @commands.hybrid_command(name="queuetime", aliases=['qtime'])
    async def queuetime(self, ctx, time:str):
        """ Assign game time """
        self.queue_time = time
        await ctx.invoke(self._queue)
    
    @commands.hybrid_command(name="leggo")
    async def leggo(self, ctx, time = "None set yet"):
        """ Get a game going """
        self.queue_time = time
        await ctx.send("Where the shooters at? @here")
        await ctx.invoke(self._queue)
