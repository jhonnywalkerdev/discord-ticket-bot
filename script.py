from distutils import archive_util
import discord
import chat_exporter
import io
import time
from discord.ext import commands
from pymysql import NULL
from sqlcontroller import gerarSQL, gerarSQLLoja
from sqlcontroller import trocarIP
from sqlcontroller import downloadScript
from sqlcontroller import getLicensesSQL
from sqlcontroller import gerarTicketSql
from sqlcontroller import getAllTicketsSql
from sqlcontroller import getTicketChannelSql
from sqlcontroller import getTicketTypeSql
from sqlcontroller import getAllStaffSql
from sqlcontroller import addStaffSql
from ticket import criarTicket
from ticket import closeTicket
from embed import makePergunta
from embed import mensagemSimple

cargo_licensegenerator = 931612091515801670 #id do cargo que pode gerar licenca
canal_comandos = 931610577707630652 #id do canal que pode trocar ip
canal_openticket = 772872211391447041 #id do canal que pode abrir um ticket
canal_openticketcompra = 955997500345565205 #id do canal que pode abrir um ticket
archivetickets = 954074660549566475 #id do canal para salvar tickets transcript
archiveticketscompra = 955989367892082749 #id do canal para salvar tickets transcript compra
canal_vencimento = 954338677406990396 #id do canal de logs dos vencimentos
canalvalidarcompra = 955997500345565205
clienterole = 708701626956775454
devrole = 805805829642125313
fiverole = 662856494009548822

bot = commands.Bot(command_prefix="!")
TOKEN = ("OTY4MTYzMjk3MjgxMDY1MDIw.Yma2VQ.JPf0ahGKGqM4ppbsnKR-1C5rb6g")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}({bot.user.id})")

@bot.event
async def on_message(message):
    author = message.author
    if author.id == 968163297281065020: # prevent bug bot dm message - id do bot
        return
    if message.channel.id == canal_openticket or message.channel.id == canal_openticketcompra:
        if "!ticket" not in message.content:
            role = discord.utils.get(message.guild.roles, id=int(devrole))
            if not role in author.roles:
                await message.delete()
    if message.channel.id == canal_comandos:
        if "!ip" not in message.content or "!download" not in message.content:
            role = discord.utils.get(message.guild.roles, id=int(devrole))
            if not role in author.roles:
                await message.delete()
    if message.channel.category == bot.get_channel(int(archivetickets)).category:
        role = discord.utils.get(message.guild.roles, id=int(devrole))
        if not role in author.roles:
            staff = getAllStaffSql(devrole)
            for row in staff:
                user = await bot.fetch_user(int(row["user_id"]))
                await user.send(f"O cliente {author.mention}({author.display_name}) enviou uma nova mensagem no ticket <#{message.channel.id}>:\n- {message.content}")
    if message.channel.category == bot.get_channel(int(archiveticketscompra)).category:
        role = discord.utils.get(message.guild.roles, id=int(fiverole))
        if not role in author.roles:
            staff = getAllStaffSql(fiverole)
            for row in staff:
                user = await bot.fetch_user(int(row["user_id"]))
                await user.send(f"O cliente {author.mention}({author.display_name}) enviou uma nova mensagem no ticket <#{message.channel.id}>:\n- {message.content}")
    await bot.process_commands(message)

@bot.command()
async def m(ctx):
    role = discord.utils.get(ctx.guild.roles,id=cargo_licensegenerator)#id do cargo que pode gerar licenca
    author = ctx.message.author
    channel = ctx.message.channel
    def check(guess):
        return guess.author == author and guess.channel == channel
    if(role in author.roles):
        titulo = await makePergunta(ctx.message.author, bot, ctx.message.channel, check, "Qual o titulo?", "Qual o titulo?")
        mensagem = await makePergunta(ctx.message.author, bot, ctx.message.channel, check, "Qual a mensagem?", "Qual a mensagem?")
        await ctx.send(embed=mensagemSimple(titulo, mensagem))

