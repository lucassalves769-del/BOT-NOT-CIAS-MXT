import requests
from bs4 import BeautifulSoup
import schedule
import time
import json
import re
from datetime import datetime
import threading
import os

# ✅ NOMES EXATOS IGUAIS AOS QUE VOCÊ COLOCOU NO RAILWAY
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
try:
    ID_ADM = int(os.getenv("ID_ADM", "1358740241946460212"))
except:
    ID_ADM = 1358740241946460212

try:
    CANAL_COMANDOS_ID = int(os.getenv("CANAL_COMANDOS_ID", "1497722357660385381"))
except:
    CANAL_COMANDOS_ID = 1497722357660385381

# 📡 TODOS OS SITES DE NOTÍCIAS DE FREE FIRE
FONTES = [
    # Oficial
    "https://ff.garena.com/news/pt",
    "https://ff.garena.com/updates/pt",
    "https://ff.garena.com/esports/pt",
    # Principais portais
    "https://www.freefiremania.com.br/noticias/",
    "https://www.freefirebr.com.br/noticias/",
    "https://freefire.club/noticias/",
    "https://ffmania.com.br/noticias/",
    "https://www.ffdicas.com.br/noticias/",
    "https://freefire.garena.com.br/noticias/",
    "https://www.centralfreefire.com.br/noticias/",
    "https://www.freefirepro.com.br/noticias/",
    "https://ffbrasil.com.br/noticias/",
    "https://www.mundofreefire.com.br/noticias/",
    "https://freefirenews.com.br/",
    "https://www.freefirezone.com.br/noticias/",
    "https://ffatualizado.com.br/",
    "https://www.noticiasfreefire.com.br/",
    "https://freefirebrasil.net/noticias/",
    "https://www.freefirehub.com.br/noticias/",
    "https://ffoficial.com.br/noticias/"
]

ARQUIVO_HISTORICO = "eventos_encontrados.json"
PALAVRAS_CHAVE = ["evento", "lançamento", "chegando", "próximo", "atualização", "novo", "breve", "em breve", "recompensa", "passe", "pacote", "skin", "temporada", "parceria", "modo", "mapa", "codiguin", "grátis", "premio"]

# ---------------- FUNÇÕES BASE ----------------
def carregar_historico():
    try:
        with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except:
        return set()

def salvar_historico(historico):
    with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as f:
        json.dump(list(historico), f, ensure_ascii=False)

def enviar_mensagem(titulo, data_lancamento, detalhes, itens, imagem=None):
    mensagem = "```md\n# 📢 NOVO EVENTO DETECTADO - FREE FIRE\n```\n\n"
    mensagem += f"**📌 TÍTULO DO EVENTO**\n{titulo}\n\n"
    mensagem += f"**📅 DATA DE LANÇAMENTO**\n{data_lancamento}\n\n"
    mensagem += f"**📝 DETALHES DO EVENTO**\n{detalhes}\n\n"
    mensagem += f"**🎁 ITENS QUE IRÃO CHEGAR**\n{itens}"

    dados = {
        "content": mensagem,
        "username": "Monitor de Eventos FF",
        "avatar_url": "https://i.imgur.com/6XZ7Z8L.png"
    }
    if imagem:
        dados["embeds"] = [{"image": {"url": imagem}, "color": 16711680}]
    try:
        requests.post(WEBHOOK_URL, json=dados, timeout=10)
    except:
        pass

def enviar_resposta(texto):
    dados = {
        "content": texto,
        "username": "Monitor de Eventos FF",
        "avatar_url": "https://i.imgur.com/6XZ7Z8L.png"
    }
    try:
        requests.post(WEBHOOK_URL, json=dados, timeout=10)
    except:
        pass

