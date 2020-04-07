#!/usr/bin/env python3
import discord
import re
from bs4 import BeautifulSoup as Soup
import requests

client = discord.Client()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower().startswith("hi outcast"):
        await message.channel.send("Hiya! I'm a work in progress, don't mind me.")

@client.event
async def on_ready():
    print("Logged in as {} ({})".format(client.user.name, client.user.id))
    if client.user.bot:
        print(discord.utils.oauth_url(client.user.id, permissions=discord.Permissions(8)))

if __name__ == "__main__":
    with open(".bottoken") as f:
        client.run(f.read().strip())
