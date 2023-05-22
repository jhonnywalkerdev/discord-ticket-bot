import discord
from discord.ext import commands
from sqlcontroller import getAllStaffSql
from sqlcontroller import gerarTicketSql
from sqlcontroller import deleteTicketSql
from embed import mensagemSimple

clienterole = 708701626956775454
devrole = 805805829642125313
archivetickets = 954074660549566475 #id do canal para salvar tickets transcript
archiveticketscompra = 955989367892082749 #id do canal para salvar tickets transcript compra

async def criarTicket(bot, guild, author, tipo):
    if tipo == "tecnico":
        crole = discord.utils.get(guild.roles, id=int(clienterole))
        if crole in author.roles:
            role = discord.utils.get(guild.roles, id=int(devrole))
            categoria_tickets = bot.get_channel(int(archivetickets)).category
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False), 
                guild.me: discord.PermissionOverwrite(read_messages=True, read_message_history=True, send_messages=True),
                author: discord.PermissionOverwrite(read_messages=True, read_message_history=True, send_messages=True),
                role: discord.PermissionOverwrite(read_messages=True, read_message_history=True, send_messages=True),
            }
            channel = await guild.create_text_channel(name=tipo+"-"+author.name, overwrites=overwrites, category=categoria_tickets)
            await channel.send(embed=mensagemSimple(f"Ticket de Suporte Técnico", f"Olá {author.name}, explique sua situação detalhadamente para que nossa equipe possa te atender da melhor forma."))
            await channel.send(f"Atenção {role.mention}, {author.mention} acabou de criar este ticket.")
        else:
            await author.send(f"Você ainda não é um cliente para abrir um ticket técnico, abra um `!ticket comprar`.")
            return
    elif tipo == "comprar":
        categoria_tickets = bot.get_channel(int(archiveticketscompra)).category
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False), 
            guild.me: discord.PermissionOverwrite(read_messages=True, read_message_history=True, send_messages=True),
            author: discord.PermissionOverwrite(read_messages=True, read_message_history=True, send_messages=True),
        }
        channel = await guild.create_text_channel(name=tipo+"-"+author.name, overwrites=overwrites, category=categoria_tickets)
        await channel.send(embed=mensagemSimple(f"Ticket de Compra", f"Olá {author.name}, você abriu um ticket de compra, em que podemos te ajudar?"))
        await channel.send(f"Atenção <@671054083544842290>, {author.mention} acabou de criar este ticket.")
        await channel.send(f"Lembre-se {author.mention}, assim que você abriu este ticket, concordou com todos os nossos <#709795163244855377>.")
        
        
    await author.send(f"Você abriu um ticket ({tipo}), estou te enviando aqui o número de protocolo: "+str(channel.id))
    gerarTicketSql(channel, author, tipo)

async def closeTicket(channel):
    await channel.send("Ticked fechado. Será transcrito e deletado em alguns segundos...")
    deleteTicketSql(channel)