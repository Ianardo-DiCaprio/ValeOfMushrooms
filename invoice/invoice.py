from redbot.core import commands
from redbot.core import Config

BaseCog = getattr(commands, "Cog", object)

class InVoice(BaseCog):
    def __init__(self, bot):
        self.bot = bot

        self.config = Config.get_conf(self, identifier=2664288593)
        default_guild = {
            'role': None
        }

        self.config.register_guild(**default_guild)

    async def on_voice_state_update(self, author, before, after):
        guild = author.guild
        if await self.config.guild(guild).role():
            role = [role for role in guild.roles if role.id == await self.config.guild(guild).role()]
            if role:
                if not before.channel and after.channel and role[0] not in author.roles:
                    await author.add_roles(*role)
                elif before.channel and not after.channel and role[0] in author.roles:
                    await author.remove_roles(*role)

    @commands.command(pass_context=True, name='invoiceset')
    @commands.has_permissions(administrator=True)
    async def _invoice_set(self, context, *, role_name):
        """Set InVoice up."""
        guild = context.guild
        invoice_role = await context.guild.create_role(name=role_name, reason='Created for InVoice')
        await self.config.guild(guild).role.set(invoice_role.id)
        await context.send(':+1:')
