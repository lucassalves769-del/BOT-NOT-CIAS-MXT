import discord
from discord.ext import commands
from discord import app_commands
import requests
from bs4 import BeautifulSoup
import schedule
import time
import json
import re
from datetime import datetime
import threading
import os

# ✅ Variáveis Railway
TOKEN_BOT = os.getenv("TOKEN_BOT")
CANAL_ID = int(os.getenv("CANAL_NOTIFICACOES_ID"))

FONTES = [
    "https://ff.garena.com/news/pt",
    "https://ff.garena.com/updates/pt",
    "https://garenafreefire.com.br/noticias/",
    "https://www.freefiremania.com.br/noticias/"
]

ARQUIVO_HISTORICO = "eventos.json"
PALAVRAS = ["evento", "lançamento", "chegando", "atualização", "novo", "breve", "passe", "skin", "pacote"]

# Configuração
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

def enviar_mensagem(titulo, data, detalhes, itens, imagem=None):
    texto = "```md\n# 📢 NOVO EVENTO DETECTADO - FREE FIRE\n```\n\n"
    texto += f"**📌 TÍTULO**\n{titulo}\n\n"
    texto += f"**📅 DATA DE LANÇAMENTO**\n{data}\n\n"
    texto += f"**📝 DETALHES**\n{detalhes}\n\n"
    texto += f"**🎁 ITENS QUE CHEGARÃO**\n{itens}"

    embed = discord.Embed(description=texto, color=discord.Color.red())
    if imagem:
        embed.set_image(url=imagem)

    canal = bot.get_channel(CANAL_ID)
    if canal:
        canal.send(embed=embed)

def buscar_eventos():
    print(f"\n🔍 Verificação: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    historico = carregar_historico()

    for url in FONTES:
        try:
            res = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            if res.status_code != 200:
                continue

            soup = BeautifulSoup(res.text, "html.parser")
            artigos = soup.find_all(["article", "div"], class_=["news-item", "post-item", "card"])

            for item in artigos:
                titulo_tag = item.find(["h2", "h3", "a"])
                titulo = titulo_tag.get_text(strip=True) if titulo_tag else "Sem título"

                if titulo in historico or not any(p in titulo.lower() for p in PALAVRAS):
                    continue

                detalhes_tag = item.find("p")
                detalhes = detalhes_tag.get_text(strip=True) if detalhes_tag else "Informações em breve."
                detalhes = detalhes[:400] + "..." if len(detalhes) > 400 else detalhes

                imagem = None
                img_tag = item.find("img")
                if img_tag and img_tag.get("src"):
                    imagem = img_tag["src"]
                    if imagem.startswith("/"):
                        base = url.split("/")[0] + "//" + url.split("/")[2]
                        imagem = base + imagem

                data = "A definir | Em breve"
                padroes = [r'\d{2}/\d{2}/\d{4}', r'\d{1,2} de \w+', r'em \d{2}/\d{2}']
                for p in padroes:
                    m = re.search(p, detalhes.lower() + " " + titulo.lower())
                    if m:
                        data = m.group(0).capitalize()
                        break

                itens = "• Pacotes e visuais\n• Skins de armas\n• Recompensas\n• Itens temáticos"
                if "passe" in titulo.lower(): itens += "\n• Passe de Elite"
                if "parceria" in titulo.lower(): itens += "\n• Conteúdo exclusivo de parceria"
                if "atualização" in titulo.lower(): itens += "\n• Novos mapas/modos"

                enviar_mensagem(titulo, data, detalhes, itens, imagem)
                historico.add(titulo)
                time.sleep(1)

        except Exception as e:
            print(f"⚠️ Erro {url}: {e}")

    salvar_historico(historico)
    print("✅ Verificação finalizada")

def rodar_agendador():
    while True:
        schedule.run_pending()
        time.sleep(60)

# ---------------- COMANDOS ----------------
@tree.command(name="status", description="Verifica se o bot está online (ADM)")
@commands.has_permissions(administrator=True)
async def status(interaction: discord.Interaction):
    await interaction.response.send_message(
        "```md\n# ✅ STATUS DO BOT\n```\n**Online ✅ | Verificações: 60min | Acesso só para ADM**",
        ephemeral=True
    )

@tree.command(name="atualizar", description="Força busca nova de eventos (ADM)")
@commands.has_permissions(administrator=True)
async def atualizar(interaction: discord.Interaction):
    await interaction.response.send_message("🔄 Buscando novidades agora...", ephemeral=True)
    buscar_eventos()
    await interaction.followup.send("✅ Busca concluída!", ephemeral=True)

@tree.command(name="testar", description="Envia mensagem de teste no canal (ADM)")
@commands.has_permissions(administrator=True)
async def testar(interaction: discord.Interaction):
    await interaction.response.send_message("🧪 Enviando mensagem de teste...", ephemeral=True)
    enviar_mensagem(
        "TESTE DE SISTEMA",
        "Agora mesmo",
        "Tudo funcionando 100% no Railway e Discord.",
        "• Comandos funcionando ✅\n• Notificações ✅\n• Formato Profissional ✅",
        "https://i.imgur.com/6XZ7Z8L.png"
    )
    await interaction.followup.send("✅ Mensagem enviada!", ephemeral=True)

@bot.event
async def on_ready():
    await tree.sync()
    print(f"🤖 BOT CONECTADO: {bot.user}")
    schedule.every(60).minutes.do(buscar_eventos)
    buscar_eventos()
    threading.Thread(target=rodar_agendador, daemon=True).start()

bot.run(TOKEN_BOT)
                
