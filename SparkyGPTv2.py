"""
SparkyGPT.py Copyright 2023 by Alek Vasek (alekvasek@icloud.com)
"""
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from gpt4all import GPT4All
import glob
import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
import functools
import typing
import asyncio
import Joking
import logging
import logging.handlers

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename='discord.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.message_content = True

model_path = r"/home/alek/GPTModules"

modules = [os.path.basename(x) for x in glob.glob(model_path + '/*.bin')] # Change '/*.bin' to `\*.bin` for Windows

model_id = "stabilityai/stable-diffusion-2-1"
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
pipe = pipe.to("cuda")
pipe.enable_attention_slicing()


bot = commands.Bot(intents=intents,command_prefix=commands.when_mentioned_or("!"))

mod = "ggml-model-gpt4all-falcon-q4_0.bin"
model = GPT4All(mod, model_path=model_path)

system_template = 'A chat between a curious user and an artificial intelligence assistant named Sparky.'


def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper

@to_thread
def image_generator(img_prompt):
    image = pipe(img_prompt).images[0]
    return image

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if bot.user.mentioned_in(message):
        system_template = f'A chat between a curious user named {message.author} and an artificial intelligence assistant named Sparky.'
        print(message.author)
        prompt = str(message.content).replace(f'<@{bot.user.id}> ', '') # Deletes AI Bot's user id
        print(prompt)
        message = await message.channel.send("Hold on while my AI mind is thinking...")
        with model.chat_session(system_template):
            tokens = []
            for token in model.generate(prompt, max_tokens=20, streaming=True):
                tokens.append(token)
                await message.edit(content="".join(str(x) for x in tokens))
                print(tokens)
    await bot.process_commands(message)