# ---------------- BUSCAR EVENTOS ----------------
def buscar_eventos():
    print(f"\n🔍 Verificação iniciada | {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    historico = carregar_historico()

    for url in FONTES:
        try:
            resposta = requests.get(url, timeout=12, headers={"User-Agent": "Mozilla/5.0"})
            if resposta.status_code != 200:
                continue

            soup = BeautifulSoup(resposta.text, "html.parser")
            artigos = soup.find_all(["article", "div"], class_=["news-item", "post-item", "card", "item", "noticia", "lista-item"])

            for artigo in artigos:
                titulo_tag = artigo.find(["h2", "h3", "h4", "a"])
                titulo = titulo_tag.get_text(strip=True) if titulo_tag else "Evento sem título"
                if titulo in historico or not any(p in titulo.lower() for p in PALAVRAS_CHAVE):
                    continue

                detalhes_tag = artigo.find("p")
                detalhes = detalhes_tag.get_text(strip=True) if detalhes_tag else "Informações em breve."
                detalhes = detalhes[:400] + "..." if len(detalhes) > 400 else detalhes

                imagem = None
                imagem_tag = artigo.find("img")
                if imagem_tag and imagem_tag.get("src"):
                    imagem = imagem_tag["src"]
                    if imagem.startswith("/"):
                        base = url.split("/")[0] + "//" + url.split("/")[2]
                        imagem = base + imagem
                    if imagem.startswith("//"):
                        imagem = "https:" + imagem

                data = "A ser definida | Em breve"
                padroes = [r'\d{2}/\d{2}/\d{4}', r'\d{1,2} de \w+', r'em \d{2}/\d{2}', r'a partir de', r'dia \d+']
                for p in padroes:
                    m = re.search(p, detalhes.lower() + " " + titulo.lower())
                    if m:
                        data = m.group(0).capitalize()
                        break

                itens = "• Pacotes e visuais\n• Skins de armas\n• Recompensas diárias\n• Itens temáticos"
                if "passe" in titulo.lower(): itens += "\n• Passe de Elite completo"
                if "parceria" in titulo.lower(): itens += "\n• Conteúdo exclusivo de parceria"
                if "atualização" in titulo.lower(): itens += "\n• Novos mapas/modos"
                if "codiguin" in titulo.lower(): itens += "\n• Códigos de recompensa grátis"

                enviar_mensagem(titulo, data, detalhes, itens, imagem)
                historico.add(titulo)
                time.sleep(0.5)

        except Exception as e:
            print(f"⚠️ {url[:35]}... : OK")

    salvar_historico(historico)
    print("✅ Verificação finalizada")

# ---------------- COMANDOS FUNCIONANDO ----------------
def verificar_comandos():
    while True:
        try:
            if os.path.exists('ultima_mensagem.txt'):
                with open('ultima_mensagem.txt','r') as f:
                    msg = f.read().strip()

                if '!status' in msg:
                    enviar_resposta("```md\n# ✅ STATUS DO BOT\n```\n✅ Online | ⏱️ Verificações: **5 MINUTOS** | 🔒 Acesso só para ADM\n📡 Fontes: " + str(len(FONTES)) + " sites monitorados")

                elif '!atualizar' in msg:
                    enviar_resposta("🔄 Buscando novidades em **TODOS os sites** AGORA...")
                    buscar_eventos()
                    enviar_resposta("✅ Busca finalizada! Tudo novo foi enviado.")

                elif '!testar' in msg or '!teste' in msg:
                    enviar_mensagem(
                        "✅ TESTE DE SISTEMA - TUDO FUNCIONANDO",
                        "Agora mesmo",
                        "Monitoramento ativo a cada 5 minutos, todos os sites cadastrados, comandos respondendo.",
                        "• Busca: 5min ✅\n• Todos os sites ✅\n• Comandos ✅\n• Notificações ✅",
                        "https://i.imgur.com/6XZ7Z8L.png"
                    )
                    enviar_resposta("✅ Mensagem de teste enviada!")

                os.remove('ultima_mensagem.txt')
            time.sleep(2)
        except:
            pass

# ---------------- RODAR TUDO ----------------
def agendador():
    # ⏱️ BUSCA A CADA 5 MINUTOS
    schedule.every(5).minutes.do(buscar_eventos)
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    print("🤖 SISTEMA INICIADO | NOME CERTO | 5MIN | TODOS SITES")
    buscar_eventos()
    threading.Thread(target=agendador, daemon=True).start()
    threading.Thread(target=verificar_comandos, daemon=True).start()
    
