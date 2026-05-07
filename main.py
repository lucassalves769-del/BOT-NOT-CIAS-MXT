import discord
from discord import app_commands
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import schedule
import time
import json
import re
from datetime import datetime
import threading
import os

# ---------------- CONFIGURAÇÕES (VARIÁVEIS RAILWAY) ----------------
TOKEN_BOT = os.getenv("TOKEN_BOT")
CANAL_NOTIFICACOES_ID = int(os.getenv("CANAL_NOTIFICACOES_ID"))

FONTES = [
    "https://ff.garena.com/news/pt",
    "https://ff.garena.com/updates/pt",
    "https://garenafreefire.com.br/noticias/",
    "https://www.freefiremania.com.br/noticias/"
]

ARQUIVO_HISTORICO = "eventos_encontrados.json"
PALAVRAS_CHAVE = ["evento", "lançamento", "chegando", "próximo", "atualização", "novo", "breve", "em breve", "recompensa", "passe", "pacote", "skin", "temporada"]
# ----------------------------------------------------------------------

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

def carregar_historico():
    try:
        with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except:
        return set()

def salvar_historico(historico):
    with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as f:
        json.dump(list(historico), f, ensure_ascii=False)

def enviar_mensagem_discord(titulo, data_lancamento, detalhes, itens, imagem=None):
    mensagem = "```md\n# 📢 NOVO EVENTO DETECTADO - FREE FIRE\n```\n\n"
    mensagem += f"**📌 TÍTULO DO EVENTO**\n{titulo}\n\n"
    mensagem += f"**📅 DATA DE LANÇAMENTO**\n{data_lancamento}\n\n"
    mensagem += f"**📝 DETALHES DO EVENTO**\n{detalhes}\n\n"
    mensagem += f"**🎁 ITENS E CONTEÚDOS QUE IRÃO CHEGAR**\n{itens}"

    embed = discord.Embed(description=mensagem, color=discord.Color.red())
    if imagem:
        embed.set_image(url=imagem)

    canal = bot.get_channel(CANAL_NOTIFICACOES_ID)
    if canal:
        canal.send(embed=embed)

def buscar_eventos():
    print(f"\n🔍 Verificação iniciada | {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    historico = carregar_historico()

    for url in FONTES:
        try:
            resposta = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            if resposta.status_code != 200:
                continue

            soup = BeautifulSoup(resposta.text, "html.parser")
            artigos = soup.find_all(["article", "div"], class_=["news-item", "post-item", "card", "item"])

            for artigo in artigos:
                titulo_tag = artigo.find(["h2", "h3", "a"])
                titulo = titulo_tag.get_text(strip=True) if titulo_tag else "Evento sem identificação"

                if titulo in historico or not any(p in titulo.lower() for p in PALAVRAS_CHAVE):
                    continue

                detalhes_tag = artigo.find("p")
                detalhes = detalhes_tag.get_text(strip=True) if detalhes_tag else "Informações detalhadas em breve."
                detalhes = detalhes[:400] + "..." if len(detalhes) > 400 else detalhes

                imagem = None
                imagem_tag = artigo.find("img")
                if imagem_tag and imagem_tag.get("src"):
                    imagem = imagem_tag["src"]
                    if imagem.startswith("/"):
                        base = url.split("/")[0] + "//" + url.split("/")[2]
                        imagem = base + imagem

                data_lancamento = "A ser definida | Em breve"
                padroes = [r'\d{2}/\d{2}/\d{4}', r'\d{1,2} de \w+', r'em \d{2}/\d{2}']
                for p in padroes:
                    m = re.search(p, detalhes.lower() + " " + titulo.lower())
                    if m:
                        data_lancamento = m.group(0).capitalize()
                        break

                itens = "• Pacotes e visuais exclusivos\n• Skins de armas e acessórios\n• Recompensas diárias\n• Itens temáticos"
                if "passe" in titulo.lower(): itens += "\n• Passe de Elite completo"
                if "parceria" in titulo.lower(): itens += "\n• Conteúdos de parceria especial"
                if "atualização" in titulo.lower(): itens += "\n• Novos modos/mapas"

                enviar_mensagem_discord(titulo, data_lancamento, detalhes, itens, imagem)
                historico.add(titulo)
                time.sleep(1)

        except Exception as e:
            print(f"⚠️ Erro {url}: {str(e)}")

    salvar_historico(historico)
    print("✅ Verificação finalizada")

def agendador():
    while True:
        schedule.run_pending()
        time.sleep(60)

# ---------------- COMANDOS (SÓ ADM) ----------------
@tree.command(name="status", description="Verifica se o bot está online (ADM)")
@commands.has_permissions(administrator=True)
async def status(interaction: discord.Interaction):
    await interaction.response.send_message(
        "```md\n# ✅ STATUS DO BOT\n```\n**🤖 Online | ⏱️ Verificação: 60min | 📡 Fontes: 4 | 🔐 Acesso: ADM**",
        ephemeral=True
    )

@tree.command(name="atualizar", description="Força busca nova de eventos (ADM)")
@commands.has_permissions(administrator=True)
async def atualizar(interaction: discord.Interaction):
    await interaction.response.send_message("🔄 Atualização iniciada...", ephemeral=True)
    buscar_eventos()
    await interaction.followup.send("✅ Busca finalizada!", ephemeral=True)

@tree.command(name="testar", description="Envia mensagem de teste (ADM)")
@commands.has_permissions(administrator=True)
async def testar(interaction: discord.Interaction):
    await interaction.response.send_message("🧪 Enviando teste...", ephemeral=True)
    enviar_mensagem_discord(
        "TESTE DE SISTEMA",
        "Agora mesmo",
        "Tudo funcionando perfeitamente, integrado com Railway e Discord.",
        "• Comandos ✅\n• Notificações ✅\n• Formato Profissional ✅",
        "https://i.imgur.com/6XZ7Z8L.png"
    )
    await interaction.followup.send("✅ Mensagem enviada no canal!", ephemeral=True)

@bot.event
async def on_ready():
    await tree.sync()
    print(f"🤖 BOT INICIADO: {bot.user}")
    schedule.every(60).minutes.do(buscar_eventos)
    buscar_eventos()
    threading.Thread(target=agendador, daemon=True).start()

bot.run(TOKEN_BOT)
            