@bot.command()
async def ver(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles,id=cargo_licensegenerator)#id do cargo que pode gerar licenca
    if(role in ctx.message.author.roles):
        licencasdosujeito = getLicensesSQL(member)
        embed=discord.Embed(title=f"Licenças de {member.name}", color=0x32c8fa)
        embed.set_author(name="FiveBrazil", url="https://fivebrazil.com.br", icon_url="https://cdn.discordapp.com/attachments/671501920040386600/931609292602228777/icon_degrade_azul.png")                
        for item in licencasdosujeito:
            embed.add_field(name="Script: ", value=item['script'], inline=True)
            embed.add_field(name="License: ", value=item['licenca'], inline=True)
            embed.add_field(name="IP: ", value=item['ip'], inline=True)
            embed.add_field(name="-", value="-", inline=False)
        await ctx.send(embed=embed)
        

@bot.command()
async def gerar(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles,id=cargo_licensegenerator)#id do cargo que pode gerar licenca
    author = ctx.message.author
    channel = ctx.message.channel
    def check(guess):
        return guess.author == author and guess.channel == channel
    if(role in ctx.message.author.roles):
        script = await makePergunta(ctx.message.author, bot, ctx.message.channel, check, "Qual o script?", "Qual o script?")
        if(script != None):
            ip = await makePergunta(ctx.message.author, bot, ctx.message.channel, check, "Qual o IP?", "Qual o IP?")
            if(ip != None):
                licenca = gerarSQL(member, script, ip)
                if(licenca == "Erro"):
                    await ctx.send(embed=mensagemSimple("Erro", "Licenca não foi gerada!"))
                else:
                    embed=discord.Embed(title="Licenca Gerada!", color=0x32c8fa)
                    embed.set_author(name="FiveBrazil", url="https://fivebrazil.com.br", icon_url="https://cdn.discordapp.com/attachments/671501920040386600/931609292602228777/icon_degrade_azul.png")
                    embed.add_field(name="Script: ", value=script, inline=False)
                    embed.add_field(name="License: ", value=licenca, inline=False)
                    embed.add_field(name="IP: ", value=ip, inline=False)
                    await ctx.send(embed=embed)

@bot.command()
async def gerarloja(ctx):
    role = discord.utils.get(ctx.guild.roles,id=cargo_licensegenerator)#id do cargo que pode gerar licenca
    author = ctx.message.author
    channel = ctx.message.channel
    def check(guess):
        return guess.author == author and guess.channel == channel
    if(role in ctx.message.author.roles):
        script = await makePergunta(ctx.message.author, bot, ctx.message.channel, check, "Qual o script?", "Qual o script?")
        if(script != None):
            quantidade = await makePergunta(ctx.message.author, bot, ctx.message.channel, check, "Qual a quantidade?", "Qual a quantidade?")
            print(quantidade)
            if(quantidade != None):
                resultado = gerarSQLLoja(script, quantidade)
                print(resultado)
                if(resultado != "Erro"):
                    embed=discord.Embed(title="Licenca Gerada!", color=0x32c8fa)
                    embed.set_author(name="FiveBrazil", url="https://fivebrazil.com.br", icon_url="https://cdn.discordapp.com/attachments/671501920040386600/931609292602228777/icon_degrade_azul.png")
                    embed.add_field(name="Script: ", value=script, inline=False)
                    embed.add_field(name="Quantidade Gerada: ", value=quantidade, inline=False)
                    await ctx.send(embed=embed)

@bot.command()
async def validar(ctx):
    author = ctx.message.author
    channel = ctx.message.channel
    def check(guess):
        return guess.author == author and guess.channel == channel
    if(ctx.channel.id == canalvalidarcompra):#id do canal que pode trocar ip
        licenca = await makePergunta(ctx.message.author, bot, ctx.message.channel, check, "Qual a sua licenca?", "Qual a sua licenca?")
        if(licenca != None):
            resultado = trocarIP(ctx.message.author, licenca, "127.0.0.1", True)
            resulmsg = await ctx.send(embed=mensagemSimple("Resultado", resultado))
            if("Erro" not in resultado):
                role = discord.utils.get(ctx.guild.roles, id=int(clienterole))
                await author.add_roles(role)
            time.sleep(15)
            await resulmsg.delete()
                           
