import aiohttp
import inspect
import discord
import os
from .setup import GrenzpolizeiSetup
import redbot.core.data_manager as datam
from redbot.core.i18n import Translator
from redbot.core import Config

_ = Translator('GrenzpolizeiCore', __file__)

#
# This is the core, where everything except the setup is being processed.
#


class GrenzpolizeiCore:
    def __init__(self, bot):
        self.bot = bot

        # Despite Config's existence, I still need a place to dump attachments
        self.path = str(datam.cog_data_path(self)).replace('\\', '/')
        self.attachment_path = self.path + '/attachments'
        self.check_folder()

        # These event types are now only used in the event enable and disable commands
        self.event_types = ['on_member_update', 'on_voice_state_update', 'on_message_edit', 'on_message_delete',
                            'on_raw_bulk_message_delete', 'on_guild_channel_create', 'on_guild_channel_delete',
                            'on_guild_channel_update', 'on_guild_update', 'on_guild_role_create', 'on_guild_role_delete',
                            'on_guild_role_update', 'on_member_ban', 'on_member_unban', 'on_member_kick',
                            'on_member_remove', 'on_member_join']

        self.config = Config.get_conf(self, identifier=6198483584, force_registration=True)
        default_guild = {
            'enabled': False,
            'compact': False,
            'events': {
                "on_ban": {"enabled": False, "channel": False},
                "on_guild_channel_create": {"enabled": False, "channel": False},
                "on_guild_channel_delete": {"enabled": False, "channel": False},
                "on_guild_channel_update": {"enabled": False, "channel": False},
                "on_guild_role_create": {"enabled": False, "channel": False},
                "on_guild_role_delete": {"enabled": False, "channel": False},
                "on_guild_role_update": {"enabled": False, "channel": False},
                "on_guild_update": {"enabled": False, "channel": False},
                "on_kick": {"enabled": False, "channel": False},
                "on_member_ban": {"enabled": False, "channel": False},
                "on_member_join": {"enabled": False, "channel": False}, 
                "on_member_remove": {"enabled": False, "channel": False},
                "on_member_unban": {"enabled": False, "channel": False},
                "on_member_update": {"enabled": False, "channel": False},
                "on_message_delete": {"enabled": False, "channel": False},
                "on_message_edit": {"enabled": False, "channel": False},
                "on_raw_bulk_message_delete": {"enabled": False, "channel": False},
                "on_voice_state_update": {"enabled": False, "channel": False},
            },
            'ignore': {
                'channels': {},
                'members': {}
            }
        }
        self.config.register_guild(**default_guild)

    def check_folder(self):
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        if not os.path.exists(self.attachment_path):
            os.mkdir(self.attachment_path)

    # Enable an event
    async def enable_event(self, guild, channel, event_type):
        async with self.config.guild(guild).events() as events:
                events[event_type].update({'enabled': True, 'channel': channel.id})

    # Disable an event
    async def disable_event(self, guild, event_type):
        async with self.config.guild(guild).events() as events:
                events[event_type].update({'enabled': False, 'channel': False})

    # Toggle the compact mode
    async def compactmode(self, guild):
        if await self.config.guild(guild).compact():
            await self.config.guild(guild).compact.set(False)
            return _('Compact mode **disabled**')
        else:
            await self.config.guild(guild).compact.set(True)
            return _('Compact mode **enabled**')

    # Toggle a member ignore
    async def ignoremember(self, guild, author):
        if str(author.id) in await self.config.guild(guild).ignore.members():
            async with self.config.guild(guild).ignore.members() as members:
                    members.pop(str(author.id), None)
            return _('Tracking {} again').format(author.mention)
        else:
            async with self.config.guild(guild).ignore.members() as members:
                    members.update({str(author.id): True})
            return _('Not tracking {} anymore').format(author.mention)

    # Toggle a channel ignore
    async def ignorechannel(self, guild, channel):
        if str(channel.id) in await self.config.guild(guild).ignore.channels():
            async with self.config.guild(guild).ignore.channels() as channels:
                    channels.pop(str(channel.id), None)
            return _('Tracking {} again').format(channel.mention)
        else:
            async with self.config.guild(guild).ignore.channels() as channels:
                    channels.update({str(channel.id): True})
            return _('Not tracking {} anymore').format(channel.mention)

    # This is triggered when an event needs to check if either a channel
    # or member is being ignored.
    async def _ignore(self, guild, author=None, channel=None):
        if channel:
            if str(channel.id) in await self.config.guild(guild).ignore.channels():
                return False
        if author:
            if str(author.id) in await self.config.guild(guild).ignore.members():
                return False
        return True

    # This right here validates the event by checking if the guild and event
    # is enabled. If not, it returns False
    #
    # return event['enabled'] if guild_enabled else False
    #
    # inspect.stack()[1][3] <- this returns the function name from the class
    # that called this function. Depending on where the function is being called
    # from, the stack changes. So you'll break it when you're placing it in a
    # different file and you have to change it accordingly.
    async def _validate_event(self, guild):
        events = await self.config.guild(guild).events()
        return events[inspect.stack()[1][3]]['enabled'] if await self.config.guild(guild).enabled() else False

    # Get the channel where the event should be logged to.
    #
    # inspect.stack()[2][3] <- this returns the function name from the class
    # that called this function. Depending on where the function is being called
    # from, the stack changes. So you'll break it when you're placing it in a
    # different file and you have to change it accordingly.
    async def _get_channel(self, guild):
        if not inspect.stack()[2][3] in ['_warn']:
            events = await self.config.guild(guild).events()
            return discord.utils.get(self.bot.get_all_channels(), id=events[inspect.stack()[2][3]]['channel'])
        return False

    # This is of my own concoction. To make message sending universal from
    # everywehere in this cog, and to accomondate for all the things it has
    # to check before we can send anything to an event channel, we need to make
    # sure all data that is needed is there and accounted for.
    async def _send_message_to_channel(self, guild, content=None, embed=None, attachment=None):
        channel = await self._get_channel(guild)
        # Check if the channel exists at all
        if channel:
            # Check if there's an embed
            if embed:
                # Check whether compact mode is enabled
                if not await self.config.guild(guild).compact():
                    await channel.send(content=content, embed=embed)
                # If not, translate the embed to a dictionary and convert it
                # to plaintext.
                else:
                    emdict = embed.to_dict()
                    content = ''
                    if 'author' in emdict:
                        content += '**{}**\n'.format(emdict['author']['name'])
                    if 'fields' in emdict:
                        for field in emdict['fields']:
                            content += '**{}:** {}\n'.format(field['name'].replace('\n', ' ').replace('**', ''), field['value'].replace('\n', ''))
                    if 'description' in emdict:
                        content += '{}\n'.format(emdict['description'])
                    if 'footer' in emdict:
                        content += '_{}_'.format(emdict['footer']['text'])
                    await channel.send(content=content)
            # If it's an attachment, send the attachment.
            elif attachment:
                await channel.send(content=content, file=discord.File(attachment))
            # If it's content only, send only content. :(
            elif content:
                await channel.send(content=content)

    # Download the attachment and store it in the predefined attachment folder
    async def downloadattachment(self, url, filename, message_id):
        session = aiohttp.ClientSession()
        async with session.get(url) as r:
            data = await r.read()
            with open(self.attachment_path+'/{}-{}'.format(message_id, filename), 'wb') as f:
                f.write(data)
        return '{}-{}'.format(message_id, filename)

    # The setup is being called from here (move to setup.py)
    async def _start_setup(self, context):
        guild = context.guild

        events_data = await GrenzpolizeiSetup(self.bot, context).setup()

        async with self.config.guild(guild).events() as events:
                events.update(events_data)
        await self.config.guild(guild).enabled.set(True)

        return True

    # The auto-setup is being called from here (move to setup.py)
    async def _start_auto_setup(self, context):
        guild = context.guild

        events_data = await GrenzpolizeiSetup(self.bot, context).auto_setup()

        async with self.config.guild(guild).events() as events:
                events.update(events_data)
        await self.config.guild(guild).enabled.set(True)

        return True
