#BugadinhoBot por BugadinhoGamers

import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
from discord.ext.commands import Bot
from discord import Game
import asyncio
import os, traceback
from chatterbot import ChatBot

chatbot = ChatBot(
    'John Smart',
    trainer='chatterbot.trainers.ChatterBotCorpusTrainer'
)

#startup_extensions = ["Music"]
startup_extensions = os.listdir("./cogs")
if "__pycache__" in startup_extensions:
    startup_extensions.remove("__pycache__")
startup_extensions = [ext.replace('.py', '') for ext in startup_extensions]
loaded_extensions = []


bot = commands.Bot(command_prefix=commands.when_mentioned_or('$'))
bot.remove_command("help")


@bot.event

async def on_ready():
	print ("BOT INICIADO!")
	print (bot.user.name)
	print (bot.user.id)
	await bot.change_presence(game=Game(name="Online :D"))
	#chatbot.train("chatterbot.corpus.portuguese.conversations")
	

async def on_resumed():
	print ("BOT VOLTOU!")

	
class Main_Commands():
	async def _init_(self, bot):
		self.bot = bot

@bot.event

async def on_member_join(member):
	server = member.server
	role = discord.utils.get(server.roles, name="🔰 Soldados 🔰")
	await bot.add_roles(member, role)
	

@bot.command(pass_context=True)

async def oi(ctx):
	await bot.say("Oi!")
	
@bot.command(pass_context=True)
@commands.has_permissions(manage_messages=True)

async def ban(ctx, banido: discord.User):
	await bot.ban(banido)
	
@bot.command(pass_context=True)
@commands.has_permissions(manage_messages=True)

async def kick(ctx, kickado: discord.User):
	await bot.kick(kickado)
	
@bot.command(pass_context=True)
@commands.has_permissions(manage_messages=True)

async def say(ctx, *, text : str):
	await bot.say(text)
	
@bot.command(pass_context=True)
@commands.has_permissions(manage_messages=True)

async def game(ctx, *, text : str):
	await bot.change_presence(game=Game(name=text))

@bot.command(pass_context=True)
@commands.has_permissions(manage_messages=True)

async def invites(ctx):
	server = ctx.message.channel.server
	invites = await bot.invites_from(server)
	await bot.say(invites)
	
@bot.command(pass_context=True)
@commands.has_permissions(manage_messages=True)

async def invite_check(ctx, *, url : str):
	invite = await bot.get_invite(url)
	print (invite.uses)
	uses = str(invite.uses)
	print (uses)
	max_uses = str(invite.max_uses)
	await bot.say(invite.server)
	await bot.say(uses)
	await bot.say(max_uses)
	await bot.say(invite.inviter)
	
	
@bot.command(pass_context=True)

async def ajuda(ctx):
	await bot.say("**Comandos** : ")
	await bot.say("***$play***    : Tocar musica do Youtube por link!")
	await bot.say("***$skip***    : Votar para pular a musica!")
	await bot.say("***$playing*** : Ver oque esta tocando!")
	await bot.say("***$stop***    : Parar musica!")
	await bot.say("***$resume***  : Voltar a tocar a musica!")
	await bot.say("***$volume***  : async definir volume da musica!")
	await bot.say("***$join***    : Entrar no canal de voz!")
	await bot.say("***$c***       : Conversar com uma rede neural!")

@bot.command(pass_context=True)

async def paraiba(ctx):
	await bot.say("ele sempre esta observando.............")
	
@bot.command(pass_context=True)

async def c(ctx, *, ai_input : str):
	print("ENTRADA AI: ",ai_input)
	ai_resposta_temp = chatbot.get_response(ai_input)
	print("SAIDA AI: ",ai_resposta_temp)
	await bot.say(ai_resposta_temp)
	
	#await bot.say(chatbot.get_response(ai_input))


if __name__ == "__main__":
	
	for extension in startup_extensions:
		try:
			bot.load_extension("cogs.{}".format(extension.replace(".py", "")))
			loaded_extensions.append(extension)
		except Exception as e:
			exc = '{}: []'.format(type(e).__name__, e)
			print('Failed to load extension {}\n{}'.format(extension, exc))
	


bot.run("botaseutokenakitudobem")