from .grenzpolizei import Grenzpolizei

#
# This is self-explanatory
#


def setup(bot):
    bot.add_cog(Grenzpolizei(bot))
