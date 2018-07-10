from .openweather import OpenWeather


def setup(bot):
    bot.add_cog(OpenWeather(bot))
