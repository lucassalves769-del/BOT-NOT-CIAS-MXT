import os
import time
from dotenv import load_dotenv
import discord

# ==================================================
# 🤍 BOT REPASSADOR - TODOS PODEM USAR 🤍
# ✅ Quem estiver no canal pode mandar mensagem/foto
# ✅ Bot repassa tudo como se fosse ele
# ✅ /status e /apagar liberados para todos
# ✅ Suporta texto, fotos, vídeos, arquivos
# ✅ PYTHON | RAILWAY
# ==================================================

load_dotenv()

# ⚙️ CONFIGURAÇÕES
TOKEN = os.getenv("TOKEN")
CANAL_ORIGEM = int(os.getenv("CANAL_ORIGEM"))
CANAL_DESTINO = int(os.getenv("CANAL_DESTINO"))

# 🚀 INICIALIZAÇÃO
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = discord.Bot(
    token=TOKEN,
    intents=intents,
    description="Bot que repassa mensagens e arquivos"
)

# 📌 VARIÁVEIS GLOBAIS
ultima_mensagem = None  # Guarda última mensagem (texto OU foto)
inicio_uptime = time.time()

# ==================================================
# 📩 FUNÇÃO PRINCIPAL: REPASSA TUDO
# ==================================================
@bot.event
async def on_message(message: discord.Message):
    global ultima_mensagem

    # Ignora mensagens do próprio bot
    if message.author == bot.user:
        return

    # SE FOR O CANAL DE ORIGEM (QUALQUER UM QUE ESTIVER LÁ PODE MANDAR)
    if message.channel.id == CANAL_ORIGEM:
        canal_destino = bot.get_channel(CANAL_DESTINO)
        if not canal_destino:
            print("❌ Canal de destino não encontrado!")
            return

        # 📝 SE TIVER TEXTO
        if message.content:
            msg_enviada = await canal_destino.send(message.content)
            ultima_mensagem = msg_enviada  # Salva para apagar depois

        # 🖼️ SE TIVER FOTOS, VÍDEOS OU ARQUIVOS
        if message.attachments:
            lista_arquivos = []
            for arquivo in message.attachments:
                lista_arquivos.append(await arquivo.to_file())

            # Envia TODOS os arquivos de uma vez
            msg_arquivos = await canal_destino.send(files=lista_arquivos)
            ultima_mensagem = msg_arquivos  # Salva também para apagar

        # 🗑️ Apaga a mensagem original do canal de origem
        try:
            await message.delete()
        except:
            pass

    await bot.process_commands(message)

# ==================================================
# ⚡ SLASH COMMANDS (LIBERADOS PARA TODOS)
# ==================================================

@bot.slash_command(name="status", description="📊 Ver status e funcionamento do bot")
async def _status(ctx):
    tempo_seg = time.time() - inicio_uptime
    uptime = f"{int(tempo_seg//86400)}d {int((tempo_seg%86400)//3600)}h {int((tempo_seg%3600)//60)}m {int(tempo_seg%60)}s"

    emb = discord.Embed(title="🤖 STATUS DO BOT", color=discord.Color.green(), description=f"""
✅ **Online e funcionando normalmente**
⏱️ **Tempo ativo:** {uptime}
📤 **Canal de Origem:** `{CANAL_ORIGEM}`
📥 **Canal de Destino:** `{CANAL_DESTINO}`
📸 **Suporte a fotos/arquivos:** ✅ ATIVADO
👥 **Acesso:** Liberado para todos os membros
    """)
    await ctx.respond(embed=emb)


@bot.slash_command(name="apagar", description="🗑️ Apaga a última mensagem/foto enviada pelo bot")
async def _apagar(ctx):
    global ultima_mensagem

    if not ultima_mensagem:
        return await ctx.respond("⚠️ Não há nenhuma mensagem minha para apagar!", ephemeral=True)

    try:
        await ultima_mensagem.delete()
        ultima_mensagem = None
        await ctx.respond("✅ Última mensagem/arquivo apagada com sucesso!", ephemeral=True)
    except:
        await ctx.respond("❌ Erro ao apagar mensagem!", ephemeral=True)

# ==================================================
# 🚀 INICIAR BOT
# ==================================================
@bot.event
async def on_ready():
    print("="*50)
    print(f"✅ BOT INICIADO COM SUCESSO | {bot.user}")
    print(f"👥 MODO LIBERADO: Todos do canal podem usar")
    print(f"📸 ENVIO DE FOTOS/ARQUIVOS: ATIVADO")
    print("="*50)

bot.run()
      
