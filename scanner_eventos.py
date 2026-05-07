# ==================================================
# 🕵️ SCANNER DE EVENTOS FREE FIRE - VERSÃO PRO 🕵️
# 📢 DISCORD INTEGRADO | VARIÁVEIS TODAS AQUI 📌
# ==================================================

import requests
import json
import time
import re
from bs4 import BeautifulSoup
from datetime import datetime
from jsonpath_ng import parse
from dateutil import parser

# ==================================================
# ⚙️ TODAS AS VARIÁVEIS E CONFIGURAÇÕES AQUI ⚙️
# ==================================================

# 📌 DADOS DO SISTEMA
VERSAO = "6.0-PRO"
REGIAO = "BR"
IDIOMA = "pt-BR"
NOME_BOT = "Scanner FF Oficial"
COR_EMBED = 0xE74C3C  # Vermelho Garena

# 🔗 LINKS E WEBHOOKS (JÁ COM SEU LINK!)
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1502050535073644666/9F9USfLqSQubFBidh_akybynCZXwvJ3ogzHlGGAJm3ahZSS36IXzhCF043CSfbFwDze-"
API_DASHBOARD = "http://0.0.0.0:8000/api/salvar-evento"  # Não alterar

# 🌐 LINKS DE VARREDURA
URL_API = "https://clientbp.ggblueshark.com"
URL_SITE_OFICIAL = "https://ff.garena.com"
URL_ATUALIZACOES = "https://ff-config-ota.garena.com"
URL_LOJA = "https://store.garena.com.br"
URL_API_DADOS = "https://api-ff.garena.com/v2/events"
URL_REDES = "https://www.instagram.com/garenafreefirebr/"

# ⏱️ TEMPO DE VARREDURA (EM SEGUNDOS)
INTERVALO_VARREDURA = 900  # 15 minutos = 900 segundos

# 📌 PALAVRAS-CHAVE PARA DETECÇÃO
PALAVRAS_ALVO = [
    "evento", "lançamento", "data de lançamento", "disponível em", "a partir de",
    "pacote", "bundle", "skin", "arma", "passe de elite", "recompensa", "grátis",
    "incubadora", "roleta", "parceria", "codiguin", "resgate", "atualização",
    "personagem", "nova arma", "mochila", "capa", "emote", "chegando", "em breve"
]

# 📌 PADRÕES PARA EXTRAIR DATAS
PADROES_DATA = [
    r"(\d{1,2} de [a-zçã]{3,10} de \d{4})",
    r"(\d{2}/\d{2}/\d{4})",
    r"(\d{4}-\d{2}-\d{2})",
    r"disponível em (\d{1,2} \w+)",
    r"a partir de (\d{1,2} de [a-zçã]+)"
]

# 📌 ARMAZENA O QUE JÁ FOI ENVIADO (EVITA REPETIÇÃO)
ENVIADOS = set()

