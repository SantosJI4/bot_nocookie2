# Importa as bibliotecas necessárias
import os
import discord  # Biblioteca para interagir com a API do Discord
from discord.ext import commands, tasks  # Extensão para criar bots com comandos
import random  # Para funcionalidades de diversão, como rolar dados
from discord.ui import Button, View
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import aiohttp  # Biblioteca para fazer requisições HTTP
import asyncio
import json

# Função para carregar as configurações do arquivo JSON
def carregar_configuracoes():
    try:
        with open("config.json", "r") as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        # Configuração padrão caso o arquivo não exista
        return {
            "prefixo": "-t ",
            "canal_boas_vindas": None,
            "canal_carro_forte": None,
            "cargo_nao_verificado": None,
            "cargo_verificado": None
        }

# Função para salvar as configurações no arquivo JSON
def salvar_configuracoes(config):
    with open("config.json", "w") as arquivo:
        json.dump(config, arquivo, indent=4)

# Carrega as configurações ao iniciar o bot
configuracoes = carregar_configuracoes()


# Configura os intents do bot para permitir eventos como mensagens e membros
intents = discord.Intents.all()

# Cria uma instância do bot com o prefixo "-t" e os intents configurados
bot = commands.Bot(command_prefix="-t ", intents=intents)

@bot.event
async def on_ready():
    # Define o status do bot
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening, name="comandos dos usuários 🎧"),  # Status "Jogando"
        status=discord.Status.online  # Define o status como "Online"
    )
    print(f"Bot conectado como {bot.user}")

# Comando: Alterar o prefixo do bot
@bot.command()
@commands.has_permissions(administrator=True)
async def set_prefixo(ctx, novo_prefixo: str):
    configuracoes["prefixo"] = novo_prefixo
    salvar_configuracoes(configuracoes)
    bot.command_prefix = novo_prefixo
    await ctx.send(f"✅ O prefixo do bot foi alterado para `{novo_prefixo}`.")

# Comando: Configurar o canal de boas-vindas
@bot.command()
@commands.has_permissions(administrator=True)
async def set_canal_boas_vindas(ctx, canal: discord.TextChannel):
    configuracoes["canal_boas_vindas"] = canal.id
    salvar_configuracoes(configuracoes)
    await ctx.send(f"✅ O canal de boas-vindas foi configurado para {canal.mention}.")

# Comando: Configurar o canal do carro-forte
@bot.command()
@commands.has_permissions(administrator=True)
async def set_canal_carro_forte(ctx, canal: discord.TextChannel):
    configuracoes["canal_carro_forte"] = canal.id
    salvar_configuracoes(configuracoes)
    await ctx.send(f"✅ O canal do carro-forte foi configurado para {canal.mention}.")

    

# Comando: Configurar o cargo "Não Verificado"
@bot.command()
@commands.has_permissions(administrator=True)
async def set_cargo_nao_verificado(ctx, cargo: discord.Role):
    configuracoes["cargo_nao_verificado"] = cargo.id
    salvar_configuracoes(configuracoes)
    await ctx.send(f"✅ O cargo 'Não Verificado' foi configurado para `{cargo.name}`.")

# Comando: Configurar o cargo "Verificado"
@bot.command()
@commands.has_permissions(administrator=True)
async def set_cargo_verificado(ctx, cargo: discord.Role):
    configuracoes["cargo_verificado"] = cargo.id
    salvar_configuracoes(configuracoes)
    await ctx.send(f"✅ O cargo 'Verificado' foi configurado para `{cargo.name}`.")

# Evento: Quando o bot estiver pronto
@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")
    print("Sistema Iniciado")

# Evento: Mensagem de boas-vindas para novos membros
@bot.event
async def on_member_join(member: discord.Member):
    canal = bot.get_channel(975154856643944521)  # Substitua pelo ID do canal de boas-vindas
    cargo = member.guild.get_role(975445235557609492)  # Substitua pelo ID do cargo que deseja adicionar

    if cargo:
        await member.add_roles(cargo)  # Adiciona o cargo ao membro
        if canal:
            embed = discord.Embed(
                title="🎉 Bem-vindo ao servidor! 🎉",
                description=f"Olá, {member.mention}! Você recebeu o cargo `{cargo.name}` automaticamente. Aproveite o servidor! 😊",
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=member.avatar.url)
            await canal.send(embed=embed)
@bot.event
async def on_member_join(member: discord.Member):
    canal = bot.get_channel(975154856643944521)  # Substitua pelo ID do canal de registro
    cargo_nao_verificado = member.guild.get_role(1366099591052787823)  # Substitua pelo ID do cargo "Não Verificado"

    if cargo_nao_verificado:
        await member.add_roles(cargo_nao_verificado)  # Adiciona o cargo "Não Verificado" ao membro

    # Cria um botão para registro
    botao_registro = Button(label="Registrar", style=discord.ButtonStyle.green)

    # Função chamada quando o botão é clicado
    async def callback(interaction: discord.Interaction):
        cargo_verificado = member.guild.get_role(975445754955055114)  # Substitua pelo ID do cargo "Verificado"
        if cargo_verificado:
            await member.add_roles(cargo_verificado)  # Adiciona o cargo "Verificado"
            await member.remove_roles(cargo_nao_verificado)  # Remove o cargo "Não Verificado"
            await interaction.response.send_message(f"✅ {member.mention}, você foi registrado com sucesso!", ephemeral=True)

    botao_registro.callback = callback

    # Cria uma view para adicionar o botão
    view = View()
    view.add_item(botao_registro)

    # Envia a mensagem de registro no canal
    if canal:
        await canal.send(
            content=f"👋 Olá, {member.mention}! Clique no botão abaixo para se registrar e acessar o servidor.",
            view=view
        )

