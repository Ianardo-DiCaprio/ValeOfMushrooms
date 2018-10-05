class CustomChannelsUtils:
    def __init__(self, config, bot):
        self.config = config
        self.bot = bot

    async def dash_channel_name(self, channel_name):
        return channel_name.replace(' ', '-')
