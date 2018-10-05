import discord
from .utils import CustomChannelsUtils
from redbot.core import Config


class CustomChannelsCore:
    def __init__(self, bot):
        self.bot = bot
        self.identifier = 26558867

        self.config = Config.get_conf(self, identifier=self.identifier)
        default_guild = {
            'custom_channels': [],
            'category': False
            }
        self.config.register_guild(**default_guild)

        self.utils = CustomChannelsUtils(self.config, self.bot)

    async def customchannels_set_category(self, context, category):
        guild = context.guild
        await self.config.guild(guild).category.set(category.id)
        return 'Category set'

    async def customchannels_public(self, context, channel_name):
        guild = context.guild
        if await self.config.guild(guild).category():
            channel_name = await self.utils.dash_channel_name(channel_name)

            overwrites = {
                            guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                            guild.me: discord.PermissionOverwrite(read_messages=True),
                            }

            category = discord.utils.get(guild.categories,
                                         id=await self.config.guild(guild).category())

            channel = await guild.create_text_channel(channel_name,
                                                      category=category,
                                                      overwrites=overwrites)

            async with self.config.guild(guild).custom_channels() as custom_channels:
                    custom_channels.append(channel.id)
            return 'Public channel created'
        return 'You need to set the category first!'

    async def customchannels_private(self, context, channel_name):
        guild = context.guild
        if await self.config.guild(guild).category():
            channel_name = await self.utils.dash_channel_name(channel_name)

            overwrites = {
                            guild.default_role: discord.PermissionOverwrite(read_messages=False),
                            guild.me: discord.PermissionOverwrite(read_messages=True),
                            context.author: discord.PermissionOverwrite(read_messages=True)
                            }

            category = discord.utils.get(guild.categories,
                                         id=await self.config.guild(guild).category())

            channel = await guild.create_text_channel(channel_name,
                                                      category=category,
                                                      overwrites=overwrites)

            async with self.config.guild(guild).custom_channels() as custom_channels:
                    custom_channels.append(channel.id)
            return 'Private channel created'
        return 'You need to set the category first!'

    async def customchannels_invite(self, context, member):
        guild = context.guild
        channel = context.channel
        if channel.id in await self.config.guild(guild).custom_channels():
            await context.channel.set_permissions(member,
                                                  read_messages=True)
            return True
        return False

    async def customchannels_leave(self, context):
        guild = context.guild
        channel = context.channel
        member = context.author
        if channel.id in await self.config.guild(guild).custom_channels():
            await context.channel.set_permissions(member,
                                                  read_messages=False)
            return True
        return False
