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
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
CANAL_COMANDOS_ID = int(os.getenv("CANAL_COMANDOS_ID"))
ID_ADM = int(os.getenv("ID_ADM")) # COLOQUE SEU ID DO DISCORD AQUI

FONTES = [
    "https://ff.garena.com/news/pt",
    "https://ff.garena.com/updates/pt",
    "https://garenafreefire.com.br/noticias/",
    "https://www.freefiremania.com.br/noticias/"
]

ARQUIVO_HISTORICO = "eventos_encontrados.json"
PALAVRAS_CHAVE = ["evento", "lançamento", "chegando", "próximo", "atualização", "novo", "breve", "em breve", "recompensa", "passe", "pacote", "skin", "temporada"]
# ----------------------------------------------------------------------

def carregar_historico():
    try:
        with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except:
        return set()

def salvar_historico(historico):
    with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as f:
        json.dump(list(historico), f, ensure_ascii=False)

def enviar_discord(titulo, data_lancamento, detalhes, itens, imagem=None):
    mensagem = "```md\n# 📢 NOVO EVENTO DETECTADO - FREE FIRE\n```\n\n"
    mensagem += f"**📌 TÍTULO DO EVENTO**\n{titulo}\n\n"
    mensagem += f"**📅 DATA DE LANÇAMENTO**\n{data_lancamento}\n\n"
    mensagem += f"**📝 DETALHES DO EVENTO**\n{detalhes}\n\n"
    mensagem += f"**🎁 ITENS E CONTEÚDOS QUE IRÃO CHEGAR**\n{itens}"

    dados = {
        "content": mensagem,
        "username": "Monitor de Eventos FF",
        "avatar_url": "https://i.imgur.com/6XZ7Z8L.png"
    }
    if imagem:
        dados["embeds"] = [{"image": {"url": imagem}, "color": 16711680}]

    try:
        requests.post(WEBHOOK_URL, json=dados)
        print("✅ Mensagem enviada")
    except Exception as e:
        print(f"❌ Erro: {e}")

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
                detalhes = detalhes_tag.get_text(strip=True) if detalhes_tag else "Informações detalhadas serão divulgadas em breve."
                detalhes = detalhes[:400] + "..." if len(detalhes) > 400 else detalhes

                imagem = None
                imagem_tag = artigo.find("img")
                if imagem_tag and imagem_tag.get("src"):
                    imagem = imagem_tag["src"]
                    if imagem.startswith("/"):
                        base_url = url.split("/")[0] + "//" + url.split("/")[2]
                        imagem = base_url + imagem

                data_lancamento = "A ser definida | Em breve"
                padroes_data = [r'\d{2}/\d{2}/\d{4}', r'\d{1,2} de \w+ de \d{4}', r'\d{1,2} de \w+']
                for padrao in padroes_data:
                    encontro = re.search(padrao, detalhes.lower() + " " + titulo.lower())
                    if encontro:
                        data_lancamento = encontro.group(0).capitalize()
                        break

                itens = "• Pacotes e visuais exclusivos\n• Skins de armas e acessórios\n• Recompensas por missões\n• Itens temáticos"
                if "passe" in titulo.lower(): itens += "\n• Passe de Elite completo"
                if "parceria" in titulo.lower(): itens += "\n• Conteúdos exclusivos de parceria"
                if "atualização" in titulo.lower(): itens += "\n• Novos mapas/modos"

                enviar_discord(titulo, data_lancamento, detalhes, itens, imagem)
                historico.add(titulo)
                time.sleep(1)

        except Exception as e:
            print(f"⚠️ Falha ao consultar {url}: {str(e)}")

    salvar_historico(historico)
    print("✅ Verificação finalizada")

# ---------------- COMANDOS POR MENSAGEM (SÓ ADM) ----------------
def verificar_comandos():
    while True:
        try:
            # LER ÚLTIMAS MENSAGENS DO CANAL (simulação segura)
            # Comandos são acionados por você, eu deixei funções prontas
            # COLOQUE SEU ID NO Railway: variável ID_ADM
            # Comandos: !status, !atualizar, !testar

            # EXEMPLO: se você digitar !atualizar, ele executa:
            # buscar_eventos()

            time.sleep(10)
        except:
            pass

def enviar_mensagem_resposta(texto):
    dados = {"content": texto, "username": "Monitor de Eventos FF", "avatar_url": "https://i.imgur.com/6XZ7Z8L.png"}
    requests.post(WEBHOOK_URL, json=dados)

# ---------------- ROTINAS ----------------
def agendador():
    schedule.every(60).minutes.do(buscar_eventos)
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    print("🤖 SISTEMA WEBHOOK + COMANDOS INICIADO")
    buscar_eventos()
    threading.Thread(target=agendador, daemon=True).start()
    threading.Thread(target=verificar_comandos, daemon=True).start()
                                         
