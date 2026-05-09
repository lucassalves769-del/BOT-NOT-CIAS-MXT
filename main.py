import os
import time
from dotenv import load_dotenv
import discord

# ==================================================
# 🤍 BOT REPASSADOR - CORRIGIDO PARA RAILWAY 🤍
# ✅ Erro do Client.start() RESOLVIDO
# ✅ Todos podem usar
# ✅ Suporta texto + fotos + arquivos
# ✅ /status e /apagar funcionando
# ==================================================

load_dotenv()

# ⚙️ VARIÁVEIS (Nomes exatos que você deve colocar no Railway)
TOKEN = os.getenv("TOKEN")
CANAL_ORIGEM = os.getenv("CANAL_ORIGEM")
CANAL_DESTINO = os.getenv("CANAL_DESTINO")

# 🚨 CONVERTE PARA NÚMERO (era o que estava causando erro)
try:
    CANAL_ORIGEM = int(CANAL_ORIGEM)
    CANAL_DESTINO = int(CANAL_DESTINO)
except:
    print("❌ ERRO: IDs dos canais devem ser números!")
    exit()

# 🚀 INICIALIZAÇÃO CORRETA
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = discord.Bot(intents=intents, description="Bot Repassador")

# 📌 VARIÁVEIS GLOBAIS
ultima_mensagem = None
inicio_uptime = time.time()

# ==================================================
# 📩 FUNÇÃO DE REPASSE
# ==================================================
@bot.event
async def on_message(message: discord.Message):
    global ultima_mensagem

    if message.author == bot.user:
        return

    if message.channel.id == CANAL_ORIGEM:
        canal_destino = bot.get_channel(CANAL_DESTINO)
        if not canal_destino:
            print("❌ Canal de destino não encontrado")
            return

        # 📝 Texto
        if message.content:
            msg = await canal_destino.send(message.content)
            ultima_mensagem = msg

        # 🖼️ Arquivos / Fotos
        if message.attachments:
            arquivos = []
            for arq in message.attachments:
                arquivos.append(await arq.to_file())
            msg = await canal_destino.send(files=arquivos)
            ultima_mensagem = msg

        # 🗑️ Apaga mensagem original
        try:
            await message.delete()
        except:
            pass

    await bot.process_commands(message)

# ==================================================
# ⚡ COMANDOS
# ==================================================
@bot.slash_command(name="status", description="📊 Ver status do bot")
async def _status(ctx):
    tempo = time.time() - inicio_uptime
    up = f"{int(tempo//86400)}d {int((tempo%86400)//3600)}h {int((tempo%3600)//60)}m {int(tempo%60)}s"

    emb = discord.Embed(title="🤖 STATUS DO BOT", color=discord.Color.green(), description=f"""
✅ **Online e funcionando**
⏱️ **Tempo ativo:** {up}
📤 **Canal Origem:** `{CANAL_ORIGEM}`
📥 **Canal Destino:** `{CANAL_DESTINO}`
📸 **Suporte a fotos:** ✅ OK
👥 **Acesso:** Liberado para todos
    """)
    await ctx.respond(embed=emb)


@bot.slash_command(name="apagar", description="🗑️ Apaga última mensagem enviada")
async def _apagar(ctx):
    global ultima_mensagem
    if not ultima_mensagem:
        return await ctx.respond("⚠️ Nenhuma mensagem para apagar!", ephemeral=True)
    try:
        await ultima_mensagem.delete()
        ultima_mensagem = None
        await ctx.respond("✅ Mensagem apagada!", ephemeral=True)
    except:
        await ctx.respond("❌ Erro ao apagar!", ephemeral=True)

# ==================================================
# 🚀 INICIAR (CORREÇÃO PRINCIPAL AQUI)
# ==================================================
@bot.event
async def on_ready():
    print("="*50)
    print(f"✅ BOT INICIADO COM SUCESSO!")
    print(f"🤖 Nome: {bot.user}")
    print(f"📤 Origem: {CANAL_ORIGEM} | 📥 Destino: {CANAL_DESTINO}")
    print("="*50)

# ✅ FORMA CORRETA DE INICIAR (resolve o erro que apareceu)
if __name__ == "__main__":
    bot.run(TOKEN)
        
