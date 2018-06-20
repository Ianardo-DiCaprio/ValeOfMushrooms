import discord
from redbot.core.i18n import Translator
from datetime import datetime
from discord.ext import commands
from .gp_core import GrenzpolizeiCore

_ = Translator('Grenzpolizei', __file__)

# TODO:
# Documentation
# Compartamentalize voice updating
# A way to show all settings (needs a complete rework, removed for now)
# Make embed a decorator

# Changelog:
# -


class Grenzpolizei:
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
        if context.invoked_subcommand is None:
            await context.send_help()

    @_grenzpolizei.group(name='set')
    @commands.has_permissions(administrator=True)
    async def _grenzpolizei_set(self, context):
        '''
        Settings
        '''
        if context.invoked_subcommand is None or context.invoked_subcommand == self._grenzpolizei_set:
            await context.send_help()

    @_grenzpolizei_set.command(name='show')
    async def _grenzpolizei_set_show(self, context):
        '''
        Show all settings
        '''
        await context.send('Sorry, this isn\'t ready yet. :(')

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
        if context.invoked_subcommand is None or context.invoked_subcommand == self._grenzpolizei_set_event:
            await context.send_help()

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

    async def on_member_join(self, author):
        guild = author.guild
        if await self.core._validate_event(guild) and author.id != self.bot.user.id:

            embed = discord.Embed(color=self.green, description=_('**{0.name}#{0.discriminator}** ({0.id})').format(author))
            embed.set_author(name=_('Member joined'))
            embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
            await self.core._send_message_to_channel(guild, embed=embed)

    async def on_member_ban(self, guild, author):
        if await self.core._validate_event(guild) and author.id != self.bot.user.id:

            the_mod = None
            async for entry in guild.audit_logs(limit=2):
                if entry.target.id == author.id and entry.action is discord.AuditLogAction.ban:
                    the_mod = entry.user
                    if entry.reason:
                        reason = entry.reason
                    else:
                        reason = False

            embed = discord.Embed(color=self.red)
            embed.set_author(name=_('Member has been banned'))
            embed.add_field(name=_('**Mod**'), value='{0.display_name}'.format(the_mod))
            embed.add_field(name=_('**Member**'), value='**{0.name}#{0.discriminator}** ({0.display_name} {0.id})'.format(author), inline=False)
            embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))

            if reason:
                embed.add_field(name='Reason', value=reason)

            await self.core._send_message_to_channel(guild, embed=embed)

    async def on_member_unban(self, guild, author):
        if await self.core._validate_event(guild) and author.id != self.bot.user.id:

            async for entry in guild.audit_logs(limit=1):
                if entry.action is discord.AuditLogAction.unban:
                    the_mod = entry.user

            embed = discord.Embed(color=self.orange)
            embed.set_author(name=_('Member has been unbanned'))
            embed.add_field(name=_('**Mod**'), value='{0.display_name}'.format(the_mod))
            embed.add_field(name=_('**Member**'), value='**{0.name}#{0.discriminator}** ({0.display_name} {0.id})'.format(author), inline=False)
            embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))

            await self.core._send_message_to_channel(guild, embed=embed)

    async def on_member_remove(self, author):
        guild = author.guild
        if await self.core._validate_event(guild) and author.id != self.bot.user.id:

            embed = discord.Embed(color=self.red, description=_('**{0.name}#{0.discriminator}** ({0.display_name} {0.id})').format(author))
            embed.set_author(name=_('Member left'))
            embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))

            await self.core._send_message_to_channel(guild, embed=embed)

    async def on_member_update(self, before, after):
        guild = after.guild
        author = after

        if await self.core._ignore(guild, author=author):

            if await self.core._validate_event(guild) and after.id != self.bot.user.id:

                async for entry in guild.audit_logs(limit=1):
                    by_mod = False

                    if entry.action is discord.AuditLogAction.member_update:
                        the_mod = entry.user
                        by_mod = True

                if before.name != after.name:
                    embed = discord.Embed(color=self.blue, description=_('From **{0.name}** ({0.id}) to **{1.name}**').format(before, after))
                    embed.set_author(name=_('Name changed'))
                    await self.core._send_message_to_channel(guild, embed=embed)
                if before.nick != after.nick:
                    embed = discord.Embed(color=self.blue, description=_('From **{0.nick}** ({0.id}) to **{1.nick}**').format(before, after))
                    if by_mod:
                        embed.set_author(name=_('Nickname changed by {0.display_name}').format(the_mod))
                    else:
                        embed.set_author(name=_('Nickname changed'))
                    await self.core._send_message_to_channel(guild, embed=embed)

                if before.roles != after.roles:
                    if len(before.roles) > len(after.roles):
                        for role in before.roles:
                            if role not in after.roles:
                                embed = discord.Embed(color=self.blue, description=_('**{0.display_name}** ({0.id}) lost the **{1.name}** role').format(before, role))
                                if by_mod:
                                    embed.set_author(name=_('Role removed by {0.display_name}').format(the_mod))
                                else:
                                    embed.set_author(name=_('Role removed'))
                    elif len(before.roles) < len(after.roles):
                        for role in after.roles:
                            if role not in before.roles:
                                embed = discord.Embed(color=self.blue, description=_('**{0.display_name}** ({0.id}) got the **{1.name}** role').format(before, role))
                                if by_mod:
                                    embed.set_author(name=_('Role applied by {0.display_name}').format(the_mod))
                                else:
                                    embed.set_author(name=_('Role applied'))
                    await self.core._send_message_to_channel(guild, embed=embed)

    async def on_message_delete(self, message):
        guild = message.guild
        author = message.author
        channel = message.channel

        if isinstance(channel, discord.abc.GuildChannel):
            if await self.core._ignore(guild, author=author, channel=channel):

                if await self.core._validate_event(guild) and author.id != self.bot.user.id:
                    the_mod = False

                    async for entry in guild.audit_logs(limit=1):
                        if entry.action is discord.AuditLogAction.message_delete:
                            the_mod = entry.user

                    embed = discord.Embed(color=self.red)

                    embed.set_author(name=_('Message removed'))
                    embed.add_field(name=_('Member'), value='{0.display_name}#{0.discriminator}\n({0.id})'.format(author))
                    if the_mod:
                        embed.add_field(name=_('Removed by'), value=_('{0.display_name}#{0.discriminator}\n({0.id})'.format(the_mod)))

                    embed.add_field(name=_('Channel'), value=message.channel.mention)
                    if message.content:
                        embed.add_field(name=_('Message'), value=message.clean_content, inline=False)

                    embed.set_footer(text=_('Message ID: {} | {}').format(message.id, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))

                    await self.core._send_message_to_channel(guild, embed=embed)

                    if message.attachments:
                        for attachment in message.attachments:
                            filename = await self.core.downloadattachment(attachment.url, attachment.filename, message.id)
                            message = _('Attachment file for message: {}').format(message.id)
                            await self.core._send_message_to_channel(guild, content=message, attachment=self.core.attachment_path+'/'+filename)

    async def on_message_edit(self, before, after):
        guild = after.guild
        author = after.author
        channel = after.channel

        if isinstance(channel, discord.abc.GuildChannel):
            if await self.core._ignore(guild, author=author, channel=channel):
                if await self.core._validate_event(guild) and author.id != self.bot.user.id and before.clean_content != after.clean_content:

                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name=_('Message changed'))
                    embed.add_field(name=_('Member'), value='{0.display_name}#{0.discriminator}\n({0.id})'.format(author))
                    embed.add_field(name=_('Channel'), value=before.channel.mention)
                    embed.add_field(name=_('Before'), value=before.clean_content, inline=False)
                    embed.add_field(name=_('After'), value=after.clean_content, inline=False)
                    embed.set_footer(text=_('Message ID: {} | {}').format(after.id, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))

                    await self.core._send_message_to_channel(guild, embed=embed)

    async def on_guild_channel_create(self, channel):
        if isinstance(channel, discord.abc.GuildChannel):
            guild = channel.guild

            if await self.core._validate_event(guild):

                async for entry in guild.audit_logs(limit=1):
                    if entry.action is discord.AuditLogAction.channel_create:
                        the_mod = entry.user

                if isinstance(channel, discord.CategoryChannel):
                    embed = discord.Embed(color=self.green)
                    embed.set_author(name=_('A new category has been created by {0.display_name}: #{1.name}').format(the_mod, channel))
                else:
                    embed = discord.Embed(color=self.green)
                    embed.set_author(name=_('A new channel has been created by {0.display_name}: #{1.name}').format(the_mod, channel))

                embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))

                await self.core._send_message_to_channel(guild, embed=embed)

    async def on_guild_channel_delete(self, channel):
        if isinstance(channel, discord.abc.GuildChannel):
            guild = channel.guild

            if await self.core._validate_event(guild):

                async for entry in guild.audit_logs(limit=1):
                    if entry.action is discord.AuditLogAction.channel_delete:
                        the_mod = entry.user

                if isinstance(channel, discord.CategoryChannel):
                    embed = discord.Embed(color=self.red)
                    embed.set_author(name=_('A category has been deleted by {0.display_name}: #{1.name}').format(the_mod, channel))
                else:
                    embed = discord.Embed(color=self.red)
                    embed.set_author(name=_('A channel has been deleted by {0.display_name}: #{1.name}').format(the_mod, channel))
                embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))

                await self.core._send_message_to_channel(guild, embed=embed)

    async def on_guild_channel_update(self, before, after):
        channel = after

        if isinstance(channel, discord.abc.GuildChannel):
            guild = after.guild

            if await self.core._validate_event(guild):

                async for entry in guild.audit_logs(limit=1):
                    if entry.action is discord.AuditLogAction.channel_update:
                        the_mod = entry.user

                if before.name != after.name:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name=_('#{0.name} renamed to #{1.name} by {0.display_name}').format(the_mod, before, after))
                    embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                    await self.core._send_message_to_channel(guild, embed=embed)
                if not isinstance(channel, discord.VoiceChannel) and not isinstance(channel, discord.CategoryChannel):
                    if before.topic != after.topic:
                        embed = discord.Embed(color=self.blue)
                        embed.set_author(name=_('#{0.name} changed topic from \'{1.topic}\' to \'{2.topic}\'').format(the_mod, before, after))
                        embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                        await self.core._send_message_to_channel(guild, embed=embed)
                if before.position != after.position:
                    if isinstance(channel, discord.CategoryChannel):
                        embed = discord.Embed(color=self.blue)
                        embed.set_author(name=_('Category moved by #{0.name} from {1.position} to {2.position}').format(the_mod, before, after))
                        embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                        await self.core._send_message_to_channel(guild, embed=embed)
                    else:
                        embed = discord.Embed(color=self.blue)
                        embed.set_author(name=_('Channel moved  by #{0.name} from {1.position} to {2.position}').format(the_mod, before, after))
                        embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                        await self.core._send_message_to_channel(guild, embed=embed)

    async def on_guild_role_create(self, role):
        guild = role.guild

        if await self.core._validate_event(guild):
            the_mod = False

            async for entry in guild.audit_logs(limit=1):
                if entry.action is discord.AuditLogAction.role_create:
                    the_mod = entry.user

            embed = discord.Embed(color=self.green)
            if the_mod:
                embed.set_author(name=_('Role created by {0.display_name}: {1.name}').format(the_mod, role))
            else:
                embed.set_author(name=_('Role created by Discord: {1.name}').format(the_mod, role))
            embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))

            await self.core._send_message_to_channel(guild, embed=embed)

    async def on_guild_role_delete(self, role):
        guild = role.guild

        if await self.core._validate_event(guild):

            async for entry in guild.audit_logs(limit=1):
                if entry.action is discord.AuditLogAction.role_delete:
                    the_mod = entry.user

            embed = discord.Embed(color=self.red)
            embed.set_author(name=_('Role deleted by {0.display_name}: {1.name}').format(the_mod, role))
            embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))

            await self.core._send_message_to_channel(guild, embed=embed)

    async def on_guild_role_update(self, before, after):
        guild = after.guild

        if await self.core._validate_event(guild):
            the_mod = None

            async for entry in guild.audit_logs(limit=1):
                if entry.action is discord.AuditLogAction.role_update:
                    the_mod = entry.user

            if before.name != after.name and after:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name=_('Role {0.name} renamed to {1.name} by {2.display_name}').format(before, after, the_mod))
                embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                await self.core._send_message_to_channel(guild, embed=embed)
            if before.color != after.color:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name=_('Role color for {0.name} changed from {0.color} to {1.color} by {2.display_name}').format(before, after, the_mod))
                embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                await self.core._send_message_to_channel(guild, embed=embed)
            if before.mentionable != after.mentionable:
                embed = discord.Embed(color=self.blue)
                if after.mentionable:
                    embed.set_author(name=_('{0.display_name} made role {1.name} mentionable').format(the_mod, after))
                else:
                    embed.set_author(name=_('{0.display_name} made role  {1.name} unmentionable').format(the_mod, after))
                embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                await self.core._send_message_to_channel(guild, embed=embed)
            if before.hoist != after.hoist:
                embed = discord.Embed(color=self.blue)
                if after.hoist:
                    embed.set_author(name=_('{0.display_name} made role {1.name} to be shown seperately').format(the_mod, after))
                else:
                    embed.set_author(name=_('{0.display_name} made role {1.name} to be shown seperately').format(the_mod, after))
                embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                await self.core._send_message_to_channel(guild, embed=embed)
            if before.permissions != after.permissions:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name=_('Role permissions {0.name} changed from {0.permissions.value} to {1.permissions.value} by {2.display_name}').format(before, after, the_mod))
                embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                await self.core._send_message_to_channel(guild, embed=embed)
            if before.position != after.position:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name=_('Role position {0} changed from {0.position} to {1.position} by {2.display_name}').format(before, after, the_mod))
                embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                await self.core._send_message_to_channel(guild, embed=embed)

    async def on_guild_update(self, before, after):
        guild = after
        if await self.core._validate_event(guild):
            async for entry in guild.audit_logs(limit=1):
                if entry.action is discord.AuditLogAction.guild_update:
                    the_mod = entry.user
            if before.owner != after.owner:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name=_('Server owner changed from {0.owner.name} (id {0.owner.id})'
                                        'to {1.owner.name} (id {1.owner.id}) by {2.display_name}').format(before, after, the_mod))
                embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                await self.core._send_message_to_channel(guild, embed=embed)
            if before.region != after.region:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name=_('Server region changed from {0.region} to {1.region} by {2.display_name}').format(before, after, the_mod))
                embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                await self.core._send_message_to_channel(guild, embed=embed)
            if before.name != after.name:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name=_('Server name changed from {0.name} to {1.name} by {2.display_name}').format(before, after, the_mod))
                embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                await self.core._send_message_to_channel(guild, embed=embed)
            if before.icon_url != after.icon_url:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name=_('Server icon changed from {0.icon_url} to {1.icon_url} by {2.display_name}').format(before, after, the_mod))
                embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                await self.core._send_message_to_channel(guild, embed=embed)

    async def on_voice_state_update(self, author, before, after):
        guild = author.guild
        if await self.core._ignore(guild, author=author):
            if await self.core._validate_event(guild):
                if not before.afk and after.afk:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name=_('{0.display_name} is idle and has been sent to #{1.channel}').format(author, after), icon_url=author.avatar_url)
                    embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                    await self.core._send_message_to_channel(guild, embed=embed)
                elif before.afk and not after.afk:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name=_('{0.display_name} is active again in #{1.channel}').format(author, after), icon_url=author.avatar_url)
                    embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                    await self.core._send_message_to_channel(guild, embed=embed)
                if not before.self_mute and after.self_mute:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name=_('{0.display_name} muted themselves in #{1.channel}').format(author, after), icon_url=author.avatar_url)
                    embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                    await self.core._send_message_to_channel(guild, embed=embed)
                elif before.self_mute and not after.self_mute:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name=_('{0.display_name} unmuted themselves in #{1.channel}').format(author, after), icon_url=author.avatar_url)
                    embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                    await self.core._send_message_to_channel(guild, embed=embed)
                if not before.self_deaf and after.self_deaf:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name=_('{0.display_name} deafened themselves in #{1.channel}').format(author, after), icon_url=author.avatar_url)
                    embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                    await self.core._send_message_to_channel(guild, embed=embed)
                elif before.self_deaf and not after.self_deaf:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name=_('{0.display_name} undeafened themselves in #{1.channel}').format(author, after), icon_url=author.avatar_url)
                    embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                    await self.core._send_message_to_channel(guild, embed=embed)
                if not before.channel and after.channel:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name=_('{0.display_name} joined voice channel #{1.channel}').format(author, after), icon_url=author.avatar_url)
                    embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                    await self.core._send_message_to_channel(guild, embed=embed)
                elif before.channel and not after.channel:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name=_('{0.display_name} left voice channel #{1.channel}').format(author, before), icon_url=author.avatar_url)
                    embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                    await self.core._send_message_to_channel(guild, embed=embed)