@bot.command()
async def ip(ctx):
    author = ctx.message.author
    channel = ctx.message.channel
    # await ctx.message.delete()
    def check(guess):
        return guess.author == author and guess.channel == channel
    if(ctx.channel.id == canal_comandos):#id do canal que pode trocar ip
        licenca = await makePergunta(ctx.message.author, bot, ctx.message.channel, check, "Qual a sua licenca?", "Qual a sua licenca?")
        if(licenca != None):
            ip = await makePergunta(ctx.message.author, bot, ctx.message.channel, check, "Qual o novo IP?", "Qual o novo IP?")
            if(ip != None):
                resultado = trocarIP(ctx.message.author, licenca, ip)
                resulmsg = await ctx.send(embed=mensagemSimple("Resultado", resultado))
                time.sleep(15)
                await resulmsg.delete()

@bot.command()
async def download(ctx):
    author = ctx.message.author
    channel = ctx.message.channel
    def check(guess):
        return guess.author == author and guess.channel == channel
    if(ctx.channel.id == canal_comandos):#id do canal que pode fazer o download
        licenca = await makePergunta(ctx.message.author, bot, ctx.message.channel, check, "Qual a sua licenca?", "Qual a sua licenca?")
        if(licenca != None):
            downloaded,msg,script,version = downloadScript(ctx.message.author, licenca)
            if downloaded:
                await author.send(msg)
                resulmsg = await ctx.send(embed=mensagemSimple("Download","Download enviado no seu privado!"))
                channel = bot.get_channel(958929988365729832)
                await channel.send(f"**Download** solicitado por {author.mention}({author.name}):\n**Script:** {script}\n**Version:** {version}")
            else:
                resulmsg = await ctx.send(embed=mensagemSimple("Download",msg))
            time.sleep(3)
            await resulmsg.delete()
                           
@bot.command()
async def ticket(ctx,status="new"):
    guild = ctx.message.guild
    author = ctx.message.author
    if status == "close":
        tickets = getTicketChannelSql(ctx.channel)
        for row in tickets:
            if row["channel_id"] == str(ctx.channel.id): # verify if ticket is oppenend and exists
                await closeTicket(ctx.channel) # close and save info close on sql
                
                # transcript ticket
                transcript = await chat_exporter.export(
                    ctx.channel,
                )

                if transcript is None:
                    return

                transcript_file = discord.File(
                    io.BytesIO(transcript.encode()),
                    filename=f"transcript-{ctx.channel.name}.html",
                )
                
                channel = bot.get_channel(archivetickets) # channel who save tickets
                await channel.send(file=transcript_file) # finish transcript ticket

                await ctx.channel.delete() # delete actual ticket channel
            else: # if ticket are just closed
                msgfechado = await ctx.channel.send("Este ticket já está fechado.")
                await ctx.message.delete()
                time.sleep(3)
                await msgfechado.delete()
    else:
        if ctx.channel.id == canal_openticket or ctx.channel.id == canal_openticketcompra:
            if status == "tecnico" or status == "comprar":
                tipo = status
                try: 
                    anyticket = getAllTicketsSql(author)
                    if anyticket:
                        tickets = getTicketTypeSql(author)
                        liberarcriacao = 0
                        for row in tickets:
                            print(row)
                            if row["type"] == tipo:
                                liberarcriacao = liberarcriacao + 1
                            
                        if liberarcriacao > 0:
                            msgfechado = await ctx.channel.send("Você já tem um ticket deste tipo aberto.")
                            time.sleep(3)
                            await msgfechado.delete()
                        else:
                            await criarTicket(bot, guild, author, tipo)
                    else:
                        await criarTicket(bot, guild, author, tipo)
                except Exception as e:
                    print(e)
                    msgerror = await ctx.channel.send("Algum erro ocorreu no sistema que ocasionou uma falha ao criar seu ticket, envie uma print desta mensagem para nossa equipe.")
                    time.sleep(3)
                    await msgerror.delete()
            else:
                msgerrortipo = await ctx.channel.send("Você não especificou o tipo do seu ticket.")
                time.sleep(3)
                await msgerrortipo.delete()
            await ctx.message.delete()
        else:
            msgerrorchannel = await ctx.channel.send("Você não pode abrir um ticket utilizando este canal.")
            time.sleep(3)
            await msgerrorchannel.delete()
        await ctx.message.delete()

