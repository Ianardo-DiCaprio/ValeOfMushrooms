import discord
from redbot.core import commands

from .core import CustomChannelsCore

BaseCog = getattr(commands, "Cog", object)

class CustomChannels(BaseCog):
    def __init__(self, bot):
        self.bot = bot
        self.core = CustomChannelsCore(self.bot)

    @commands.group(name='customchannels', aliases=['cc'])
    async def customchannels(self, context):
        '''Let users make custom channels'''

    @customchannels.group(name='set')
    @commands.has_permissions(administrator=True)
    async def customchannels_set(self, context):
        '''Settings for CustomChannels'''

    @customchannels_set.group(name='category')
    async def customchannels_set_category(self, context, category: discord.CategoryChannel):
        '''Set the category in which you want all custom channels to be placed in.'''
        message = await self.core.customchannels_set_category(context, category)
        await context.send(message)

    @customchannels.group(name='public')
    async def customchannels_public(self, context, *, channel_name: str):
        '''Open a public channel'''
        message = await self.core.customchannels_public(context, channel_name)
        await context.send(message)

    @customchannels.group(name='private')
    async def customchannels_private(self, context, *, channel_name: str):
        '''Open a private channel'''
        message = await self.core.customchannels_private(context, channel_name)
        await context.send(message)

    @customchannels.group(name='invite')
    async def customchannels_invite(self, context, member: discord.Member):
        '''Invite someone to a private channel'''
        await self.core.customchannels_invite(context, member)

    @customchannels.group(name='leave')
    async def customchannels_leave(self, context):
        '''Leave a private channel'''
        await self.core.customchannels_leave(context)

    @customchannels.group(name='clear')
    async def customchannels_clear(self, context):
        '''Leave a private channel'''
        await self.core.config.guild(context.guild).clear()
        await context.send('cleared')