@bot.command(name='sparky')
async def sparky(ctx, *args):
    global mod 
    global modules

    try:
        print(args)
        if ("--help" in args) and (len(args) > 1):
            rspns = """
            -sparky: --help: too many arguments
            """
            await ctx.send(rspns)
        elif "--help" in args:
            rspns = f"""
            Usage: !sparky [-m] [expression]
                Config SparkyGPT using bash-like commands

                Options:
                    model: Configure Model
                        Options: 
                            -f, --file Takes The File Name of the Module

                            -c, --current Returns Current Model

                            -a, --available Returns Available Models

                    txt2image: Generate Image from Text
                        Options:
                            -p, --prompt "Create image from prompt. Example: !sparky txt2image -p "An Astronaut riding a horse on the moon"
                    
                    joke: Get a Random Joke
                        Options:
                            --dad-joke Random Dad Joke
                            --programming-joke Random Programming Joke
                            --knock-knock-joke Random Knock Knock Joke
                            --chuck-norris-joke Random Chuck Norris Joke
                            --help Open Up's the Joking Documentation

                        Available Models:
                            {modules}

            Copyright 2023 Alek Vasek
            Built using GPT4ALL & discord.py"""
            print(rspns)
            await ctx.send(rspns)
        elif args[0] == "txt2image":
            if ("--prompt" == args[1]) or ("-p" == args[1]):
                try: # Detects if a paremter has actually been passed
                    args[2]
                except IndexError:
                    rspns = f"""
                    sparky: option requires an argument '{t}'
                    Try '!sparky --help' for more information."""
                    await ctx.send(rspns)
                    return
                
                    
                if len(args) > 3:
                    rspns = f"""
                    -sparky: {args[1]}: too many arguments
                    """
                    await ctx.send(rspns)
                else:
                    pass
                
                await ctx.send("Generating Your Image! (Note: this could take 20-30 minutes)")
                await ctx.send("In the meantime feel free to continue chatting with me! Tip: Run '!sparky joke --dad-joke' to get a random dad joke")
                await asyncio.sleep(1)

                image_prompt = args[2]
                image = await image_generator(image_prompt)
                image.save("./discordimage.png")
                await ctx.send("Image Created!",file=discord.File("./discordimage.png"))
            else:
                rspns = f"""
                sparky: invalid command
                Try '!sparky --help' for more information."""
                await ctx.send(rspns)
        elif args[0] == "joke":
            if args[1] == "--dad-joke":
                if len(args) > 2:
                    rspns = f"""
                    -sparky: {args[1]}: too many arguments
                    """
                    await ctx.send(rspns)
                else:
                    pass

                await ctx.send(Joking.random_dad_joke())
            elif args[1] == "--programming-joke":
                if len(args) > 2:
                    rspns = f"""
                    -sparky: {args[1]}: too many arguments
                    """
                    await ctx.send(rspns)
                else:
                    pass

                await ctx.send(Joking.programming_joke())
            elif args[1] == "--knock-knock-joke":
                if len(args) > 2:
                    rspns = f"""
                    -sparky: {args[1]}: too many arguments
                    """
                    await ctx.send(rspns)
                else:
                    pass

                await ctx.send(Joking.Random_knock_knock_joke())
            elif args[1] == "--chuck-norris-joke":
                if len(args) > 2:
                    rspns = f"""
                    -sparky: {args[1]}: too many arguments
                    """
                    await ctx.send(rspns)
                else:
                    pass

                await ctx.send(Joking.chuck_norris_jokes())
            elif args[1] == "--help":
                if len(args) > 2:
                    rspns = f"""
                    -sparky: {args[1]}: too many arguments
                    """
                    await ctx.send(rspns)
                else:
                    pass

                await ctx.send(Joking.Help())
            else:
                print(args)
                rspns = f"""
                sparky: invalid command
                Try '!sparky --help' for more information."""
                await ctx.send(rspns)

        elif args[0] == "model":
            if ("--file" == args[1]) or ("-f" == args[1]):
                if "--file" in args:  # Args returns something like this: ("-m", "module.bin")
                    m = args.index("--file")
                    t = "--file"
                else:
                    m = args.index("-f")
                    t = "-f"

                exp = m+1

                try: # Detects if a paremter has actually been passed
                    args[exp]
                except IndexError:
                    rspns = f"""
                    sparky: option requires an argument '{t}'
                    Try '!sparky --help' for more information."""
                    await ctx.send(rspns)
                    return
                
                

                modules = [os.path.basename(x) for x in glob.glob(model_path + '/*.bin')] # Change '/*.bin' to `\*.bin` for Windows

                mod = args[exp]
                print(mod)
                print(modules)
                if mod in modules:
                    model = GPT4All(mod, allow_download=False, model_path=model_path)
                    await ctx.send(f"Set Model to {mod}")
                else:
                    rspns = f"""
                    -bash: {args[exp]}: model not found
                    
                    Sparky {t} found models:
                    {modules}"""
                    await ctx.send(rspns)
            elif ("--current" == args[1]) or ("-c" == args[1]):
                if len(args) == 2:
                    rspns = f"""
                    sparky: Current Model is {mod}
                    """
                    await ctx.send(rspns)
                    
                elif len(args) > 2:
                    rspns = f"""
                    -sparky: {args[1]}: too many arguments
                    """
                    await ctx.send(rspns)

            elif ("--available" == args[1]) or ("-a" == args[1]):
                if len(args) == 2:
                    rspns = f"""
                    sparky: Available Modules: {modules}
                    """
                    await ctx.send(rspns)
                    
                elif len(args) > 2:
                    rspns = f"""
                    -sparky: {args[1]}: too many arguments
                    """
                    await ctx.send(rspns)
            else:
                print(args)
                rspns = f"""
                sparky: missing operand
                Try '!sparky --help' for more information."""
                await ctx.send(rspns)

        elif () == args:
            rspns = f"""
            sparky: missing command
            Try '!sparky --help' for more information."""
            await ctx.send(rspns)
        else:
            print(args)
            rspns = f"""
            sparky: invalid command
            Try '!sparky --help' for more information."""
            await ctx.send(rspns)
    except Exception as e:
        rspns = f"""
        sparky: {e}
        Try '!sparky --help' for more information."""
        await ctx.send(rspns)
        
bot.run(TOKEN, log_handler=None)