# ==============================================
# 📢 FUNÇÃO: MENSAGEM PROFISSIONAL PARA DISCORD
# ==============================================
def enviar_evento_discord(titulo, data_lancamento, detalhes, itens, imagem_url=None):
    """Envia mensagem formatada profissionalmente com todos os campos"""
    try:
        # Cria ID único
        id_unico = f"{titulo}-{data_lancamento}"
        if id_unico in ENVIADOS:
            return

        # 🔹 EMBED PROFISSIONAL
        embed = {
            "author": {
                "name": "🚨 NOVO EVENTO DETECTADO | FREE FIRE",
                "icon_url": "https://i.imgur.com/9QZ7QZL.png"
            },
            "title": f"📌 {titulo.upper()}",
            "color": COR_EMBED,
            "fields": [
                {
                    "name": "📅 DATA DE LANÇAMENTO",
                    "value": f"```fix\n{data_lancamento if data_lancamento else 'Não definida / Em breve'}```",
                    "inline": False
                },
                {
                    "name": "📝 DETALHES DO EVENTO",
                    "value": f"```md\n{detalhes if detalhes else 'Nenhuma informação detalhada encontrada.'}```",
                    "inline": False
                },
                {
                    "name": "🎒 ITENS QUE IRÃO CHEGAR",
                    "value": f"```yaml\n{itens if itens else 'Nenhum item específico detectado.'}```",
                    "inline": False
                }
            ],
            "footer": {
                "text": f"Scanner Profissional FF • Detectado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                "icon_url": "https://i.imgur.com/2X7y9.png"
            },
            "timestamp": datetime.utcnow().isoformat()
        }

        # Adiciona imagem se existir
        if imagem_url:
            embed["image"] = {"url": imagem_url}

        # 🔹 DADOS DO WEBHOOK
        payload = {
            "username": NOME_BOT,
            "avatar_url": "https://i.imgur.com/7Z7Z7Z7.png",
            "embeds": [embed]
        }

        # 🔹 ENVIA PARA DISCORD
        resposta = requests.post(DISCORD_WEBHOOK, json=payload, timeout=15)
        if resposta.status_code in [200, 204]:
            print(f"✅ ENVIADO AO DISCORD: {titulo}")
            ENVIADOS.add(id_unico)
            
            # 🔹 SALVA NO DASHBOARD
            try:
                requests.post(API_DASHBOARD, json={
                    "titulo": titulo,
                    "data": data_lancamento,
                    "detalhes": detalhes,
                    "itens": itens,
                    "imagem": imagem_url
                }, timeout=5)
            except:
                pass
        else:
            print(f"⚠️ ERRO DISCORD: Status {resposta.status_code}")

    except Exception as e:
        print(f"❌ FALHA: {str(e)}")

