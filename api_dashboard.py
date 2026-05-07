from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
import uvicorn
import json
import os
from datetime import datetime
from typing import List, Dict

# ==================================================
# 🖥️ DASHBOARD SCANNER FF | VARIÁVEIS CENTRAIS 🖥️
# ==================================================

# 📌 VARIÁVEIS DO SISTEMA
VERSAO = "6.0-PRO"
NOME_SISTEMA = "Scanner Profissional Free Fire"
ARQUIVO_DADOS = "eventos_detectados.json"
ARQUIVO_LOGS = "logs_sistema.txt"
DISCORD_STATUS = "ATIVO ✅"
WEBHOOK_LINK = "https://discord.com/api/webhooks/1502050535073644666/..."

app = FastAPI(
    title=NOME_SISTEMA,
    description="Painel de Controle | Detecção de Eventos + Discord",
    version=VERSAO,
    docs_url="/docs",
    redoc_url="/redoc"
)

# ==============================================
# 📌 FUNÇÕES AUXILIARES
# ==============================================
def carregar_eventos_salvos() -> List[Dict]:
    
