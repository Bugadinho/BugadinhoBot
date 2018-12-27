import asyncio
import discord
from discord.ext import commands
if not discord.opus.is_loaded():
    # the 'opus' library here is opus.dll on windows
    # or libopus.so on linux in the current directory
    # you should replace this with the location the
    # opus library is located in and with the proper filename.
    # note that on windows this DLL is automatically provided for you
    discord.opus.load_opus('opus')

#Nao gosto de dizer isso, mas roubei essa cog dum cara kekekekeke

def __init__(self, bot):
        self.bot = bot

class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

    def __str__(self):
        fmt = ' {0.title} feito por {0.uploader} e pedido por {1.display_name}'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [Duração: {0[0]}m {0[1]}s]'.format(divmod(duration, 60))
        return fmt.format(self.player, self.requester)

class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.voice = None
        self.bot = bot
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.skip_votes = set() # a set of user_ids that voted
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        return self.current.player

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    @asyncio.coroutine
    def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = yield from self.songs.get()
            yield from self.bot.send_message(self.current.channel, 'Agora tocando' + str(self.current))
            self.current.player.start()
            yield from self.play_next_song.wait()
class Music:
    """Voice related commands.
    Works in multiple servers at once.
    """
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[server.id] = state

        return state

    @asyncio.coroutine
    def create_voice_client(self, channel):
        voice = yield from self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass

    @commands.command(pass_context=True, no_pm=True)
    @asyncio.coroutine
    def join(self, ctx, *, channel : discord.Channel):
        """Joins a voice channel."""
        try:
            yield from self.create_voice_client(channel)
        except discord.ClientException:
            yield from self.bot.say('Ja estou estou em um canal de voz...')
        except discord.InvalidArgument:
            yield from self.bot.say('Isso não é um canal de voz...')
        else:
            yield from self.bot.say('Pronto para tocar musica em **' + channel.name)

    @commands.command(pass_context=True, no_pm=True)
    @asyncio.coroutine
    def summon(self, ctx):
        """Summons the bot to join your voice channel."""
        summoned_channel = ctx.message.author.voice_channel
        if summoned_channel is None:
            yield from self.bot.say('Você tem certeza que esta em um canal de voz?')
            return False

        state = self.get_voice_state(ctx.message.server)
        if state.voice is None:
            state.voice = yield from self.bot.join_voice_channel(summoned_channel)
        else:
            yield from state.voice.move_to(summoned_channel)

        return True

    @commands.command(pass_context=True, no_pm=True)
    @asyncio.coroutine
    def play(self, ctx, *, song : str):
        """Plays a song.
        If there is a song currently in the queue, then it is
        queued until the next song is done playing.
        This command automatically searches as well from YouTube.
        The list of supported sites can be found here:
        https://rg3.github.io/youtube-dl/supportedsites.html
        """
        state = self.get_voice_state(ctx.message.server)
        opts = {
            'default_search': 'auto',
            'quiet': True,
        }

        if state.voice is None:
            success = yield from ctx.invoke(self.summon)
            yield from self.bot.say("Carregando a musica...")
            if not success:
                return

        try:
            player = yield from state.voice.create_ytdl_player(song, ytdl_options=opts, after=state.toggle_next)
        except Exception as e:
            fmt = 'Um erro ocorreu ao processar este pedido: ```py\n{}: {}\n```'
            yield from self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
        else:
            player.volume = 0.6
            entry = VoiceEntry(ctx.message, player)
            yield from self.bot.say('Adicionado a playlist' + str(entry))
            yield from state.songs.put(entry)

    @commands.command(pass_context=True, no_pm=True)
    @asyncio.coroutine
    def volume(self, ctx, value : int):
        """Sets the volume of the currently playing song."""

        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.volume = value / 100
            yield from self.bot.say('Volume mudado para {:.0%}'.format(player.volume))
    @commands.command(pass_context=True, no_pm=True)
    @asyncio.coroutine
    def resume(self, ctx):
        """Resumes the currently played song."""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.resume()

    @commands.command(pass_context=True, no_pm=True)
    @asyncio.coroutine
    def stop(self, ctx):
        """Stops playing audio and leaves the voice channel.
        This also clears the queue.
        """
        server = ctx.message.server
        state = self.get_voice_state(server)

        if state.is_playing():
            player = state.player
            player.stop()

        try:
            state.audio_player.cancel()
            del self.voice_states[server.id]
            yield from state.voice.disconnect()
            yield from self.bot.say("Playlist limpa e desconectado do canal ")
        except:
            pass

    @commands.command(pass_context=True, no_pm=True)
    @asyncio.coroutine
    def skip(self, ctx):
        """Vote to skip a song. The song requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """

        state = self.get_voice_state(ctx.message.server)
        if not state.is_playing():
            yield from self.bot.say('Não estou tocando nenhuma musica.')
            return

        voter = ctx.message.author
        if voter == state.current.requester:
            yield from self.bot.say('Pulando musica...')
            state.skip()
        elif voter.id not in state.skip_votes:
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            if total_votes >= 3:
                yield from self.bot.say('Pulando musica...')
                state.skip()
            else:
                yield from self.bot.say('Pedido para pular adicionado, atualmente em [{}/3]'.format(total_votes))
        else:
            yield from self.bot.say('Você ja pediu para pular a musica.')

    @commands.command(pass_context=True, no_pm=True)
    @asyncio.coroutine
    def playing(self, ctx):
        """Shows info about the currently played song."""

        state = self.get_voice_state(ctx.message.server)
        if state.current is None:
            yield from self.bot.say('Não estou tocando nada.')
        else:
            skip_count = len(state.skip_votes)
            yield from self.bot.say('Agora tocando {} [Pedidos para pular: {}/3]'.format(state.current, skip_count))
            
def setup(bot):
    bot.add_cog(Music(bot))
    print('Music is loaded')
