from redbot.core import Config
from discord.ext import commands
import discord
import time


class Ticketing:
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=2134287593)
        default_guild = {
            'category': None,
            'closed_category': None,
            'ticket_role': None,
            'default_message': None,
            'dm_message_open': None,
            'dm_message_close': None,
            'sessions': {}
        }
        self.config.register_guild(**default_guild)

    @commands.group(name='ticket')
    async def _ticket(self, context):
        '''
        Create a new ticket
        '''
        if context.invoked_subcommand is None:
            guild = context.guild
            author = context.author
            category_channel = await self.config.guild(guild).category()
            default_message = await self.config.guild(guild).default_message()
            if category_channel and category_channel in [category.id for category in guild.categories]:
                ticket_id = int(time.time())
                ticket_channel = await guild.create_text_channel('ticket-{}'.format(ticket_id), category=self.bot.get_channel(category_channel))
                await ticket_channel.set_permissions(author, read_messages=True, send_messages=True)
                await ticket_channel.set_permissions(guild.me, send_messages=True)
                if default_message:
                    await ticket_channel.send(default_message)
                await self.config.guild(guild).sessions.set({ticket_channel.id: author.id})
                try:
                    await author.send('Ticket `#{}` has been opened for you on {}.'.format(ticket_id, guild.name))
                except discord.Forbidden:
                    pass
            else:
                await context.send('Naughty! You need to run the setup first.')

    @_ticket.command(name='close')
    async def _ticket_close(self, context):
        '''
        Close a ticket
        '''
        guild = context.guild
        channel = context.channel
        author = context.author
        sessions = await self.config.guild(guild).sessions()
        if channel.id in sessions and await self.config.guild(guild).ticket_role() in [role.id for role in author.roles]:
            member = guild.get_member(sessions[channel.id])

            closed_category_channel = await self.config.guild(guild).closed_category()
            closed_category_channel = self.bot.get_channel(closed_category_channel)

            await channel.set_permissions(member, read_messages=False, send_messages=False)
            await channel.edit(category=closed_category_channel)

            ticket_id = str(channel.name).split('-')[1]
            try:
                await member.send('Ticket `#{}` on {} has been closed.'.format(ticket_id, guild.name))
            except discord.Forbidden:
                pass

    @commands.group(name='ticketset')
    async def _tickets(self, context):
        '''
        The settings for Tickets
        '''
        if context.invoked_subcommand is None:
            await context.send_help()

    @_tickets.command(name='setup')
    @commands.has_permissions(administrator=True)
    async def _tickets_setup(self, context):
        '''
        Automatic setup
        '''
        guild = context.guild
        try:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(send_messages=False, read_messages=False),
            }

            category_channel = await guild.create_category('Tickets', overwrites=overwrites)
            closed_category_channel = await guild.create_category('Closed Tickets', overwrites=overwrites)

            ticket_role = await guild.create_role(name='Ticket')

            await category_channel.set_permissions(ticket_role, read_messages=True, send_messages=True)
            await closed_category_channel.set_permissions(ticket_role, read_messages=True, send_messages=True)

            await self.config.guild(guild).category.set(category_channel.id)
            await self.config.guild(guild).closed_category.set(closed_category_channel.id)
            await self.config.guild(guild).ticket_role.set(ticket_role.id)
            await context.send(':tada: Fabulous! You\'re all done! Now add the `Ticket` role to anyone who you deem good enought to handle tickets. And if you care, you can change the name of the role and category if you _really_ want to.')
        except discord.Forbidden:
            await context.send('That didn\'t go well... I need permissions to create channels. :rolling_eyes:')

    @_tickets.command(name='message')
    @commands.has_permissions(administrator=True)
    async def _tickets_message(self, context, *message: str):
        '''
        Set the default message when a new ticket has been created (markdown safe)
        '''
        guild = context.guild
        message = ' '.join(message)
        await self.config.guild(guild).default_message.set(message)
        await context.send('Your default message has been set.')