# Comando: Chamar o registro manualmente
@bot.command()
@commands.has_permissions(administrator=True)  # Apenas administradores podem usar este comando
async def r(ctx):
    # IDs dos cargos e canal
    canal = ctx.channel  # Usa o canal onde o comando foi executado
    cargo_nao_verificado = ctx.guild.get_role(1366099591052787823)  # Substitua pelo ID do cargo "Não Verificado"
    cargo_verificado = ctx.guild.get_role(975445754955055114)  # Substitua pelo ID do cargo "Verificado"

    # Cria um botão para registro
    botao_registro = Button(label="Registrar", style=discord.ButtonStyle.green)

    # Função chamada quando o botão é clicado
    async def callback(interaction: discord.Interaction):
        membro = interaction.user  # Obtém o membro que clicou no botão
        if cargo_verificado:
            await membro.add_roles(cargo_verificado)  # Adiciona o cargo "Verificado"
            await membro.remove_roles(cargo_nao_verificado)  # Remove o cargo "Não Verificado"
            await interaction.response.send_message(f"✅ {membro.mention}, você foi registrado com sucesso!", ephemeral=True)

    botao_registro.callback = callback

    # Cria uma view para adicionar o botão
    view = View()
    view.add_item(botao_registro)

    # Envia a mensagem de registro no canal
    await canal.send(
        content="👋 Clique no botão abaixo para se registrar e acessar o servidor.",
        view=view
    )

# Comando: Falar algo (diversão)
@bot.command()
async def falar(ctx, *, texto):
    await ctx.send(texto)

# Comando: Enviar embed com comandos
@bot.command()
async def ajuda(ctx: commands.Context):
    embed = discord.Embed(
        title="📖 Central de Ajuda",
        description="Aqui estão os comandos disponíveis no bot. Use o prefixo `-t` antes de cada comando.",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="🎮 Diversão",
        value="`falar [texto]` - O bot repete o texto enviado.\n"
              "`dado` - Rola um dado de 6 lados.\n"
              "`abracar [@membro]` - Dá um abraço em outro membro.\n"
              "`nivel [@membro]` - Consulta seu nível.",
        inline=False
    )
    embed.add_field(
        name="🛠️ Moderação",
        value="`ban [@membro] [motivo]` - Bane um membro do servidor.\n"
              "`kick [@membro] [motivo]` - Expulsa um membro do servidor.\n"
              "`clear [quantidade]` - Apaga mensagens no canal atual.\n"
              "`add_cargo [@membro] [@cargo]` - Adiciona um cargo a um membro.\n"
              "`remove_cargo [@membro] [@cargo]` - Remove um cargo de um membro.\n"
              "`r` - Registra membros manualmente.",
        inline=False
    )
    embed.add_field(
        name="💰 Economia",
        value="`saldo` - Ver seu saldo na carteira e no banco.\n"
              "`trabalhar` - Trabalhe para ganhar dinheiro (a cada 8 horas).\n"
              "`depositar [quantia]` - Deposite dinheiro no banco.\n"
              "`sacar [quantia]` - Saque dinheiro do banco.\n"
              "`transferir [@membro] [quantia]` - Transfira dinheiro para outro usuário.\n"
              "`loja` - Veja os itens disponíveis para compra.\n"
              "`comprar [item]` - Compre um item da loja.\n"
              "`roubar [@membro]` - Roube dinheiro de outro usuário (necessário ter uma arma).\n"
              "`ranking` - Veja o ranking dos usuários mais ricos.\n"
              "`ajuda_economia` - Mostra apenas os comandos de economia.",
        inline=False
    )
    embed.add_field(
        name="💍 Relacionamentos",
        value="`casar [@membro]` - Case-se com outro usuário.\n"
              "`divorciar` - Divorcie-se do seu parceiro.",
        inline=False
    )
    embed.add_field(
        name="📋 Outros",
        value="`ajuda` - Mostra esta mensagem de ajuda.\n"
              "`ola` - O bot responde com uma saudação.\n"
              "`serverinfo` - Mostra informações sobre o servidor.\n"
              "`userinfo [@membro]` - Mostra informações sobre um usuário.",
        inline=False
    )
    embed.set_footer(
        text="Bot de exemplo • Desenvolvido por Maurício Santana",
        icon_url="https://i.imgur.com/3ZQ3ZKq.png"
    )
    embed.set_thumbnail(url="https://i.imgur.com/3ZQ3ZKq.png")  # Adiciona um ícone ao embed
    await ctx.reply(embed=embed)

