import discord
from discord.ext import commands, tasks
import youtube_dl


from random import choice

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)



client = commands.Bot(command_prefix="-")

status = ["Sadboi Hours", "Listening to J. Cole", "Missing her 😔"]

@client.event
async def on_ready():
    change_status.start()
    print('Bot is online!')

@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='general')
    await channel.send(f'Aur kya haal chaal {member.mention} Gaane chalaye?')

@client.command(name='ping', help=':This command returns the latency')
async def ping(ctx):
    await ctx.send(f'**Pong!** Latency: {round(client.latency * 1000)} ms')

@client.command(name='hello', help=':This command returns the welcome message')
async def hello(ctx):
    responses = ['Hi vro sabh badhiya?', 'Aur batao kese ho', 'Bekar mei utha diya mereko, haan bol kya chaiye' , 'kaha the? missed u ;)']
    await ctx.send(choice(responses))

@client.command(name='die', help=':This command kills the bot')
async def hello(ctx):
    responses = ['Ek toh kaam karo phir ye sabh suno', 'Dalle tereko maardunga', 'aarha hoon mei tere ghar ruk','lakshay ye dekho kya keh rhe hai mereko']
    await ctx.send(choice(responses))

@client.command(name='credits', help = ':This command shows who created me :)')
async def credits(ctx):
    await ctx.send("Made by `Lakshay Kalra`")
    await ctx.send("His discord ID is: `lukky#3358`")

@client.command(name='play', help = ':This command plays music')
async def play(ctx, url):
    if not ctx.message.author.voice:
        await ctx.send('Bestie ur not connected to a voice channel')
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

    server = ctx.message.guild
    voice_channel = server.voice_client

    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=client.loop)
        voice_channel.play(player, after=lambda e: print('Player error: %s' %e) if e else None)

    await ctx.send('**Currently Playing:** {}'.format(player.title))

@client.command(name='stop', help = ':This command stops the music and makes the bot leave the VC.')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()

@tasks.loop(seconds=20)
async def change_status():
    await client.change_presence(activity=discord.Game(choice(status)))

client.run('OTAxMjY5MTQ3NTI1MTg1NTc3.YXNaTQ.tTSdMdjMBbcWaREvyofNIqvIg-o')