@bot.command()
async def dm(ctx, user: discord.User = None, *, value = None):
    if user == ctx.message.author:
        await ctx.send("Você não pode mencionar a si mesmo")
    else:
        await ctx.message.delete()
    if user == None:
        errormsg = await ctx.send('Por favor mencione qualquer usuário, sintaxe correta: `!dm @mention message`.')
        time.sleep(3)
        await errormsg.delete()
    else:
        if value == None:
            errormsg = await ctx.send('Por favor escreva uma mensagem para ser enviada, sintaxe correta: `!dm @mention message`.')
            time.sleep(3)
            await errormsg.delete()
        else:
            await user.send(value)
            await ctx.message.author.send(f'**Enviado no privado de {user.mention}.**\n'+value)

@bot.command()
async def poke(ctx, user: discord.User = None):
    if user == ctx.message.author:
        await ctx.send("Você não pode mencionar a si mesmo")
        time.sleep(3)
        await errormsg.delete()
    else:
        await ctx.message.delete()
    if user == None:
        errormsg = await ctx.send('Por favor mencione qualquer usuário, sintaxe correta: `!poke @mention`.')
        time.sleep(3)
        await errormsg.delete()
    else:
        await user.send(f"> **{user.mention}, você recebeu uma resposta em seu ticket**.\nPara ir diretamente até o canal, **clique em <#{ctx.channel.id}>**.\n*Geralmente você receberá essa mensagem se não tiver respondido nossa equipe a algum tempo ou caso nossa equipe necessite de uma resposta para solucionar o seu problema o mais rápido possível.*")
        await ctx.send(f"*Poke enviado no privado de {user.display_name}.*")

@bot.command()
async def vencimento(ctx, user: discord.User = None):
    author = ctx.message.author
    channel = ctx.message.channel
    if user == ctx.message.author:
        await ctx.send("Você não pode mencionar a si mesmo")
        time.sleep(3)
        await errormsg.delete()
    else:
        await ctx.message.delete()
    if user == None:
        errormsg = await ctx.send('Por favor mencione qualquer usuário, sintaxe correta: `!vencimento @mention`.')
        time.sleep(3)
        await errormsg.delete()
    else:
        def check(guess):
            return guess.author == author and guess.channel == channel
        servico = await makePergunta(author, bot, channel, check, "Qual o serviço?", "Divulgação\nVPS 2gb\nVPS 4gb\nVPS 8gb\njw_vip")
        if(servico != None):
            vencimento = await makePergunta(author, bot, channel, check, "Qual a data de vencimento?", "Digite a data de vencimento:")
            if(vencimento != None):
                canal = bot.get_channel(canal_vencimento)
                m = f"> **NOTIFICAÇÃO DE VENCIMENTO**.\nOlá {user.mention}({user.display_name}), só estou passando aqui para te lembrar que seu serviço **{servico}** tem validade até **{vencimento}**. Qualquer pagamento deve ser feito em nosso site https://fivebrazil.com.br ou no privado do Jhonny Walker.\n*OBS: Caso não realize o pagamento da mensalidade, após a data informada, seu serviço poderá ser encerrado a qualquer momento. Caso já tenha realizado o pagamento, apenas ignore esta mensagem.*"
                await user.send(m)
                await canal.send(m)

@bot.command()
async def addstaff(ctx, user: discord.User = None):
    author = ctx.message.author
    channel = ctx.message.channel
    if user == None:
        errormsg = await ctx.send('Por favor mencione qualquer usuário, sintaxe correta: `!addstaff @mention`.')
        time.sleep(3)
        await errormsg.delete()
    else:
        def check(guess):
            return guess.author == author and guess.channel == channel
        perm = await makePergunta(author, bot, channel, check, "Qual cargo?", "Mencione o cargo que deseja setar para o staff:")
        if(perm != None):
            permissao = perm.replace("<", "").replace(">", "").replace("@", "").replace("&", "")
            role = discord.utils.get(ctx.guild.roles, id=int(permissao))
            m = f"{user.mention}({user.display_name}) foi adicionado como staff de cargo {role.mention}"
            await channel.send(m)
            await user.add_roles(role)
            addStaffSql(user,role)

if __name__ == "__main__":
    bot.run(TOKEN)
