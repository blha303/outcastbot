#!/usr/bin/env python3
import discord
from io import BytesIO
from subprocess import check_output

client = discord.Client()

__cw_help = "Usage: !cw <message id or link>:<trigger warning message>, ... - e.g !cw 12345:trigger 2, 67890:trigger 3. Link required if cwing message in another channel (including \"server/channel/message\" IDs)"

async def cw(message, *args):
    if args == ([''],):
        try:
            await message.author.send(__cw_help)
        except discord.Forbidden:
            await message.channel.send(__cw_help)
        return

    for msg,trigger in args:
        if "/" in msg: # message link
            guild_id, channel_id, msg_id = msg.split("/")
            channel = await client.fetch_channel(channel_id)
            try:
                target_msg = await channel.fetch_message(msg_id)
            except discord.NotFound:
                yield f"{msg}:{trigger}", False, "Message not found"
                continue
            if not message.author.permissions_in(target_msg.channel).manage_messages:
                yield f"{msg}:{trigger}", False, "No 'Manage Messages' permission in target channel"
                continue
        else:
            try:
                target_msg = await message.channel.fetch_message(msg)
            except discord.NotFound:
                yield f"{msg}:{trigger}", False, "Message not found"
                continue
        content = f"""Message from {target_msg.author.mention} has been marked with a trigger warning. Below content has CW: {trigger}
||{target_msg.content}||"""
        files = []
        for a in target_msg.attachments:
            f = await a.to_file()
            if not a.is_spoiler():
                f.filename = f"SPOILER_{f.filename}"
            files.append(f)
        await target_msg.channel.send(content=content, files=files)
        await target_msg.delete()
        yield f"{msg}:{trigger}", True, ""

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.id == "698610551114432583": # cw-void
        await message.delete(delay=60*60*24)

    if message.content.lower().startswith("!clearvoid") and message.author.permissions_in(message.channel).manage_messages:
        channel = await client.fetch_channel("698610551114432583")
        async for msg in channel.history(limit=None):
            await msg.delete()
        await message.channel.send("void cleared")

    if message.content.lower().startswith("hi outcast"):
        print(get_emoji_count(message.guild))
        await message.channel.send("Hiya! I'm a work in progress, don't mind me. " + get_emoji_count(message.guild))

    if message.content.lower().startswith("!boop outcast") and message.author.permissions_in(message.channel).administrator:
        await message.channel.send("I've been booped! Back shortly...")
        await client.logout()

    if message.content.lower().startswith("!cw"):
        if message.author.permissions_in(message.channel).manage_messages:
            async for req, status, reason in cw(message, *map(lambda n: n.strip().split(":"), message.content[4:].replace("https://discordapp.com/channels/","").split(","))):
                if not status:
                    await message.channel.send(f"!cw failed on {req}: {reason}")
        else:
            await message.channel.send("No 'Manage Messages' permission in target channel")

@client.event
async def on_ready():
    print("Logged in as {} ({})".format(client.user.name, client.user.id))
    await client.get_channel(697503616587792415).send("Back online. Last update: {}\n<{}/commit/{}>".format(
        check_output(["git", "log", "-1", "--pretty=%B"]).strip().decode("utf-8"),
        check_output(["git", "remote", "get-url", "origin"]).strip().decode("utf-8"),
        check_output(["git", "log", "-1", "--pretty=%h"]).strip().decode("utf-8")
    ))
    if client.user.bot:
        print(discord.utils.oauth_url(client.user.id, permissions=discord.Permissions(8)))

if __name__ == "__main__":
    with open(".bottoken") as f:
        client.run(f.read().strip())
