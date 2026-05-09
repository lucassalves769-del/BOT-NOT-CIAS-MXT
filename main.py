import os
import time
from dotenv import load_dotenv
import discord

# ==================================================
# 🤍 BOT NOTÍCIAS MXT - VERSÃO FINAL CORRIGIDA 🤍
# ✅ Erro 'Bot' object has no attribute RESOLVIDO
# ✅ Fica ONLINE (bolinha verde)
# ✅ Repassa texto + fotos + arquivos
# ✅ Comandos /status e /apagar funcionando
# ✅ Todos podem usar
# ==================================================

load_dotenv()

# ⚙️ VARIÁVEIS (coloque exatamente esses nomes no Railway)
TOKEN = os.getenv("TOKEN")
CANAL_ORIGEM = os.getenv("CANAL_ORIGEM")
CANAL_DESTINO = os.getenv("CANAL_DESTINO")

# 🚨 Validação das variáveis
if not TOKEN or not CANAL_ORIGEM or not CANAL_DESTINO:
    print("❌ ERRO: Preencha todas as variáveis no Railway!")
    exit()

try:
    CANAL_ORIGEM = int(CANAL_ORIGEM)
    CANAL_DESTINO = int(CANAL_DESTINO)
except:
    print("❌ ERRO: IDs dos canais devem ser números!")
    exit()

# 🚀 INICIALIZAÇÃO COM TODAS AS PERMISSÕES
intents = discord.Intents.all()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = discord.Bot(
    intents=intents,
    description="Bot Notícias MXT - Repassador",
    activity=discord.Activity(type=discord.ActivityType.watching, name="📢 Notícias | MXT")
)

# 📌 VARIÁVEIS GLOBAIS
ultima_mensagem = None
inicio_uptime = time.time()

# ==================================================
# 📩 FUNÇÃO DE REPASSE DE MENSAGENS
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
            print("❌ ERRO: Canal de destino não encontrado!")
            return

        # 📝 Envia texto
        if message.content:
            try:
                msg = await canal_destino.send(message.content)
                ultima_mensagem = msg
            except Exception as e:
                print(f"❌ Erro ao enviar texto: {e}")

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
                except Exception as e:
                    print(f"❌ Erro ao enviar arquivo: {e}")

        # 🗑️ Apaga mensagem original
        try:
            await message.delete()
        except:
            pass

    # ✅ REMOVIDO O COMANDO QUE DAVA ERRO: bot.process_commands(message)

# ==================================================
# ⚡ SLASH COMMANDS
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
📸 **Suporte a Fotos:** ✅ ATIVADO
👥 **Acesso:** Liberado para todos
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
        await ctx.respond(f"❌ Erro ao apagar: {e}", ephemeral=True)

# ==================================================
# 🚀 INICIAR BOT
# ==================================================
@bot.event
async def on_ready():
    print("="*60)
    print(f"✅ CONECTADO COM SUCESSO!")
    print(f"🤖 Nome: {bot.user}")
    print(f"🟢 STATUS: ONLINE | BOLINHA VERDE")
    print(f"📤 Canal Origem: {CANAL_ORIGEM}")
    print(f"📥 Canal Destino: {CANAL_DESTINO}")
    print("="*60)

if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"❌ ERRO AO INICIAR: {e}")
