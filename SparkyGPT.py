# bot.py
import os
import random
from dotenv import load_dotenv
import discord
from discord.ext import commands
from gpt4all import GPT4All

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents,command_prefix=commands.when_mentioned_or("!"))
#model = GPT4All(r"C:\Users\alekp\Downloads\GPT4All-13B-snoozy.ggmlv3.q4_0.bin")
model = GPT4All(r"C:\Users\alekp\AppData\Local\nomic.ai\GPT4All\wizardlm-13b-v1.1-superhot-8k.ggmlv3.q4_0.bin")

system_template = 'A chat between a curious user and an artificial intelligence assistant.'


@bot.command()
async def test(ctx, *args):
    arguments = ' '.join(args)
    prompt = str(arguments)
    output = model.generate(prompt)
    await ctx.send("Hold on while my AI mine is thinking...")
    await ctx.send(output)
        
bot.run(TOKEN)
