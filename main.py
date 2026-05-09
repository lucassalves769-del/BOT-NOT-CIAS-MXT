import os
import time
import asyncio
from dotenv import load_dotenv
import discord

# ==================================================
# 🤍 BOT NOTÍCIAS MXT + DIVULGAÇÃO AUTOMÁTICA 🤍
# ✅ ERRO DE STRING RESOLVIDO
# ✅ Repassa mensagens/fotos
# ✅ Comandos /status e /apagar
# ✅ Divulgação a cada 5min com mensagem correta
# ✅ Online e funcionando
# ==================================================

load_dotenv()

# ⚙️ VARIÁVEIS (no Railway, coloque todas essas)
TOKEN = os.getenv("TOKEN")
CANAL_ORIGEM = os.getenv("CANAL_ORIGEM")
CANAL_DESTINO = os.getenv("CANAL_DESTINO")
CANAL_DIVULGACAO = os.getenv("CANAL_DIVULGACAO")

# 🚨 Validação
if not TOKEN or not CANAL_ORIGEM or not CANAL_DESTINO or not CANAL_DIVULGACAO:
    print("❌ ERRO: Preencha TODAS as variáveis!")
    exit()

try:
    CANAL_ORIGEM = int(CANAL_ORIGEM)
    CANAL_DESTINO = int(CANAL_DESTINO)
    CANAL_DIVULGACAO = int(CANAL_DIVULGACAO)
except:
    print("❌ ERRO: IDs devem ser números!")
    exit()

# 🚀 INICIALIZAÇÃO
intents = discord.Intents.all()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = discord.Bot(
    intents=intents,
    description="Bot Notícias MXT",
    activity=discord.Activity(type=discord.ActivityType.watching, name="📢 Notícias | MXT")
)

# 📌 VARIÁVEIS GLOBAIS
ultima_mensagem = None
inicio_uptime = time.time()

# 📌 MENSAGEM DE DIVULGAÇÃO (CORRIGIDA, SEM ERRO)
MENSAGEM_ANUNCIO = """**tá procurando passe booyah barato?
aqui você achou!! ofertas imperdíveis somente aqui na MXT STORE, temos o bot de eventos e bot de vendas, então venha comprar aqui na MXT e vire cliente vip 😉"""

# ==================================================
# 🔁 FUNÇÃO: ENVIA ANÚNCIO A CADA 5 MINUTOS
# ==================================================
async def enviar_divulgacao():
    await bot.wait_until_ready()
    while not bot.is_closed():
        canal = bot.get_channel(CANAL_DIVULGACAO)
        if canal:
            try:
                await canal.send(MENSAGEM_ANUNCIO)
            except Exception as e:
                print(f"Erro ao enviar anúncio: {e}")
        # Espera 5 minutos = 300 segundos
        await asyncio.sleep(300)

# ==================================================
# 📩 FUNÇÃO: REPASSA MENSAGENS E FOTOS
# ==================================================
@bot.event
async def on_message(message: discord.Message):
    global ultima_mensagem

    # Ignora mensagens do próprio bot
    if message.author == bot.user:
        return

    # Se for o canal de origem
    if message.channel.id == CANAL_ORIGEM:
        canal_destino = bot.get_channel(CANAL_DESTINO)
        if not canal_destino:
            return

        # 📝 Envia texto
        if message.content:
            try:
                msg = await canal_destino.send(message.content)
                ultima_mensagem = msg
            except:
                pass

        # 🖼️ Envia fotos/arquivos
        if message.attachments:
            arquivos = []
            for arq in message.attachments:
                try:
                    arquivos.append(await arq.to_file())
                except:
                    pass
            if arquivos:
                try:
                    msg = await canal_destino.send(files=arquivos)
                    ultima_mensagem = msg
                except:
                    pass

        # 🗑️ Apaga mensagem original
        try:
            await message.delete()
        except:
            pass

# ==================================================
# ⚡ COMANDOS
# ==================================================
@bot.slash_command(name="status", description="📊 Ver status do bot")
async def _status(ctx):
    tempo = time.time() - inicio_uptime
    up = f"{int(tempo//86400)}d {int((tempo%86400)//3600)}h {int((tempo%3600)//60)}m {int(tempo%60)}s"

    emb = discord.Embed(title="🤖 STATUS - BOT NOTÍCIAS MXT", color=discord.Color.green(), description=f"""
✅ **🟢 ONLINE E FUNCIONANDO**
⏱️ **Tempo Ativo:** {up}
📤 **Canal Origem:** `{CANAL_ORIGEM}`
📥 **Canal Destino:** `{CANAL_DESTINO}`
📢 **Divulgação:** Ativada (a cada 5 minutos)
📸 **Suporte a Fotos:** ✅ OK
    """)
    await ctx.respond(embed=emb)


@bot.slash_command(name="apagar", description="🗑️ Apaga a última mensagem enviada pelo bot")
async def _apagar(ctx):
    global ultima_mensagem
    if not ultima_mensagem:
        return await ctx.respond("⚠️ Nenhuma mensagem minha para apagar!", ephemeral=True)
    try:
        await ultima_mensagem.delete()
        ultima_mensagem = None
        await ctx.respond("✅ Última mensagem/arquivo APAGADA!", ephemeral=True)
    except Exception as e:
        await ctx.respond(f"❌ Erro: {e}", ephemeral=True)

# ==================================================
# 🚀 INICIAR BOT
# ==================================================
@bot.event
async def on_ready():
    print("="*60)
    print(f"✅ BOT CONECTADO COM SUCESSO!")
    print(f"🤖 Nome: {bot.user}")
    print(f"📢 Divulgação automática ATIVADA")
    print("="*60)
    # Inicia a tarefa de divulgação
    bot.loop.create_task(enviar_divulgacao())

if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
                          
