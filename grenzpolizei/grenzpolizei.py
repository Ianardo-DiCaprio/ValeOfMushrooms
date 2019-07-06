import discord
from redbot.core import commands
from redbot.core.i18n import Translator


from .core import GrenzpolizeiCore
from .events import GrenzpolizeiEvents

BaseCog = getattr(commands, "Cog", object)

_ = Translator('Grenzpolizei', __file__)

#
# This is where all commands come from, no actual logic is being worked here.
# A function from core is being called to process the data from the commands
#
# So unless you have to add a new command, there's nothing to be done here.
#


class Grenzpolizei(GrenzpolizeiEvents, BaseCog):
    #
    # GrenzpolizeiEvents is a mixin of events.py
    #
    def __init__(self, bot):
        self.bot = bot
        self.core = GrenzpolizeiCore(bot)

        self.green = discord.Color.green()
        self.orange = discord.Color.orange()
        self.red = discord.Color.red()
        self.blue = discord.Color.blue()
        self.black = discord.Color.from_rgb(15, 2, 2)

    @commands.group(name='grenzpolizei', aliases=['gp'])
    async def _grenzpolizei(self, context):
        '''
        The Grenzpolizei Cog
        '''

    @_grenzpolizei.group(name='set')
    @commands.has_permissions(administrator=True)
    async def _grenzpolizei_set(self, context):
        '''
        Settings
        '''

    @_grenzpolizei_set.command(name='show')
    async def _grenzpolizei_set_show(self, context):
        '''
        Show all settings
        '''
        guild = context.guild
        try:
            enabled = await self.core.config.guild(guild).enabled()
            message = '**Enabled:** {}\n\n'.format(enabled)
            on_ban = await self.core.config.guild(guild).events.get_raw("on_ban", "enabled")
            on_ban_channel = await self.core.config.guild(guild).events.get_raw("on_ban", "channel")
            on_ban_chan = self.bot.get_channel(int(on_ban_channel))
            message += '**Ban logging:** {}\n     **Channel:** {}\n'.format(on_ban, on_ban_chan.mention if on_ban_chan else on_ban_chan)
            on_guild_channel_create = await self.core.config.guild(guild).events.get_raw("on_guild_channel_create", "enabled")
            on_guild_channel_create_channel = await self.core.config.guild(guild).events.get_raw("on_guild_channel_create", "channel")
            on_guild_channel_create_chan = self.bot.get_channel(int(on_guild_channel_create_channel))
            message += '**Channel creation:** {}\n     **Channel:** {}\n'.format(on_guild_channel_create, on_guild_channel_create_chan.mention if on_guild_channel_create_chan else on_guild_channel_create_chan)
            on_guild_channel_delete = await self.core.config.guild(guild).events.get_raw("on_guild_channel_delete", "enabled")
            on_guild_channel_delete_channel = await self.core.config.guild(guild).events.get_raw("on_guild_channel_delete", "channel")
            on_guild_channel_delete_chan = self.bot.get_channel(int(on_guild_channel_delete_channel))
            message += '**Channel deletion:** {}\n     **Channel:** {}\n'.format(on_guild_channel_delete, on_guild_channel_delete_chan.mention if on_guild_channel_delete_chan else on_guild_channel_delete_chan)
            on_guild_channel_update = await self.core.config.guild(guild).events.get_raw("on_guild_channel_update", "enabled")
            on_guild_channel_update_channel = await self.core.config.guild(guild).events.get_raw("on_guild_channel_update", "channel")
            on_guild_channel_update_chan = self.bot.get_channel(int(on_guild_channel_update_channel))
            message += '**Channel updates:** {}\n     **Channel:** {}\n'.format(on_guild_channel_update, on_guild_channel_update_chan.mention if on_guild_channel_update_chan else on_guild_channel_update_chan)
            on_guild_role_create = await self.core.config.guild(guild).events.get_raw("on_guild_role_create", "enabled")
            on_guild_role_create_channel = await self.core.config.guild(guild).events.get_raw("on_guild_role_create", "channel")
            on_guild_role_create_chan = self.bot.get_channel(int(on_guild_role_create_channel))
            message += '**Role creation:** {}\n     **Channel:** {}\n'.format(on_guild_role_create, on_guild_role_create_chan.mention if on_guild_role_create_chan else on_guild_role_create_chan)
            on_guild_role_delete = await self.core.config.guild(guild).events.get_raw("on_guild_role_delete", "enabled")
            on_guild_role_delete_channel = await self.core.config.guild(guild).events.get_raw("on_guild_role_delete", "channel")
            on_guild_role_delete_chan = self.bot.get_channel(int(on_guild_role_delete_channel))
            message += '**Role deletion:** {}\n     **Channel:** {}\n'.format(on_guild_role_delete, on_guild_role_delete_chan.mention if on_guild_role_delete_chan else on_guild_role_delete_chan)
            on_guild_role_update = await self.core.config.guild(guild).events.get_raw("on_guild_role_update", "enabled")
            on_guild_role_update_channel = await self.core.config.guild(guild).events.get_raw("on_guild_role_update", "channel")
            on_guild_role_update_chan = self.bot.get_channel(int(on_guild_role_update_channel))
            message += '**Role updates:** {}\n     **Channel:** {}\n'.format(on_guild_role_update, on_guild_role_update_chan.mention if on_guild_role_update_chan else on_guild_role_update_chan)
            on_guild_update = await self.core.config.guild(guild).events.get_raw("on_guild_update", "enabled")
            on_guild_update_channel = await self.core.config.guild(guild).events.get_raw("on_guild_update", "channel")
            on_guild_update_chan = self.bot.get_channel(int(on_guild_update_channel))
            message += '**Server updates:** {}\n     **Channel:** {}\n'.format(on_guild_update, on_guild_update_chan.mention if on_guild_update_chan else on_guild_update_chan)
            on_kick = await self.core.config.guild(guild).events.get_raw("on_kick", "enabled")
            on_kick_channel = await self.core.config.guild(guild).events.get_raw("on_kick", "channel")
            on_kick_chan = self.bot.get_channel(int(on_kick_channel))
            message += '**Kick logging:** {}\n     **Channel:** {}\n'.format(on_kick, on_kick_chan.mention if on_kick_chan else on_kick_chan)
            on_member_join = await self.core.config.guild(guild).events.get_raw("on_member_join", "enabled")
            on_member_join_channel = await self.core.config.guild(guild).events.get_raw("on_member_join", "channel")
            on_member_join_chan = self.bot.get_channel(int(on_member_join_channel))
            message += '**Member joins:** {}\n     **Channel:** {}\n'.format(on_member_join, on_member_join_chan.mention if on_member_join_chan else on_member_join_chan)
            on_member_remove = await self.core.config.guild(guild).events.get_raw("on_member_remove", "enabled")
            on_member_remove_channel = await self.core.config.guild(guild).events.get_raw("on_member_remove", "channel")
            on_member_remove_chan = self.bot.get_channel(int(on_member_remove_channel))
            message += '**Member removes:** {}\n     **Channel:** {}\n'.format(on_member_remove, on_member_remove_chan.mention if on_member_remove_chan else on_member_remove_chan)
            on_member_unban = await self.core.config.guild(guild).events.get_raw("on_member_unban", "enabled")
            on_member_unban_channel = await self.core.config.guild(guild).events.get_raw("on_member_unban", "channel")
            on_member_unban_chan = self.bot.get_channel(int(on_member_unban_channel))
            message += '**Member unbans:** {}\n     **Channel:** {}\n'.format(on_member_unban, on_member_unban_chan.mention if on_member_unban_chan else on_member_unban_chan)
            on_member_ban = await self.core.config.guild(guild).events.get_raw("on_member_ban", "enabled")
            on_member_ban_channel = await self.core.config.guild(guild).events.get_raw("on_member_ban", "channel")
            on_member_ban_chan = self.bot.get_channel(int(on_member_ban_channel))
            message += '**Member bans:** {}\n     **Channel:** {}\n'.format(on_member_ban, on_member_ban_chan.mention if on_member_ban_chan else on_member_ban_chan)
            on_member_update = await self.core.config.guild(guild).events.get_raw("on_member_update", "enabled")
            on_member_update_channel = await self.core.config.guild(guild).events.get_raw("on_member_update", "channel")
            on_member_update_chan = self.bot.get_channel(int(on_member_update_channel))
            message += '**Member updates:** {}\n     **Channel:** {}\n'.format(on_member_update, on_member_update_chan.mention if on_member_update_chan else on_member_update_chan)
            on_message_delete = await self.core.config.guild(guild).events.get_raw("on_message_delete", "enabled")
            on_message_delete_channel = await self.core.config.guild(guild).events.get_raw("on_message_delete", "channel")
            on_message_delete_chan = self.bot.get_channel(int(on_message_delete_channel))
            message += '**Message deletion:** {}\n     **Channel:** {}\n'.format(on_message_delete, on_message_delete_chan.mention if on_message_delete_chan else on_message_delete_chan)
            on_message_edit = await self.core.config.guild(guild).events.get_raw("on_message_edit", "enabled")
            on_message_edit_channel = await self.core.config.guild(guild).events.get_raw("on_message_edit", "channel")
            on_message_edit_chan = self.bot.get_channel(int(on_message_edit_channel))
            message += '**Message edits:** {}\n     **Channel:** {}\n'.format(on_message_edit, on_message_edit_chan.mention if on_message_edit_chan else on_message_edit_chan)
            on_raw_bulk_message_delete = await self.core.config.guild(guild).events.get_raw("on_raw_bulk_message_delete", "enabled")
            on_raw_bulk_message_delete_channel = await self.core.config.guild(guild).events.get_raw("on_raw_bulk_message_delete", "channel")
            on_raw_bulk_message_delete_chan = self.bot.get_channel(int(on_raw_bulk_message_delete_channel))
            message += '**Bulk message deletion:** {}\n     **Channel:** {}\n'.format(on_raw_bulk_message_delete, on_raw_bulk_message_delete_chan.mention if on_raw_bulk_message_delete_chan else on_raw_bulk_message_delete_chan)
            on_voice_state_update = await self.core.config.guild(guild).events.get_raw("on_voice_state_update", "enabled")
            on_voice_state_update_channel = await self.core.config.guild(guild).events.get_raw("on_voice_state_update", "channel")
            on_voice_state_update_chan = self.bot.get_channel(int(on_voice_state_update_channel))
            message += '**Voice updates:** {}\n     **Channel:** {}'.format(on_voice_state_update, on_voice_state_update_chan.mention if on_voice_state_update_chan else on_voice_state_update_chan)
            embed=discord.Embed(title="Grenzpolizei settings", description=message, color=self.red)
            await context.send(embed=embed)
        except:
            await context.send("Something went wrong while trying to show the set settings.")

    @_grenzpolizei_set.command(name='compact')
    async def _grenzpolizei_set_compact(self, context):
        '''
        Toggle compact mode for smaller messages
        '''
        guild = context.guild
        await context.send(await self.core.compactmode(guild))

    @_grenzpolizei_set.group(name='event')
    async def _grenzpolizei_set_event(self, context):
        '''
        Manually control and change event settings
        '''

    @_grenzpolizei_set_event.command(name='enable')
    async def _grenzpolizei_set_event_enable(self, context, event_type: str, channel: discord.TextChannel):
        '''
        Enable an event
        '''
        guild = context.guild
        if event_type.lower() in self.core.event_types:
            await self.core.enable_event(guild, channel, event_type)
            await context.send(_('Event \'{}\' enabled').format(event_type))
        else:
            await context.send(_('This event type does not exist.'))
            message = _('Copy these exactly in order enable or disable them.\n')
            for event in self.core.event_types:
                message += '\n**{}**'.format(event)
            embed = discord.Embed(title=_('Available event types'), description=message, color=self.green)
            await context.send(embed=embed)

    @_grenzpolizei_set_event.command(name='disable')
    async def _grenzpolizei_set_event_disable(self, context, event_type: str):
        '''
        Disable an event
        '''
        guild = context.guild
        if event_type in self.core.event_types:
            await self.core.disable_event(guild, event_type)
            await context.send(_('Event \'{}\' disabled').format(event_type))
        else:
            await context.send(_('This event type does not exist.'))
            message = _('Copy these exactly in order enable or disable them.\n')
            for event in self.core.event_types:
                message += '\n**{}**'.format(event)
            embed = discord.Embed(title=_('Available event types'), description=message, color=self.green)
            await context.send(embed=embed)

    @_grenzpolizei.command(name='setup')
    @commands.has_permissions(administrator=True)
    async def _grenzpolizei_setup(self, context):
        '''
        Begin your journey into authoritarianism
        '''
        x = await self.core._start_setup(context)
        if x:
            await context.send(_('“Until they become conscious, they will never rebel”'))
        else:
            await context.send(_('Please try again, it didn\'t go quite alright.'))

    @_grenzpolizei.command(name='autosetup')
    @commands.has_permissions(administrator=True)
    async def _grenzpolizei_autosetup(self, context):
        '''
        RECOMMENDED! Begin your journey into authoritarianism, automatically.
        '''
        try:
            x = await self.core._start_auto_setup(context)
            if x:
                await context.send(_('“Until they become conscious, they will never rebel”'))
            else:
                await context.send(_('Please try again, it didn\'t go quite alright.'))
        except discord.Forbidden:
            await context.send(_('I don\'t have the permissions to create channels.'))

    @_grenzpolizei.group(name='ignore')
    @commands.has_permissions(kick_members=True)
    async def _grenzpolizei_ignore(self, context):
        '''
        Ignore
        '''
        if context.invoked_subcommand is None or context.invoked_subcommand == self._grenzpolizei_ignore:
            await context.send_help()

    @_grenzpolizei_ignore.command(name='member')
    async def _grenzpolizei_ignore_member(self, context, member: discord.Member):
        '''
        Ignore a member, this is a toggle
        '''
        guild = context.guild
        channel = context.channel
        await channel.send(await self.core.ignoremember(guild, member))

    @_grenzpolizei_ignore.command(name='channel')
    async def _grenzpolizei_ignore_channel(self, context, channel: discord.TextChannel):
        '''
        Ignore a channel, this is a toggle
        '''
        guild = context.guild
        source_channel = context.channel
        await source_channel.send(await self.core.ignorechannel(guild, channel))
