import os
import discord
from moviepy.editor import AudioFileClip
from discord.ext import commands
from dotenv import load_dotenv
from pytube import YouTube
from urllib.parse import quote
import asyncio

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', description='', intents=intents) #Asignar prefijo



@bot.command(name='join', help='Manda al bot al canal de voz')
async def join(ctx):
    try:
        author = ctx.author
        if ctx.guild and author.voice and author.voice.channel:
            channel = author.voice.channel
            voice_channel = await channel.connect()
            await ctx.send(f"Joined {channel.name}")
        else:
            await ctx.send("Este comando solo se puede ejecutar en un servidor.")
    except Exception as e:
        print(f"Error during join: {str(e)}")
        await ctx.send(f"An error occurred: {str(e)}")


@bot.command(name='leave', help='Hacer que el bot deje el canal de voz')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("El bot no esta conectado al canal de voz.")


@bot.command(name='play_song', help='Para reproducir el song')
async def play(ctx, url):
    try:
        voice_channel = ctx.author.voice.channel  # Obtén el canal de voz del autor del mensaje

        if not voice_channel:
            await ctx.send("No estas conectado al canal de voz.")
            return

        # Verifica si el bot ya está en un canal de voz
        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect()

        await voice_channel.connect()

        yt = YouTube(url)

        # Codifica el nombre del video antes de guardarlo como archivo para los signos especiales
        encoded_title = quote(yt.title, safe='')
        audio_path = f"{encoded_title}.mp3"

        # Descarga solo el audio utilizando moviepy
        audio_clip = AudioFileClip(yt.streams.filter(only_audio=True).first().url)
        audio_clip.write_audiofile(audio_path)

        ctx.voice_client.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=audio_path))

        await ctx.send(f'**Now playing:** {yt.title}')

         # Espera hasta que termine la reproducción
        while ctx.voice_client.is_playing():
            await asyncio.sleep(1)

        # Se llama a la función para desconectar y eliminar el archivo
        await disconnect_and_cleanup(ctx, audio_path)

    except Exception as e:
        print(f"An error occurred during playback: {str(e)}")
        await ctx.send("An error occurred during playback.")


@bot.command(name='pause', help='Pausar el song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("El bot no esta reproduciendo nada")
    
@bot.command(name='resume', help='Continua el song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("Usa play_song")

@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("El bot no esta reproduciendo nada")

async def disconnect_and_cleanup(ctx, audio_path):
    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()

    if audio_path is not None and os.path.exists(audio_path):
        os.remove(audio_path)


#Funcion de suma
@bot.command(name='s', help='Suma dos números')
async def s(ctx, n1: int, n2: int):
    try:
        result = n1 + n2
        await ctx.send(f"La suma de {n1} y {n2} es: {result}")
    except Exception as e:
        print(f"Error durante la ejecución del comando: {str(e)}")
        await ctx.send(f"Se produjo un error durante la ejecución del comando.")

if __name__ == "__main__":
    bot.run(TOKEN)
