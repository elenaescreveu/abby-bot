from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)
import random
import asyncio
import json
import os
from datetime import datetime, date

TOKEN = "8283057776:AAGoSORGMdfJmtSh6LAGarM-oTukQrvd9w8"
MEMORIA_ARQ = "memoria.json"

# ======================
# MEMÓRIA
# ======================

def carregar_memoria():
    if not os.path.exists(MEMORIA_ARQ):
        return {"usuarios": {}, "confissoes": {}, "stats": {"total_mensagens": 0, "total_confissoes": 0}}
    with open(MEMORIA_ARQ, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_memoria():
    with open(MEMORIA_ARQ, "w", encoding="utf-8") as f:
        json.dump(memoria, f, ensure_ascii=False, indent=2)

memoria = carregar_memoria()

# ======================
# LINKS
# ======================

LINK_SOMBRAS = "https://www.amazon.com.br/Sombras-Tempo-romance-desafia-viagem-ebook/dp/B0FCHNC5B7"
LINK_CURVA = "https://www.wattpad.com/myworks/407471594-antes-da-curva"
PERFIL_ELENA_TIKTOK = "https://www.tiktok.com/@elenaescreveu?_r=1&_t=ZS-93hzxBfee9N"
PERFIL_ELENA_INSTAGRAM = "https://www.instagram.com/elenaescreveu?igsh=MWprbnY5ZXJnY3MzaQ=="
PERFIL_ELENA_KWAI = "https://k.kwai.com/u/@elenaescreveu/lhbqaCyF"


# ======================
# FRASES
# ======================

respostas_base = [
    "Não sei o que você espera ouvir.",
    "Você parece cansado.",
    "Isso diz mais sobre você do que parece.",
    "Nem tudo precisa de resposta."
]

respostas_intimas = [
    "Você sempre acaba aqui.",
    "Já devia ter aprendido… mas voltou.",
    "Eu reconheceria esse silêncio."
]

confissoes_fracas = [
    "Nem tudo que você perde foi tirado.",
    "Algumas verdades não pedem permissão."
]

confissoes_fortes = [
    "Você ainda vive algo que já acabou.",
    "O que te dói hoje começou há muito tempo.",
    "Você não superou. Só se distraiu."
]

reconhecimento = [
    "Você voltou.",
    "De novo você.",
    "Achei que não voltaria."
]

# ======================
# UTIL
# ======================

def humor_por_hora():
    h = datetime.now().hour
    if 0 <= h < 6:
        return "madrugada"
    if h < 18:
        return "dia"
    return "noite"

def nivel_vinculo(user):
    msgs = memoria["usuarios"][user]["mensagens"]
    if msgs > 30:
        return "alto"
    if msgs > 10:
        return "medio"
    return "baixo"

def resposta_baseada_em_vinculo(user):
    nivel = nivel_vinculo(user)
    base = random.choice(respostas_base)
    if nivel == "alto":
        base = random.choice(respostas_intimas)
    humor = humor_por_hora()
    if humor == "madrugada":
        base += "\n\nVocê devia estar dormindo."
    elif humor == "noite":
        base += "\n\nÀ noite tudo pesa mais."
    return base

# ======================
# COMANDOS
# ======================

async def start(update, context):
    user = str(update.effective_user.id)
    nome = update.effective_user.first_name

    if user not in memoria["usuarios"]:
        memoria["usuarios"][user] = {
            "nome": nome,
            "mensagens": 0,
            "primeira_vez": str(datetime.now())
        }
        salvar_memoria()
        msg = (
            "Então… você me achou.\n"
            "Não sei se isso é bom ou ruim.\n"
            "Mas agora já foi."
        )
    else:
        msg = random.choice(reconhecimento)

    await update.message.reply_text(msg)

async def confissao(update, context):
    user = str(update.effective_user.id)
    hoje = str(date.today())

    if memoria["confissoes"].get(user) == hoje:
        await update.message.reply_text("Hoje não.")
        return

    memoria["confissoes"][user] = hoje
    memoria["stats"]["total_confissoes"] += 1
    salvar_memoria()

    await asyncio.sleep(random.choice([4, 6, 8]))

    nivel = nivel_vinculo(user)
    if nivel == "alto":
        texto = random.choice(confissoes_fortes)
    else:
        texto = random.choice(confissoes_fracas)

    await update.message.reply_text(texto)

async def onde_te_acho(update, context):
    texto = (
        "Se for procurar histórias:\n\n"
        f"Sombras do Tempo:\n{LINK_SOMBRAS}\n\n"
        f"Antes da Curva:\n{LINK_CURVA}\n\n"
        f"Quem escreve isso:\n{PERFIL_ELENA_TIKTOK}"
        f"Quem escreve isso:\n{PERFIL_ELENA_INSTAGRAM}"
        f"Quem escreve isso:\n{PERFIL_ELENA_KWAI}"
    )
    await update.message.reply_text(texto)

# ======================
# CONVERSA
# ======================

gatilhos = ["livro", "história", "ler", "passado", "escrever"]

async def conversar(update, context):
    texto = update.message.text.lower()
    user = str(update.effective_user.id)

    if texto.startswith("/"):
        return

    if user not in memoria["usuarios"]:
        memoria["usuarios"][user] = {
            "nome": update.effective_user.first_name,
            "mensagens": 0,
            "primeira_vez": str(datetime.now())
        }

    memoria["usuarios"][user]["mensagens"] += 1
    memoria["stats"]["total_mensagens"] += 1
    salvar_memoria()

    await asyncio.sleep(random.choice([2, 4, 6]))
    resposta = resposta_baseada_em_vinculo(user)

    if any(p in texto for p in gatilhos):
        resposta += f"\n\nTalvez isso te interesse:\n{PERFIL_ELENA_INSTAGRAM}"
    elif random.random() < 0.08:
        resposta += f"\n\n{LINK_SOMBRAS}"

    await update.message.reply_text(resposta)

# ======================
# APP
# ======================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("confissao", confissao))
app.add_handler(CommandHandler("onde_te_acho", onde_te_acho))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, conversar))

app.run_polling()
