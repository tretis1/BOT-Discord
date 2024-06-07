import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

file = "festa-junina.mp3"  # Variável para o caminho do arquivo de áudio

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

async def join_and_play(channel):
    try:
        # Disconnect from any existing voice connections in the same guild
        for vc in bot.voice_clients:
            if vc.guild == channel.guild and vc.channel != channel:
                await vc.disconnect(force=True)
                print('Bot disconnected from the previous channel')

        # Check if the bot is already connected to the desired channel
        if not any(vc.channel == channel for vc in bot.voice_clients):
            vc = await channel.connect()
            print(f'Bot connected to {channel.name}')

            # Play the local audio file
            audio_source = discord.FFmpegPCMAudio(file)
            if not vc.is_playing():
                vc.play(audio_source, after=lambda e: print(f'Finished playing: {e}') if e else None)
                print('Audio started playing')
            else:
                print('Audio is already playing')

            while vc.is_playing():
                await asyncio.sleep(1)

            print('Audio finished playing')
            await vc.disconnect()
            print('Bot disconnected from the channel')
        else:
            print('Bot is already connected to the channel')
    except Exception as e:
        print(f'Error: {e}')

@bot.event
async def on_voice_state_update(member, before, after):
    print(f'Voice state update detected for {member.name}')
    if before.channel is None and after.channel is not None:
        # Member joined a voice channel
        print(f'{member.name} joined {after.channel.name}')
        await join_and_play(after.channel)
    elif before.channel is not None and after.channel is not None and before.channel.id != after.channel.id:
        # Member moved to a different voice channel
        print(f'{member.name} moved from {before.channel.name} to {after.channel.name}')
        await join_and_play(after.channel)
    else:
        print(f'{member.name} did not join a new channel')

bot.run(os.getenv('DISCORD_TOKEN'))
