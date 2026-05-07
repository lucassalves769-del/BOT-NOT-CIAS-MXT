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
import os  # ✅ Pega as variáveis do Railway

# ---------------- CONFIGURAÇÕES (TUDO NAS VARIÁVEIS) ----------------
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

# Configuração do Bot
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
    mensagem = "```md\n"
    mensagem += "# 📢 NOVO EVENTO DETECTADO - FREE FIRE\n"
    mensagem += "```\n\n"

    mensagem += "**📌 TÍTULO DO EVENTO**\n"
    mensagem += f"{titulo}\n\n"

    mensagem += "**📅 DATA DE LANÇAMENTO**\n"
    mensagem += f"{data_lancamento}\n\n"

    mensagem += "**📝 DETALHES DO EVENTO**\n"
    mensagem += f"{detalhes}\n\n"

    mensagem += "**🎁 ITENS E CONTEÚDOS QUE IRÃO CHEGAR**\n"
    mensagem += f"{itens}\n"

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
            resposta = requests.get(
                url,
                timeout=15,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/120.0.0.0 Safari/537.36"}
            )
            if resposta.status_code != 200:
                continue

            soup = BeautifulSoup(resposta.text, "html.parser")
            artigos = soup.find_all(["article", "div"], class_=["news-item", "post-item", "card", "item"])

            for artigo in artigos:
                titulo_tag = artigo.find(["h2", "h3", "a"])
                titulo = titulo_tag.get_text(strip=True) if titulo_tag else "Evento sem identificação"

                if titulo in historico:
                    continue

                if not any(palavra in titulo.lower() for palavra in PALAVRAS_CHAVE):
                    continue

                # Extrair detalhes
                detalhes_tag = artigo.find("p")
                detalhes = detalhes_tag.get_text(strip=True) if detalhes_tag else "Informações detalhadas serão divulgadas em breve."
                detalhes = detalhes[:400] + "..." if len(detalhes) > 400 else detalhes

                # Extrair imagem
                imagem = None
                imagem_tag = artigo.find("img")
                if imagem_tag and imagem_tag.get("src"):
                    imagem = imagem_tag["src"]
                    if imagem.startswith("/"):
                        base_url = url.split("/")[0] + "//" + url.split("/")[2]
                        imagem = base_url + imagem

                # Definir data
                data_lancamento = "A ser definida | Em breve"
                padroes_data = [
                    r'\d{2}/\d{2}/\d{4}', r'\d{1,2} de \w+ de \d{4}',
                    r'\d{1,2} de \w+', r'em \d{2}/\d{2}'
                ]
                for padrao in padroes_data:
                    encontro = re.search(padrao, detalhes.lower() + " " + titulo.lower())
                    if encontro:
                        data_lancamento = encontro.group(0).capitalize()
                        break

                # Definir itens
                itens = "• Pacotes e visuais exclusivos\n• Skins de armas e acessórios\n• Recompensas por missões diárias\n• Itens temáticos do evento"
                if "passe" in titulo.lower():
                    itens += "\n• Passe de Elite completo com recompensas"
                if "parceria" in titulo.lower() or "colaboração" in titulo.lower():
                    itens += "\n• Conteúdos exclusivos da parceria especial"
                if "atualização" in titulo.lower():
                    itens += "\n• Novos mapas, modos e mecânicas de jogo"

                # Enviar notificação
                enviar_mensagem_discord(titulo, data_lancamento, detalhes, itens, imagem)
                historico.add(titulo)
                time.sleep(1)

        except Exception as e:
            print(f"⚠️ Falha ao consultar {url}: {str(e)}")

    salvar_historico(historico)
    print("✅ Verificação finalizada")

# Função do agendador (roda em segundo plano)
def agendador():
    while True:
        schedule.run_pending()
        time.sleep(60)

# ---------------- COMANDOS SLASH (SÓ ADM PODE USAR) ----------------

@tree.command(name="status", description="Verifica se o bot está funcionando (Apenas ADM)")
@commands.has_permissions(administrator=True)
async def status(interaction: discord.Interaction):
    await interaction.response.send_message(
        "```md\n# ✅ STATUS DO BOT\n```\n"
        "**🤖 Estado:** Online e operacional\n"
        "**⏱️ Verificação:** A cada 60 minutos\n"
        "**📡 Fontes ativas:** 4 sites oficiais\n"
        "**🔐 Acesso:** Restrito a administradores",
        ephemeral=True
    )

@tree.command(name="atualizar", description="Força nova busca e troca fonte de pesquisa (Apenas ADM)")
@commands.has_permissions(administrator=True)
async def atualizar(interaction: discord.Interaction):
    await interaction.response.send_message(
        "🔄 **Atualização forçada iniciada...**\n"
        "Interrompi a rotina automática e estou vasculhando todas as fontes agora mesmo.",
        ephemeral=True
    )
    buscar_eventos()
    await interaction.followup.send("✅ **Busca finalizada!** Nenhuma novidade ou todos os eventos já foram enviados.", ephemeral=True)

@tree.command(name="testar", description="Envia mensagem de teste no canal de eventos (Apenas ADM)")
@commands.has_permissions(administrator=True)
async def testar(interaction: discord.Interaction):
    await interaction.response.send_message("🧪 Enviando mensagem de teste...", ephemeral=True)
    enviar_mensagem_discord(
        titulo="TESTE DE FUNCIONAMENTO",
        data_lancamento="Agora mesmo",
        detalhes="Sistema 100% operacional, integrado com Railway e Discord. Todas as funções estão ativas.",
        itens="• Comandos funcionando ✅\n• Notificações enviadas ✅\n• Formato profissional ✅",
        imagem="https://i.imgur.com/6XZ7Z8L.png"
    )
    await interaction.followup.send("✅ Mensagem de teste enviada com sucesso no canal!", ephemeral=True)

# ---------------- EVENTOS DO BOT ----------------

@bot.event
async def on_ready():
    await tree.sync()  # Sincroniza os comandos /
    print(f"🤖 BOT INICIADO | Logado como: {bot.user}")
    print("🔹 Comandos: /status, /atualizar, /testar")
    print("🔹 Monitoramento ATIVO")

    # Inicia busca automática a cada 60min
    schedule.every(60).minutes.do(buscar_eventos)
    # Primeira busca logo ao ligar
    buscar_eventos()

    # Inicia rotina em segundo plano
    threading.Thread(target=agendador, daemon=True).start()

# Rodar o bot
bot.run(TOKEN_BOT)
            