# ==============================================
# 🧩 FUNÇÕES DE EXTRAÇÃO DE DADOS
# ==============================================
def extrair_data(texto):
    """Busca padrões de data no texto"""
    for padrao in PADROES_DATA:
        match = re.search(padrao, texto, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None

def extrair_itens(texto):
    """Extrai lista de itens/objetos mencionados"""
    itens_encontrados = []
    palavras_itens = ["pacote", "skin", "arma", "mochila", "emote", "capacete", "parada", "asa-delta", "pingente", "personagem"]
    for p in palavras_itens:
        if p in texto.lower():
            trechos = re.findall(rf'{p}[\w\sçãõéíúáàâêô]*', texto.lower())
            itens_encontrados.extend(trechos)
    return "\n- ".join(itens_encontrados).capitalize() if itens_encontrados else None

# ==============================================
# 🔍 VARREDURA: ARQUIVOS DO SERVIDOR
# ==============================================
def varrer_arquivos_jogo():
    print("\n🔍 [1/4] VARRENDO ARQUIVOS DO SERVIDOR...")
    try:
        endpoints = [
            f"{URL_API}/Config/GetConfig?region={REGIAO}&lang={IDIOMA}",
            f"{URL_API}/Home/GetHomeInfo?region={REGIAO}&lang={IDIOMA}",
            f"{URL_ATUALIZACOES}/config/Android/versions/version_{REGIAO.lower()}.json"
        ]

        for url in endpoints:
            res = requests.get(url, timeout=20, headers={"User-Agent": "GarenaFF/1.0"})
            if res.status_code == 200:
                try:
                    dados = res.json()
                    texto_str = json.dumps(dados).lower()

                    for palavra in PALAVRAS_ALVO:
                        if palavra in texto_str:
                            titulo = palavra.upper() + " - Servidor Oficial"
                            data = extrair_data(texto_str) or "A confirmar"
                            detalhes = "Informação detectada diretamente nos arquivos de configuração do jogo.\nFonte: Servidor Garena"
                            itens = extrair_itens(texto_str) or "Verificar detalhes no lançamento"
                            
                            img_match = re.search(r'(https?://[^\s"]+\.(jpg|png|webp))', texto_str)
                            img_url = img_match.group(1) if img_match else None

                            enviar_evento_discord(titulo, data, detalhes, itens, img_url)
                            break
                except:
                    continue
    except Exception as e:
        print(f"⚠️ Erro: {e}")

# ==============================================
# 🔍 VARREDURA: SITE OFICIAL
# ==============================================
def varrer_site_oficial():
    print("\n🔍 [2/4] VARRENDO SITE E NOTÍCIAS...")
    try:
        paginas = ["/news", "/events", "/updates"]
        for caminho in paginas:
            res = requests.get(f"{URL_SITE_OFICIAL}{caminho}", timeout=15)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                
                artigos = soup.find_all("div", class_=["news-item", "event-card", "article"])
                for art in artigos:
                    titulo_tag = art.find(["h2", "h3"])
                    if not titulo_tag: continue
                    
                    titulo = titulo_tag.get_text(strip=True)
                    texto = art.get_text(" ", strip=True)
                    
                    if any(p in texto.lower() for p in PALAVRAS_ALVO):
                        data = extrair_data(texto) or "Em breve"
                        detalhes = texto[:300] + "..." if len(texto) > 300 else texto
                        itens = extrair_itens(texto) or "Conteúdo exclusivo do evento"
                        
                        img_tag = art.find("img")
                        img_url = img_tag.get("src") if img_tag else None
                        if img_url and not img_url.startswith("http"):
                            img_url = URL_SITE_OFICIAL + img_url

                        enviar_evento_discord(titulo, data, detalhes, itens, img_url)

    except Exception as e:
        print(f"⚠️ Erro: {e}")

# ==============================================
# 🔍 VARREDURA: API DE DADOS
# ==============================================
def varrer_api_dados():
    print("\n🔍 [3/4] VARRENDO API DE DADOS...")
    try:
        res = requests.get(URL_API_DADOS, timeout=15)
        if res.status_code == 200:
            dados = res.json()
            if "data" in dados:
                for evento in dados["data"]:
                    nome = evento.get("name", "Evento sem nome")
                    desc = evento.get("description", "Detalhes não informados")
                    data_inicio = evento.get("start_date", None)
                    img = evento.get("image", None)
                    
                    try:
                        data_formatada = parser.parse(data_inicio).strftime("%d/%m/%Y") if data_inicio else "A definir"
                    except:
                        data_formatada = data_inicio or "Em breve"

                    itens = extrair_itens(desc) or "Pacotes, skins e recompensas variadas"
                    enviar_evento_discord(nome, data_formatada, desc, itens, img)

    except Exception as e:
        print(f"⚠️ Erro: {e}")

# ==============================================
# 🔍 VARREDURA: LOJA E PARCEIROS
# ==============================================
def varrer_loja_parceiros():
    print("\n🔍 [4/4] VARRENDO LOJA OFICIAL...")
    try:
        res = requests.get(URL_LOJA, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            produtos = soup.find_all("div", class_=["product", "item"])
            
            for prod in produtos:
                nome = prod.find(["h3", "span"])
                if not nome: continue
                nome_txt = nome.get_text(strip=True)
                texto = prod.get_text(" ", strip=True)

                if any(p in texto.lower() for p in ["novo", "lançamento", "chegando"]):
                    data = extrair_data(texto) or "Próximos dias"
                    detalhes = "Disponível para compra na Loja Oficial Garena.\n" + texto[:150]
                    itens = extrair_itens(texto) or nome_txt
                    img = prod.find("img")
                    img_url = img.get("src") if img else None

                    enviar_evento_discord(nome_txt, data, detalhes, itens, img_url)

    except Exception as e:
        print(f"⚠️ Erro: {e}")

# ==============================================
# 🚀 LOOP PRINCIPAL
# ==============================================
if __name__ == "__main__":
    print("="*70)
    print(f"🚀 SCANNER FF {VERSAO} | DISCORD 🚀")
    print(f"🌐 REGIÃO: {REGIAO} | IDIOMA: {IDIOMA}")
    print(f"⏱️ INTERVALO: {INTERVALO_VARREDURA/60:.0f} minutos")
    print("="*70)

    while True:
        hora_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f"\n⏳ INICIANDO VARREDURA: {hora_atual}")

        # Executa todas as buscas
        varrer_arquivos_jogo()
        varrer_site_oficial()
        varrer_api_dados()
        varrer_loja_parceiros()

        print(f"\n✅ CONCLUÍDO! Próxima em {INTERVALO_VARREDURA/60:.0f} minutos...")
        time.sleep(INTERVALO_VARREDURA)
