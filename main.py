"""
This is a discord bot for generating texts using OpenAI's GPT-4

Author: Stefan Rial
YouTube: https://youtube.com/@StefanRial
GitHub: https://https://github.com/StefanRial/AlexBot
E-Mail: mail.stefanrial@gmail.com
"""

import discord
import openai
from configparser import ConfigParser
from discord import app_commands

config_file = "config.ini"
config = ConfigParser(interpolation=None)
config.read(config_file)

SERVER_ID = config["discord"]["server_id"]
DISCORD_API_KEY = config["discord"][str("api_key")]
OPENAI_ORG = config["openai"][str("organization")]
OPENAI_API_KEY = config["openai"][str("api_key")]

GUILD = discord.Object(id=SERVER_ID)


class Client(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.conversation_history = []

    async def setup_hook(self):
        self.tree.copy_global_to(guild=GUILD)
        await self.tree.sync(guild=GUILD)

    async def on_message(self, message):
        if message.author == self.user:
            return

        input_content = message.content
        self.conversation_history.append({"role": "user", "content": input_content})

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=self.conversation_history
        )

        assistant_response = response["choices"][0]["message"]["content"]
        self.conversation_history.append({"role": "assistant", "content": assistant_response})
        parts = [assistant_response[i:i + 2000] for i in range(0, len(assistant_response), 2000)]
        for index, part in enumerate(parts):
            await message.channel.send(part)


alex_intents = discord.Intents.default()
alex_intents.messages = True
alex_intents.message_content = True
client = Client(intents=alex_intents)

openai.organization = OPENAI_ORG
openai.api_key = OPENAI_API_KEY
openai.Model.list()

client.run(DISCORD_API_KEY)