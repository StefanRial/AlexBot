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

SYSTEM_MESSAGE = config["bot"]["system_message"]
HISTORY_LENGTH = config["bot"]["history_length"]


def trim_conversation_history(history, max_length=int(HISTORY_LENGTH)):
    if len(history) > max_length:
        history = history[-max_length:]
    return history


class Client(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.conversation_history = []

    async def setup_hook(self):
        self.tree.copy_global_to(guild=GUILD)
        await self.tree.sync(guild=GUILD)

    async def on_message(self, message):
        author = message.author

        if message.author == self.user:
            return

        input_content = message.content
        print(f"{message.author}: {input_content}")

        self.conversation_history.append({"role": "system", "content": f"The user is {author.display_name}. {SYSTEM_MESSAGE}"})
        self.conversation_history.append({"role": "user", "content": input_content})
        self.conversation_history = trim_conversation_history(self.conversation_history)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=self.conversation_history
            )

            assistant_response = response["choices"][0]["message"]["content"]
            self.conversation_history.append({"role": "assistant", "content": assistant_response})
            self.conversation_history = trim_conversation_history(self.conversation_history)

        except AttributeError:
            assistant_response = "It looks like you might have to update your openai package. You can do that with ```pip install --upgrade openai```"
        except ImportError:
            assistant_response = "You might not have all required packages installed. Make sure you install the openai and discord package"
        except openai.error.AuthenticationError:
            assistant_response = "It looks like you don't have access to the gpt-4 model. Please make sure you have been invited by openai and double check your openai API key and organization ID"
        except openai.error.RateLimitError:
            assistant_response = "Your rate has been limited. This might be because of too many requests or because your rate limit has been reached."
        except openai.error.Timeout:
            assistant_response = "My response is taking too long and I have received a timeout error."
        except openai.error.APIConnectionError:
            assistant_response = "I can't connect to the OpenAI servers at the moment. Please try again later!"

        if assistant_response is not None:
            parts = [assistant_response[i:i + 2000] for i in range(0, len(assistant_response), 2000)]
            for index, part in enumerate(parts):
                try:
                    print(f"Alex: {part}")
                    await message.channel.send(part)
                except discord.errors.Forbidden:
                    print("Alex: I am not able to send a message. Do I have the correct permissions on your server?")


alex_intents = discord.Intents.default()
alex_intents.messages = True
alex_intents.message_content = True
client = Client(intents=alex_intents)

openai.organization = OPENAI_ORG
openai.api_key = OPENAI_API_KEY
openai.Model.list()

client.run(DISCORD_API_KEY)
