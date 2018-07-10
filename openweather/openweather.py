from discord.ext import commands
from .core import OpenWeatherCore


class OpenWeather:
    def __init__(self, bot):
        self.core = OpenWeatherCore()

    @commands.command(pass_context=True, name='weather', aliases=['we'])
    async def openweather(self, context, location: str):
        if context.invoked_subcommand:
            await context.send_help()
        else:
            embed = await self.core.get_weather(context.guild, location)
            await context.send(embed=embed)

    @commands.group(pass_context=True, name='weatherset', aliases=['weset'])
    @commands.has_permissions(administrator=True)
    async def weatherset(self, context):
        if context.invoked_subcommand is None:
            await context.send_help()

    @weatherset.command(pass_context=True, name='apikey')
    @commands.is_owner()
    async def weatherset_apikey(self, context, key: str):
        message = await self.core.set_api_key(key)
        await context.send(message)

    @weatherset.command(pass_context=True, name='unit')
    async def weatherset_unit(self, context, unit: str):
        message = await self.core.set_unit(unit)
        await context.send(message)
