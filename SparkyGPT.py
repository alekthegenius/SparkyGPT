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

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if bot.user.mentioned_in(message):
        prompt = str(message.content).replace('<@1141136275148124272> ', '')
        print(prompt)
        message = await message.channel.send("Hold on while my AI mind is thinking...")
        with model.chat_session(system_template):
            tokens = []
            for token in model.generate(prompt, max_tokens=20, streaming=True):
                tokens.append(token)
                await message.edit(content="".join(str(x) for x in tokens))
                print(tokens)
    await bot.process_commands(message)



"""
@bot.command()
async def test(ctx, *args):
    arguments = ' '.join(args)
    prompt = str(arguments)
    output = model.generate(prompt)
    await ctx.send("Hold on while my AI mine is thinking...")
    await ctx.send(output)
"""
        
bot.run(TOKEN)
