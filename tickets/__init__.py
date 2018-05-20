from .tickets import Ticketing


def setup(bot):
    bot.add_cog(Ticketing(bot))
