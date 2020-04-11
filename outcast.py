#!/usr/bin/env python3
import discord
from io import BytesIO
import aiohttp

client = discord.Client()

__cw_help = "Usage: !cw <message id or link>:<trigger warning message>, ... - e.g !cw 12345:trigger 2, 67890:trigger 3. Link required if cwing message in another channel (including \"server/channel/message\" IDs)"
__emoji_help = """Usage:
!emoji import <custom emoji to import> <another custom emoji> ... - emoji will be imported using the name from the other server
!emoji image <name> - attach an image and specify the name to import. image must be smaller than 256kb"""

async def emoji(message):
    content = message.content[6:].strip()
    try:
        cmd, *args = content.split()
        if cmd not in ["import", "image"]:
            content = None
    except ValueError:
        content = None
    if not content:
        try:
            await message.author.send(__emoji_help)
        except discord.Forbidden:
            await message.channel.send(__emoji_help)
        return
    if cmd == "import":
        print(args)
    elif cmd == "image":
        img_bytes = await message.attachments[0].read()
        emoji = await message.server.create_custom_emoji(name=shortname, image=img_bytes, reason=f"Added by {message.author.name}#{message.author.discriminator}")
        await message.channel.send(str(emoji))

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

    if message.content.lower().startswith("hi outcast"):
        await message.channel.send("Hiya! I'm a work in progress, don't mind me.")

    if message.content.lower().startswith("!emoji"):
        if message.author.permissions_in(message.channel).manage_emojis:
            await emoji(message)
        else:
            await message.channel.send("No 'Manage Emoji' permission")

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
    if client.user.bot:
        print(discord.utils.oauth_url(client.user.id, permissions=discord.Permissions(8)))

if __name__ == "__main__":
    with open(".bottoken") as f:
        client.run(f.read().strip())