# Comando: Rolar um dado (diversão)
@bot.command()
async def dado(ctx):
    numero = random.randint(1, 6)
    await ctx.send(f"🎲 Você rolou o número: {numero}")
# Comando: Banir um membro (moderação)
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, motivo="Sem motivo especificado"):
    try:
        await member.ban(reason=motivo)
        await ctx.send(f"🚫 {member.mention} foi banido. Motivo: {motivo}")
    except discord.Forbidden:
        await ctx.send("❌ Não tenho permissões suficientes para expulsar este membro.")
    except discord.HTTPException as e:
        await ctx.send(f"❌ Ocorreu um erro ao tentar expulsar o membro: {e}")

# Comando: Expulsar um membro (moderação)
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, motivo="Sem motivo especificado"):
    try:
        await member.kick(reason=motivo)
        await ctx.send(f"👢 {member.mention} foi expulso. Motivo: {motivo}")
    except discord.Forbidden:
        await ctx.send("❌ Não tenho permissões suficientes para banir este membro.")
    except discord.HTTPException as e:
        await ctx.send(f"❌ Ocorreu um erro ao tentar banir o membro: {e}")
# add cargo
@bot.command()
@commands.has_permissions(manage_roles=True)  # Verifica se o usuário tem permissão para gerenciar cargos
async def add_cargo(ctx, member: discord.Member, cargo: discord.Role):
    try:
        await member.add_roles(cargo)  # Adiciona o cargo ao membro
        await ctx.send(f"✅ O cargo `{cargo.name}` foi adicionado a {member.mention}.")
    except discord.Forbidden:
        await ctx.send("❌ Não tenho permissões suficientes para adicionar este cargo.")
    except discord.HTTPException as e:
        await ctx.send(f"❌ Ocorreu um erro ao tentar adicionar o cargo: {e}")
# remove cargo
@bot.command()
@commands.has_permissions(manage_roles=True)  # Verifica se o usuário tem permissão para gerenciar cargos
async def remove_cargo(ctx, member: discord.Member, cargo: discord.Role):
    try:
        await member.remove_roles(cargo)  # Remove o cargo do membro
        await ctx.send(f"✅ O cargo `{cargo.name}` foi removido de {member.mention}.")
    except discord.Forbidden:
        await ctx.send("❌ Não tenho permissões suficientes para remover este cargo.")
    except discord.HTTPException as e:
        await ctx.send(f"❌ Ocorreu um erro ao tentar remover o cargo: {e}")
# apagar as mensagens
# Comando: Limpar mensagens
@bot.command()
@commands.has_permissions(manage_messages=True)  # Verifica se o usuário tem permissão para gerenciar mensagens
async def clear(ctx, quantidade: int):
    try:
        # Apaga as mensagens no canal atual
        await ctx.channel.purge(limit=quantidade)
        # Envia uma mensagem confirmando a limpeza (e apaga a mensagem após 5 segundos)
        confirmacao = await ctx.send(f"🧹 {quantidade} mensagens foram apagadas.")
        await confirmacao.delete(delay=5)
    except discord.Forbidden:
        await ctx.send("❌ Não tenho permissões suficientes para apagar mensagens.")
    except discord.HTTPException as e:
        await ctx.send(f"❌ Ocorreu um erro ao tentar apagar as mensagens: {e}")

# Comando: Responder com "Olá"
@bot.tree.command()
async def ola(interact: discord.Interaction):
    await interact.response.send_message(f"Olá, {interact.user.name}! 😊")

# Evento: Responder quando o bot for mencionado
@bot.event
async def on_message(msg: discord.Message):
    if msg.author.bot:
        return

    # Verifica se o bot foi mencionado
    if bot.user in msg.mentions:
        embed = discord.Embed(
            title="🎉 Olá! 🎉",
            description=f"Olá, {msg.author.mention}! Estou aqui para ajudar. Use `-t ajuda` para ver meus comandos!",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=msg.author.avatar.url)
        embed.set_image(url="https://mir-s3-cdn-cf.behance.net/project_modules/1400/aedf7c162029523.63cf1b888ac5b.jpg")
        embed.set_footer(text="Equipe do Servidor", icon_url="https://i.ytimg.com/vi/hiBHn-S8J2E/maxresdefault.jpg")
        await msg.channel.send(embed=embed)

    # Processa comandos normalmente
    await bot.process_commands(msg)

@bot.event
async def on_message(msg: discord.Message):
    if msg.author.bot:
        return
    if msg.content.lower() == "boa noite":
        await msg.channel.send(f"Boa noite, {msg.author.mention} a noite está linda hoje.")
    if msg.content.lower() == "bom dia":
        await msg.channel.send(f"bom dia, {msg.author.mention} o dia está lindo hoje.")
    if msg.content.lower() == "boa tarde":
        await msg.channel.send(f"Boa tarde, {msg.author.mention} a tarde está linda hoje.")
    if msg.content.lower() == "preciso de ajuda":
        await msg.channel.send(f"olá {msg.author.mention} está precisando de ajuda. me chama com `-t ajuda`")
    await bot.process_commands(msg)

