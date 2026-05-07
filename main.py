import requests
from bs4 import BeautifulSoup
import schedule
import time
import json
import re
from datetime import datetime

# ---------------- CONFIGURAÇÕES PRONTAS ----------------
WEBHOOK_DISCORD = "https://discord.com/api/webhooks/1502050535073644666/9F9USfLqSQubFBidh_akybynCZXwvJ3ogzHlGGAJm3ahZSS36IXzhCF043CSfbFwDze-"

FONTES = [
    "https://ff.garena.com/news/pt",
    "https://ff.garena.com/updates/pt",
    "https://garenafreefire.com.br/noticias/",
    "https://www.freefiremania.com.br/noticias/"
]

ARQUIVO_HISTORICO = "eventos_encontrados.json"
PALAVRAS_CHAVE = ["evento", "lançamento", "chegando", "próximo", "atualização", "novo", "breve", "em breve", "recompensa", "passe", "pacote", "skin", "temporada"]
# ---------------------------------------------------------

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
    """Mensagem 100% profissional formatada"""
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

    dados = {
        "content": mensagem,
        "username": "Monitor de Eventos FF",
        "avatar_url": "https://i.imgur.com/6XZ7Z8L.png"
    }

    if imagem:
        dados["embeds"] = [
            {
                "image": {"url": imagem},
                "color": 16711680
            }
        ]

    try:
        requests.post(WEBHOOK_DISCORD, json=dados)
        print("✅ Notificação enviada ao Discord com sucesso")
    except Exception as e:
        print(f"❌ Erro ao enviar notificação: {str(e)}")

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

                # Definir data de lançamento
                data_lancamento = "A ser definida | Em breve"
                padroes_data = [
                    r'\d{2}/\d{2}/\d{4}',
                    r'\d{1,2} de \w+ de \d{4}',
                    r'\d{1,2} de \w+',
                    r'em \d{2}/\d{2}'
                ]
                for padrao in padroes_data:
                    encontro = re.search(padrao, detalhes.lower() + " " + titulo.lower())
                    if encontro:
                        data_lancamento = encontro.group(0).capitalize()
                        break

                # Definir itens que chegarão
                itens = "• Pacotes e visuais exclusivos\n• Skins de armas e acessórios\n• Recompensas por missões diárias\n• Itens temáticos do evento"
                if "passe" in titulo.lower():
                    itens += "\n• Passe de Elite completo com recompensas"
                if "parceria" in titulo.lower() or "colaboração" in titulo.lower():
                    itens += "\n• Conteúdos exclusivos da parceria especial"
                if "atualização" in titulo.lower():
                    itens += "\n• Novos mapas, modos e mecânicas de jogo"

                # Enviar e salvar
                enviar_discord(titulo, data_lancamento, detalhes, itens, imagem)
                historico.add(titulo)
                time.sleep(1)

        except Exception as e:
            print(f"⚠️ Falha ao consultar {url}: {str(e)}")

    salvar_historico(historico)
    print("✅ Verificação finalizada")

# Verifica a cada 60 minutos
schedule.every(60).minutes.do(buscar_eventos)

if __name__ == "__main__":
    print("🤖 MONITOR DE EVENTOS FREE FIRE - INICIADO")
    print("🔹 Modo: Profissional | 🔹 Intervalo: 60min | 🔹 Saída: Discord")
    buscar_eventos()
    while True:
        schedule.run_pending()
        time.sleep(30)
    
