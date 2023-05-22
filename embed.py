import discord
from discord.ext import commands
import asyncio

async def makePergunta(author, bot, channel, check, pergunta, descricao):
    embed=discord.Embed(title="Pergunta", color=0x32c8fa)
    embed.set_author(name="FiveBrazil - Gerenciamento", url="https://fivebrazil.com.br", icon_url="https://cdn.discordapp.com/attachments/671501920040386600/931609292602228777/icon_degrade_azul.png")
    embed.add_field(name=pergunta, value=descricao, inline=True)
    embed.set_footer(text="Responda cada pergunta em até 1 minuto.", icon_url="https://thumbs.gfycat.com/BitterEarnestBeardeddragon-small.gif")
    msgid = await channel.send(embed=embed)
    try:
        guess = await bot.wait_for('message', check=check, timeout=60.0)
        nome = guess.content.replace("|", "").replace("'", "").replace('"', '').replace('=', '').replace('ALTER', '').replace('UPDATE', '').replace('TRUNCATE', '').replace('ELIMINATE', '').replace('DELETE', '').replace('INSERT', '').replace('WHERE', '').replace('alter', '').replace('update', '').replace('truncate', '').replace('eliminate', '').replace('delete', '').replace('insert', '').replace('where', '')
        await msgid.delete()
        return nome
    except asyncio.TimeoutError:
        await msgid.delete()
        return None

def mensagemSimple(mensagem, submensagem):
    embed=discord.Embed(title="Gerenciamento", color=0x32c8fa)
    embed.set_author(name="FiveBrazil", url="https://fivebrazil.com.br", icon_url="https://cdn.discordapp.com/attachments/671501920040386600/931609292602228777/icon_degrade_azul.png")
    embed.add_field(name=mensagem, value=submensagem, inline=True)
    return embed