# Comando: Exibir informações do servidor
@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild  # Obtém o servidor atual
    embed = discord.Embed(
        title=f"Informações do Servidor: {guild.name}",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)  # Adiciona o ícone do servidor
    embed.add_field(name="👑 Dono", value=guild.owner.mention, inline=True)
    embed.add_field(name="📅 Criado em", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="👥 Membros", value=guild.member_count, inline=True)
    embed.add_field(name="💬 Canais de Texto", value=len(guild.text_channels), inline=True)
    embed.add_field(name="🔊 Canais de Voz", value=len(guild.voice_channels), inline=True)
    embed.add_field(name="🌍 Região", value=guild.preferred_locale, inline=True)
    embed.set_footer(text=f"ID do Servidor: {guild.id}")
    await ctx.send(embed=embed)

# Comando: Exibir informações do usuário
@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author  # Usa o autor do comando se nenhum membro for mencionado

    embed = discord.Embed(
        title=f"Informações do Usuário: {member.name}",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.avatar.url)  # Adiciona o avatar do usuário
    embed.add_field(name="🆔 ID", value=member.id, inline=True)
    embed.add_field(name="📅 Conta Criada em", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="📅 Entrou no Servidor em", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="👑 Cargo Mais Alto", value=member.top_role.mention, inline=True)
    embed.add_field(name="📜 Cargos", value=", ".join([role.mention for role in member.roles if role != ctx.guild.default_role]), inline=False)
    embed.set_footer(text=f"Solicitado por {ctx.author.name}", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)

economia = {}
itens = {}
user_levels = {}
roubos = {}



empregos = {
    "Desempregado": 0,
    "Faxineiro": 1,
    "Vendedor": 5,
    "Gerente": 10,
    "Empresário": 15,
    "Policial": 20
}

# Função para inicializar os dados de um usuário
# Função para inicializar os dados de um usuário
def inicializar_usuario(user_id):
    if user_id not in economia:
        economia[user_id] = {"carteira": 0, "banco": 0, "casado_com": None, "emprego": "Desempregado"}
    if user_id not in itens:
        itens[user_id] = {"arma": 0}
    if user_id not in user_levels:
        user_levels[user_id] = {"nivel": 1, "exp": 0}

def calcular_exp_para_proximo_nivel(nivel):
    return 100 + (nivel * 50)

