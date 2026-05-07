from fastapi import FastAPI
import uvicorn
from datetime import datetime

app = FastAPI(
    title="Scanner Profissional Free Fire",
    description="Sistema de detecção e alerta de eventos para Discord",
    version="6.0-PRO"
)

@app.get("/")
def painel_principal():
    return {
        "status": "✅ ONLINE E FUNCIONANDO",
        "versao": "6.0-PRO",
        "discord_webhook": "✅ CONFIGURADO",
        "funcionalidades": [
            "Varre arquivos do servidor do jogo",
            "Varre site oficial, notícias e loja",
            "Varre APIs oficiais de dados",

          
