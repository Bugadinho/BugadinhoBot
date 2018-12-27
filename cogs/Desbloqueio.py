import datetime
from datetime import datetime
import asyncio
import discord
from discord.ext import commands

class Desbloqueio():
    def __init__(self, bot):
        self.bot = bot

    @asyncio.coroutine
    def on_message(self, message):
        if (message.mentions.__len__()>0):
            log_channel = self.bot.get_channel("472930808873746433") 
            horario = str(datetime.now())
            yield from self.bot.send_message(log_channel, "--[LOG]")
            yield from self.bot.send_message(log_channel, horario)
            yield from self.bot.send_message(log_channel, message.author.name)
            yield from self.bot.send_message(log_channel, "mencionou:")
            for user in message.mentions:
                yield from self.bot.send_message(log_channel, user.name)
            yield from self.bot.send_message(log_channel, "em:")
            yield from self.bot.send_message(log_channel, message.channel.name)
            yield from self.bot.send_message(log_channel, "--[FIM]")

def setup(bot):
    bot.add_cog(Desbloqueio(bot))
    print ("Os mendigao vao tudin si ferra :D")

#Isso era o antigo metodo de responder a quando alguem falava desbloqueio, depois do fim do desbloqueio, reutilizei para fazer logs de mencoes