@bot.command()
async def nivel(ctx):
    user_id = ctx.author.id
    inicializar_usuario(user_id)

    nivel = user_levels[user_id]["nivel"]
    exp = user_levels[user_id]["exp"]
    exp_para_proximo_nivel = calcular_exp_para_proximo_nivel(nivel)
    emprego = economia[user_id]["emprego"]

    embed = discord.Embed(
        title=f"📊 Status de {ctx.author.name}",
        description=f"**Nível:** {nivel}\n**EXP:** {exp}/{exp_para_proximo_nivel}\n**Emprego:** {emprego}",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

# Evento: Ganhar EXP ao enviar mensagens
@bot.event
async def on_message(msg: discord.Message):
    if msg.author.bot:
        return

    user_id = msg.author.id
    inicializar_usuario(user_id)

    # Adiciona EXP aleatório entre 5 e 15
    exp_ganho = random.randint(5, 15)
    user_levels[user_id]["exp"] += exp_ganho

    # Verifica se o usuário passou de nível
    nivel_atual = user_levels[user_id]["nivel"]
    exp_para_proximo_nivel = calcular_exp_para_proximo_nivel(nivel_atual)

    if user_levels[user_id]["exp"] >= exp_para_proximo_nivel:
        user_levels[user_id]["nivel"] += 1
        user_levels[user_id]["exp"] -= exp_para_proximo_nivel

        # Atualiza o emprego se o nível permitir
        for emprego, nivel_minimo in empregos.items():
            if user_levels[user_id]["nivel"] >= nivel_minimo:
                economia[user_id]["emprego"] = emprego

        await msg.channel.send(
            f"🎉 Parabéns, {msg.author.mention}! Você subiu para o nível {user_levels[user_id]['nivel']} e agora é um **{economia[user_id]['emprego']}**!"
        )

    # Processa comandos normalmente
    await bot.process_commands(msg)



# Comando: Ver saldo
@bot.command()
async def saldo(ctx):
    user_id = ctx.author.id
    inicializar_usuario(user_id)

    carteira = economia[user_id]["carteira"]
    banco = economia[user_id]["banco"]

    embed = discord.Embed(
        title=f"💰 Saldo de {ctx.author.name}",
        color=discord.Color.gold()
    )
    embed.add_field(name="🪙 Carteira", value=f"R$ {carteira}", inline=True)
    embed.add_field(name="🏦 Banco", value=f"R$ {banco}", inline=True)
    embed.set_footer(text="Use os comandos de economia para gerenciar seu dinheiro!")
    await ctx.send(embed=embed)

@bot.command()
async def loja(ctx):
    embed = discord.Embed(
        title="🛒 Loja",
        description="Compre itens para usar no sistema de economia!",
        color=discord.Color.blue()
    )
    embed.add_field(name="🔫 Arma", value="Preço: R$ 500\nUse para roubar outros usuários.", inline=False)
    embed.set_footer(text="Use `-t comprar [item]` para comprar um item.")
    await ctx.send(embed=embed)

@bot.command()
async def comprar(ctx, item: str):
    user_id = ctx.author.id
    inicializar_usuario(user_id)

    if item.lower() == "arma":
        preco = 500
        if economia[user_id]["carteira"] < preco:
            await ctx.send("❌ Você não tem dinheiro suficiente para comprar uma arma.")
            return
        economia[user_id]["carteira"] -= preco
        itens[user_id]["arma"] += 1
        await ctx.send(f"✅ {ctx.author.mention}, você comprou uma arma! 🔫")
    else:
        await ctx.send("❌ Este item não está disponível na loja.")

@bot.command()
async def roubar(ctx, member: discord.Member):
    user_id = ctx.author.id
    alvo_id = member.id
    inicializar_usuario(user_id)
    inicializar_usuario(alvo_id)

    if itens[user_id]["arma"] <= 0:
        await ctx.send("❌ Você precisa de uma arma para roubar outro usuário.")
        return

    if economia[alvo_id]["carteira"] <= 0:
        await ctx.send(f"❌ {member.mention} não tem dinheiro na carteira para ser roubado.")
        return

    sucesso = random.choice([True, False])
    if sucesso:
        valor_roubado = random.randint(50, min(200, economia[alvo_id]["carteira"]))
        economia[user_id]["carteira"] += valor_roubado
        economia[alvo_id]["carteira"] -= valor_roubado
        itens[user_id]["arma"] -= 1  # Consome uma arma
        roubos[user_id] = {"alvo": alvo_id, "tempo": datetime.now()}
        await ctx.send(f"💰 {ctx.author.mention} roubou R$ {valor_roubado} de {member.mention}! 🔫")
    else:
        await ctx.send(f"❌ {ctx.author.mention}, você falhou ao tentar roubar {member.mention}.")

@bot.command()
async def prender(ctx, member: discord.Member):
    user_id = ctx.author.id
    ladrão_id = member.id
    inicializar_usuario(user_id)
    inicializar_usuario(ladrão_id)

    if economia[user_id]["emprego"] != "Policial":
        await ctx.send("❌ Apenas policiais podem prender ladrões!")
        return

    if ladrão_id not in roubos:
        await ctx.send(f"❌ {member.mention} não cometeu nenhum roubo recentemente.")
        return

    tempo_roubo = roubos[ladrão_id]["tempo"]
    if datetime.now() - tempo_roubo > timedelta(minutes=5):
        del roubos[ladrão_id]
        await ctx.send(f"❌ O tempo para prender {member.mention} expirou.")
        return

    # Prende o ladrão
    del roubos[ladrão_id]
    multa = random.randint(100, 300)
    economia[ladrão_id]["carteira"] -= multa
    economia[user_id]["carteira"] += multa
    await ctx.send(f"🚔 {ctx.author.mention} prendeu {member.mention} e recebeu uma multa de R$ {multa}!")

# Comando: Casar
@bot.command()
async def casar(ctx, member: discord.Member):
    user_id = ctx.author.id
    alvo_id = member.id
    inicializar_usuario(user_id)
    inicializar_usuario(alvo_id)

    if economia[user_id]["casado_com"] is not None:
        await ctx.send("❌ Você já está casado!")
        return

    if economia[alvo_id]["casado_com"] is not None:
        await ctx.send(f"❌ {member.mention} já está casado!")
        return

    economia[user_id]["casado_com"] = alvo_id
    economia[alvo_id]["casado_com"] = user_id
    await ctx.send(f"💍 {ctx.author.mention} e {member.mention} agora estão casados!")

# Comando: Divorciar
@bot.command()
async def divorciar(ctx):
    user_id = ctx.author.id
    inicializar_usuario(user_id)

    if economia[user_id]["casado_com"] is None:
        await ctx.send("❌ Você não está casado!")
        return

    parceiro_id = economia[user_id]["casado_com"]
    economia[user_id]["casado_com"] = None
    economia[parceiro_id]["casado_com"] = None
    parceiro = await bot.fetch_user(parceiro_id)
    await ctx.send(f"💔 {ctx.author.mention} e {parceiro.mention} agora estão divorciados.")

# Comando: Ranking dos Mais Ricos
@bot.command()
async def ranking(ctx):
    # Ordena os usuários pelo total de dinheiro (carteira + banco)
    ranking = sorted(economia.items(), key=lambda x: x[1]["carteira"] + x[1]["banco"], reverse=True)
    embed = discord.Embed(
        title="🏆 Ranking dos Mais Ricos",
        color=discord.Color.gold()
    )
    for i, (user_id, dados) in enumerate(ranking[:10], start=1):  # Mostra os 10 mais ricos
        usuario = await bot.fetch_user(user_id)
        total = dados["carteira"] + dados["banco"]
        embed.add_field(name=f"{i}º {usuario.name}", value=f"R$ {total}", inline=False)
    await ctx.send(embed=embed)

ultimo_trabalho = {}

# Comando: Trabalhar
@bot.command()
async def trabalhar(ctx):
    user_id = ctx.author.id
    inicializar_usuario(user_id)
    emprego = economia[user_id]["emprego"]
    if emprego == "Desempregado":
        await ctx.send("❌ Você está desempregado! Suba de nível para desbloquear empregos.")
        
        return
    
    pagamentos = {
        "Faxineiro": 50,
        "Vendedor": 100,
        "Gerente": 200,
        "Empresário": 500,
        "Policial": 300
    }
    pagamento = pagamentos.get(emprego, 0)
    economia[user_id]["carteira"] += pagamento
    # Verifica se o usuário já trabalhou antes
    agora = datetime.now()
    if user_id in ultimo_trabalho:
        diferenca = agora - ultimo_trabalho[user_id]
        if diferenca < timedelta(hours=8):
            tempo_restante = timedelta(hours=8) - diferenca
            horas, resto = divmod(tempo_restante.seconds, 3600)
            minutos, _ = divmod(resto, 60)
            await ctx.send(
                f"❌ {ctx.author.mention}, você já trabalhou recentemente! Tente novamente em {horas} horas e {minutos} minutos."
            )
            return

    # Gera um valor aleatório de dinheiro ganho
    dinheiro_ganho = random.randint(50, 200)
    economia[user_id]["carteira"] += dinheiro_ganho
    ultimo_trabalho[user_id] = agora  # Atualiza o horário do último trabalho

    await ctx.send(f"💼 {ctx.author.mention}, você trabalhou e ganhou R$ {dinheiro_ganho}!")
# Comando: Depositar dinheiro no banco
@bot.command()
async def depositar(ctx, quantia: int):
    user_id = ctx.author.id
    inicializar_usuario(user_id)

    if quantia <= 0:
        await ctx.send("❌ Você não pode depositar uma quantia negativa ou zero.")
        return

    if economia[user_id]["carteira"] < quantia:
        await ctx.send("❌ Você não tem dinheiro suficiente na carteira para depositar.")
        return

    economia[user_id]["carteira"] -= quantia
    economia[user_id]["banco"] += quantia
    await ctx.send(f"🏦 {ctx.author.mention}, você depositou R$ {quantia} no banco!")

# Comando: Sacar dinheiro do banco
@bot.command()
async def sacar(ctx, quantia: int):
    user_id = ctx.author.id
    inicializar_usuario(user_id)

    if quantia <= 0:
        await ctx.send("❌ Você não pode sacar uma quantia negativa ou zero.")
        return

    if economia[user_id]["banco"] < quantia:
        await ctx.send("❌ Você não tem dinheiro suficiente no banco para sacar.")
        return

    economia[user_id]["banco"] -= quantia
    economia[user_id]["carteira"] += quantia
    await ctx.send(f"💸 {ctx.author.mention}, você sacou R$ {quantia} do banco!")

# Comando: Transferir dinheiro para outro usuário
@bot.command()
async def transferir(ctx, member: discord.Member, quantia: int):
    user_id = ctx.author.id
    inicializar_usuario(user_id)
    inicializar_usuario(member.id)

    if quantia <= 0:
        await ctx.send("❌ Você não pode transferir uma quantia negativa ou zero.")
        return

    if economia[user_id]["carteira"] < quantia:
        await ctx.send("❌ Você não tem dinheiro suficiente na carteira para transferir.")
        return

    economia[user_id]["carteira"] -= quantia
    economia[member.id]["carteira"] += quantia
    await ctx.send(f"💸 {ctx.author.mention} transferiu R$ {quantia} para {member.mention}!")

# Evento: Carro-Forte (Evento Aleatório)
carro_forte_ativo = False
vencedor_carro_forte = None

# Evento: Carro-Forte (Evento Aleatório)
@tasks.loop(minutes=30)  # Executa a cada 30 minutos
async def carro_forte():
    global carro_forte_ativo, vencedor_carro_forte

    canal = bot.get_channel(975156796899594240)  # Substitua pelo ID do canal onde o evento será anunciado
    if not canal:
        print("❌ Canal do carro-forte não encontrado ou ID inválido.")
        return

    # Ativa o evento do carro-forte
    carro_forte_ativo = True
    vencedor_carro_forte = None

    # Anuncia o evento no canal
    await canal.send(
        "🚚💰 **O carro-forte chegou!** Seja o primeiro a digitar `-t furtar` para ganhar uma quantia alta de dinheiro!"
    )

    # Aguarda 2 minutos para o evento
    await asyncio.sleep(120)

    # Verifica se alguém ganhou
    if vencedor_carro_forte:
        await canal.send(f"🎉 {vencedor_carro_forte.mention} foi o mais rápido e roubou o carro-forte! Parabéns! 💰")
    else:
        await canal.send("🚚💨 O carro-forte foi embora sem ser roubado... Tente na próxima vez!")

    # Desativa o evento do carro-forte
    carro_forte_ativo = False

# Comando: Roubar o carro-forte
@bot.command()
async def furtar(ctx):
    global carro_forte_ativo, vencedor_carro_forte

    user_id = ctx.author.id
    inicializar_usuario(user_id)

    if not carro_forte_ativo:
        await ctx.send("❌ Não há nenhum carro-forte disponível no momento. Aguarde o próximo evento!")
        return

    if vencedor_carro_forte:
        await ctx.send("❌ O carro-forte já foi roubado por outra pessoa!")
        return

    # Define o vencedor e concede o prêmio
    vencedor_carro_forte = ctx.author
    valor = random.randint(1000, 5000)  # Quantia alta aleatória
    economia[user_id]["carteira"] += valor

    await ctx.send(f"🎉 {ctx.author.mention}, você roubou o carro-forte e ganhou R$ {valor}! 💰")

# Inicia o evento do carro-forte
@bot.event
async def on_ready():
    if not carro_forte.is_running():
        carro_forte.start()
    print(f"Bot conectado como {bot.user}")
    print("Sistema do carro-forte iniciado.")

# Comando: Ajuda para Economia
@bot.command()
async def ajuda_economia(ctx):
    embed = discord.Embed(
        title="📖 Ajuda - Economia",
        description="Aqui estão os comandos disponíveis para gerenciar sua economia:",
        color=discord.Color.green()
    )
    embed.add_field(
        name="💰 Comandos de Economia",
        value=(
            "`saldo` - Ver seu saldo na carteira e no banco.\n"
            "`trabalhar` - Trabalhe para ganhar dinheiro.\n"
            "`depositar [quantia]` - Deposite dinheiro no banco.\n"
            "`sacar [quantia]` - Saque dinheiro do banco.\n"
            "`transferir [@membro] [quantia]` - Transfira dinheiro para outro usuário.\n"
        ),
        inline=False
    )
    embed.add_field(
        name="🚚 Evento Aleatório",
        value="O evento **Carro-Forte** ocorre a cada 30 minutos. Fique atento para ganhar dinheiro!",
        inline=False
    )
    embed.set_footer(text="Use os comandos para gerenciar sua economia e ficar rico!")
    await ctx.send(embed=embed)

@bot.command()
async def abracar(ctx, member: discord.Member):
    gifs = [
        "https://media.giphy.com/media/l2QDM9Jnim1YVILXa/giphy.gif",
        "https://media.giphy.com/media/od5H3PmEG5EVq/giphy.gif",
        "https://media.giphy.com/media/3o6ZsYm5P38NvUWrDi/giphy.gif"
    ]
    gif = random.choice(gifs)
    embed = discord.Embed(
        title="🤗 Abraço!",
        description=f"{ctx.author.mention} deu um abraço em {member.mention}!",
        color=discord.Color.purple()
    )
    embed.set_image(url=gif)
    await ctx.send(embed=embed)

@bot.command()
async def beijar(ctx, member: discord.Member):
    gifs = [
        "https://media.giphy.com/media/3o6ZsY6WJv3hGgK2uU/giphy.gif",
        "https://media.giphy.com/media/FqBTvSNjNzeZG/giphy.gif",
        "https://media.giphy.com/media/l2Sqc3POpzkj5rSoE/giphy.gif"
    ]
    gif = random.choice(gifs)
    embed = discord.Embed(
        title="💋 Beijo!",
        description=f"{ctx.author.mention} deu um beijo em {member.mention}!",
        color=discord.Color.red()
    )
    embed.set_image(url=gif)
    await ctx.send(embed=embed)

@bot.command()
async def cafune(ctx, member: discord.Member):
    gifs = [
        "https://media.giphy.com/media/109ltuoSQT212w/giphy.gif",
        "https://media.giphy.com/media/ye7OTQgwmVuVy/giphy.gif",
        "https://media.giphy.com/media/ARSp9T7wwxNcs/giphy.gif"
    ]
    gif = random.choice(gifs)
    embed = discord.Embed(
        title="✨ Cafuné!",
        description=f"{ctx.author.mention} fez cafuné em {member.mention}!",
        color=discord.Color.green()
    )
    embed.set_image(url=gif)
    await ctx.send(embed=embed)

@bot.command()
async def tapa(ctx, member: discord.Member):
    gifs = [
        "https://media.giphy.com/media/Gf3AUz3eBNbTW/giphy.gif",
        "https://media.giphy.com/media/xUNd9HZq1itMkiK652/giphy.gif",
        "https://media.giphy.com/media/3XlEk2RxPS1m8/giphy.gif"
    ]
    gif = random.choice(gifs)
    embed = discord.Embed(
        title="👋 Tapa!",
        description=f"{ctx.author.mention} deu um tapa em {member.mention}!",
        color=discord.Color.orange()
    )
    embed.set_image(url=gif)
    await ctx.send(embed=embed)

@bot.command()
async def fuzilar(ctx, member: discord.Member):
    gifs = [
        "https://media.giphy.com/media/3o7abldj0b3rxrZUxW/giphy.gif",
        "https://media.giphy.com/media/3o6ZsY6WJv3hGgK2uU/giphy.gif",
        "https://media.giphy.com/media/26AHONQ79FdWZhAI0/giphy.gif"
    ]
    gif = random.choice(gifs)
    embed = discord.Embed(
        title="💥 Fuzilamento!",
        description=f"{ctx.author.mention} fuzilou {member.mention}! 😱",
        color=discord.Color.dark_red()
    )
    embed.set_image(url=gif)
    await ctx.send(embed=embed)

@bot.command()
async def perfil(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author  # Usa o autor do comando se nenhum membro for mencionado

    user_id = member.id
    inicializar_usuario(user_id)

    # Obtém os dados do usuário
    nivel = user_levels[user_id]["nivel"]
    exp = user_levels[user_id]["exp"]
    exp_para_proximo_nivel = calcular_exp_para_proximo_nivel(nivel)
    emprego = economia[user_id]["emprego"]
    casado_com = economia[user_id]["casado_com"]

    # Verifica se o usuário está casado
    if casado_com is not None:
        parceiro = await bot.fetch_user(casado_com)
        status_casamento = f"Casado com {parceiro.name}"
    else:
        status_casamento = "Solteiro"

    # Cria a imagem do perfil
    largura, altura = 900, 500

    # Verifica se há um fundo personalizado
    fundo_path = f"backgrounds/{user_id}.png"
    if os.path.exists(fundo_path):
        imagem = Image.open(fundo_path).resize((largura, altura))
    else:
        imagem = Image.new("RGB", (largura, altura), (20, 20, 20))  # Fundo cinza escuro
        draw = ImageDraw.Draw(imagem)
        for i in range(altura):  # Gradiente de fundo
            cor = (20 + i // 10, 20 + i // 15, 50 + i // 20)
            draw.line([(0, i), (largura, i)], fill=cor)

    draw = ImageDraw.Draw(imagem)
    # Fontes
    # Caminho relativo para a fonte Arial no projeto
    fonte_titulo = ImageFont.truetype("assets/fonts/arial.ttf", 40)
    fonte_texto = ImageFont.truetype("assets/fonts/arial.ttf", 30)
    fonte_destaque = ImageFont.truetype("assets/fonts/arial.ttf", 35)

    # Adiciona o título
    draw.text((30, 30), f"Perfil de {member.name}", font=fonte_titulo, fill=(255, 255, 255))

    # Adiciona as informações do perfil
    draw.text((30, 120), f"Nível: {nivel}", font=fonte_destaque, fill=(255, 215, 0))
    draw.text((30, 180), f"EXP: {exp}/{exp_para_proximo_nivel}", font=fonte_texto, fill=(255, 255, 255))
    draw.text((30, 240), f"Emprego: {emprego}", font=fonte_texto, fill=(255, 255, 255))
    draw.text((30, 300), f"Status: {status_casamento}", font=fonte_texto, fill=(255, 255, 255))

    # Adiciona uma moldura para o avatar
    avatar_url = member.avatar.replace(size=256).url  # Obtém a URL do avatar
    async with aiohttp.ClientSession() as session:
        async with session.get(avatar_url) as response:
            avatar_bytes = await response.read()
            avatar = Image.open(io.BytesIO(avatar_bytes)).resize((200, 200))
            avatar = ImageOps.fit(avatar, (200, 200), centering=(0.5, 0.5))
            mask = Image.new("L", avatar.size, 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, 200, 200), fill=255)
            avatar.putalpha(mask)
            imagem.paste(avatar, (650, 50), avatar)

    # Adiciona uma barra de progresso para o EXP
    barra_x = 30
    barra_y = 400
    barra_largura = 800
    barra_altura = 30
    progresso = int((exp / exp_para_proximo_nivel) * barra_largura)

    # Fundo da barra
    draw.rectangle(
        [barra_x, barra_y, barra_x + barra_largura, barra_y + barra_altura],
        fill=(50, 50, 50),
    )
    # Progresso da barra
    draw.rectangle(
        [barra_x, barra_y, barra_x + progresso, barra_y + barra_altura],
        fill=(0, 200, 0),
    )
    # Texto da barra
    draw.text(
        (barra_x + barra_largura // 2, barra_y - 10),
        f"{exp}/{exp_para_proximo_nivel} EXP",
        font=fonte_texto,
        fill=(255, 255, 255),
        anchor="ms",
    )

    # Salva a imagem em um buffer
    buffer = io.BytesIO()
    imagem.save(buffer, format="PNG")
    buffer.seek(0)

    # Envia a imagem no Discord
    await ctx.send(file=discord.File(fp=buffer, filename="perfil.png"))


@bot.command()
async def set_background(ctx):
    if not ctx.message.attachments:
        await ctx.send("❌ Por favor, envie uma imagem junto com o comando.")
        return

    attachment = ctx.message.attachments[0]
    if not attachment.filename.lower().endswith(("png", "jpg", "jpeg")):
        await ctx.send("❌ O arquivo deve ser uma imagem (PNG, JPG ou JPEG).")
        return

    user_id = ctx.author.id
    fundo_path = f"backgrounds/{user_id}.png"

    # Baixa e salva a imagem
    await attachment.save(fundo_path)
    await ctx.send("✅ Seu fundo personalizado foi configurado com sucesso!")
# Inicia o bot com o token carregado
bot.run("")