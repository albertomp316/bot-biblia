import logging
import requests
from datetime import time
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

import os
# ─── CONFIGURAÇÃO ───
TOKEN = os.environ.get("8873195607:AAGT6rmvJeNeTFdwxleWdnJQGMgqkalcc30")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ─── VERSÍCULOS DO DIA ───
VERSICULOS = [
    {"texto": "Porque Deus amou o mundo de tal maneira que deu o seu Filho unigênito, para que todo aquele que nele crê não pereça, mas tenha a vida eterna.", "ref": "João 3:16"},
    {"texto": "Tudo posso naquele que me fortalece.", "ref": "Filipenses 4:13"},
    {"texto": "O Senhor é o meu pastor e nada me faltará.", "ref": "Salmos 23:1"},
    {"texto": "Porque eu bem sei os planos que tenho a vosso respeito, diz o Senhor; planos de paz, e não de mal, para vos dar um futuro e uma esperança.", "ref": "Jeremias 29:11"},
    {"texto": "Entrega o teu caminho ao Senhor; confia nele, e ele tudo fará.", "ref": "Salmos 37:5"},
    {"texto": "Sede fortes e corajosos. Não temais, nem vos assusteis diante deles, porque o Senhor, vosso Deus, é quem anda convosco.", "ref": "Deuteronômio 31:6"},
    {"texto": "A fé é o firme fundamento das coisas que se esperam e a prova das coisas que não se veem.", "ref": "Hebreus 11:1"},
    {"texto": "Mas os que esperam no Senhor renovarão as suas forças, subirão com asas como águias.", "ref": "Isaías 40:31"},
    {"texto": "Não andeis ansiosos por coisa alguma; antes, em tudo, pela oração e pela súplica com ação de graças.", "ref": "Filipenses 4:6"},
    {"texto": "O Senhor é a minha luz e a minha salvação; a quem temerei?", "ref": "Salmos 27:1"},
    {"texto": "Amor é paciente, amor é bondoso. Não inveja, não se vangloria, não se orgulha.", "ref": "1 Coríntios 13:4"},
    {"texto": "Vinde a mim, todos os que estais cansados e sobrecarregados, e eu vos aliviarei.", "ref": "Mateus 11:28"},
    {"texto": "Porque a palavra de Deus é viva, e eficaz, e mais cortante do que qualquer espada de dois gumes.", "ref": "Hebreus 4:12"},
    {"texto": "Teme ao Senhor teu Deus, serve-o, e apega-te a ele.", "ref": "Deuteronômio 10:20"},
    {"texto": "Em tudo dai graças, porque esta é a vontade de Deus em Cristo Jesus para convosco.", "ref": "1 Tessalonicenses 5:18"},
]

# ─── BANCO DE USUÁRIOS (simples em memória) ───
usuarios = set()

# ─── BUSCAR VERSÍCULO NA API ───
async def buscar_versiculo(referencia: str):
    try:
        url = f"https://bible-api.com/{referencia}?translation=almeida"
        res = requests.get(url, timeout=10)
        data = res.json()
        if "error" not in data:
            return {
                "texto": data.get("text", "").strip(),
                "ref": data.get("reference", referencia)
            }
    except:
        pass

    # Fallback segunda API
    try:
        url2 = f"https://bible-api.com/{referencia}"
        res2 = requests.get(url2, timeout=10)
        data2 = res2.json()
        if "error" not in data2:
            return {
                "texto": data2.get("text", "").strip(),
                "ref": data2.get("reference", referencia)
            }
    except:
        pass

    return None

# ─── COMANDO /start ───
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    usuarios.add(user_id)
    nome = update.effective_user.first_name

    teclado = [
        [InlineKeyboardButton("📖 Versículo do Dia", callback_data="versiculo_dia")],
        [InlineKeyboardButton("🔍 Pesquisar Versículo", callback_data="ajuda_pesquisa")],
        [InlineKeyboardButton("📚 Como Usar", callback_data="como_usar")],
    ]
    markup = InlineKeyboardMarkup(teclado)

    mensagem = (
        f"✝️ *Bem-vindo, {nome}!*\n\n"
        "Que a Palavra de Deus ilumine o seu dia.\n\n"
        "Aqui você pode:\n"
        "📖 Receber um versículo todo dia\n"
        "🔍 Pesquisar qualquer versículo da Bíblia\n"
        "🙏 Se fortalecer na fé\n\n"
        "_Escolha uma opção abaixo:_"
    )

    await update.message.reply_text(mensagem, parse_mode="Markdown", reply_markup=markup)

# ─── COMANDO /versiculo ───
async def versiculo_dia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    v = random.choice(VERSICULOS)
    mensagem = (
        f"✝️ *Palavra do Dia*\n\n"
        f"_{v['texto']}_\n\n"
        f"📖 *{v['ref']}*\n\n"
        f"🙏 Que essa palavra abençoe o seu dia!"
    )
    await update.message.reply_text(mensagem, parse_mode="Markdown")

# ─── COMANDO /pesquisar ───
async def pesquisar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "📖 *Como pesquisar:*\n\n"
            "Digite o comando seguido da referência:\n\n"
            "Exemplos:\n"
            "`/pesquisar João 3:16`\n"
            "`/pesquisar Salmos 23:1`\n"
            "`/pesquisar Filipenses 4:13`",
            parse_mode="Markdown"
        )
        return

    referencia = " ".join(context.args)
    await update.message.reply_text("🔍 Buscando versículo...")

    resultado = await buscar_versiculo(referencia)

    if resultado:
        mensagem = (
            f"📖 *{resultado['ref']}*\n\n"
            f"_{resultado['texto']}_\n\n"
            f"🙏 _Que a Palavra de Deus abençoe você!_"
        )
    else:
        mensagem = (
            "❌ Versículo não encontrado.\n\n"
            "Tente no formato:\n"
            "`/pesquisar João 3:16`\n"
            "`/pesquisar Salmos 23`"
        )

    await update.message.reply_text(mensagem, parse_mode="Markdown")

# ─── COMANDO /ajuda ───
async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensagem = (
        "📚 *Como usar o bot:*\n\n"
        "✅ /start — Menu principal\n"
        "✅ /versiculo — Versículo do dia\n"
        "✅ /pesquisar João 3:16 — Pesquisar versículo\n"
        "✅ /ajuda — Ver essa mensagem\n\n"
        "*Exemplos de pesquisa:*\n"
        "`/pesquisar Salmos 23:1`\n"
        "`/pesquisar Mateus 5:3`\n"
        "`/pesquisar Romanos 8:28`\n\n"
        "🙏 _Que Deus abençoe você!_"
    )
    await update.message.reply_text(mensagem, parse_mode="Markdown")

# ─── BOTÕES INLINE ───
async def botoes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "versiculo_dia":
        v = random.choice(VERSICULOS)
        mensagem = (
            f"✝️ *Palavra do Dia*\n\n"
            f"_{v['texto']}_\n\n"
            f"📖 *{v['ref']}*\n\n"
            f"🙏 Que essa palavra abençoe o seu dia!"
        )
        await query.edit_message_text(mensagem, parse_mode="Markdown")

    elif query.data == "ajuda_pesquisa":
        mensagem = (
            "🔍 *Como pesquisar versículos:*\n\n"
            "Digite no chat:\n\n"
            "`/pesquisar João 3:16`\n"
            "`/pesquisar Salmos 23:1`\n"
            "`/pesquisar Filipenses 4:13`\n\n"
            "_Use o nome do livro em português!_"
        )
        await query.edit_message_text(mensagem, parse_mode="Markdown")

    elif query.data == "como_usar":
        mensagem = (
            "📚 *Comandos disponíveis:*\n\n"
            "✅ /start — Menu principal\n"
            "✅ /versiculo — Versículo do dia\n"
            "✅ /pesquisar João 3:16 — Pesquisar\n"
            "✅ /ajuda — Ajuda\n\n"
            "🙏 _Que Deus abençoe você!_"
        )
        await query.edit_message_text(mensagem, parse_mode="Markdown")

# ─── ENVIO AUTOMÁTICO DIÁRIO ───
async def enviar_palavra_diaria(context: ContextTypes.DEFAULT_TYPE):
    if not usuarios:
        return

    v = random.choice(VERSICULOS)
    mensagem = (
        f"🌅 *Bom dia! Palavra do Dia:*\n\n"
        f"_{v['texto']}_\n\n"
        f"📖 *{v['ref']}*\n\n"
        f"🙏 Que Deus abençoe o seu dia!\n\n"
        f"_Use /pesquisar para buscar qualquer versículo_"
    )

    for user_id in usuarios.copy():
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=mensagem,
                parse_mode="Markdown"
            )
        except Exception as e:
            logging.warning(f"Erro ao enviar para {user_id}: {e}")
            usuarios.discard(user_id)

# ─── MENSAGENS DE TEXTO LIVRES ───
async def mensagem_livre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.lower()

    if any(p in texto for p in ["joão", "salmos", "mateus", "lucas", "marcos",
                                  "romanos", "genesis", "gênesis", "atos",
                                  "filipenses", "efésios", "hebreus"]):
        await update.message.reply_text(
            f"🔍 Quer pesquisar esse versículo? Use:\n\n"
            f"`/pesquisar {update.message.text}`",
            parse_mode="Markdown"
        )
    else:
        teclado = [
            [InlineKeyboardButton("📖 Versículo do Dia", callback_data="versiculo_dia")],
            [InlineKeyboardButton("📚 Como Usar", callback_data="como_usar")],
        ]
        markup = InlineKeyboardMarkup(teclado)
        await update.message.reply_text(
            "🙏 Use os comandos abaixo para navegar:",
            reply_markup=markup
        )

# ─── MAIN ───
def main():
    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("versiculo", versiculo_dia))
    app.add_handler(CommandHandler("pesquisar", pesquisar))
    app.add_handler(CommandHandler("ajuda", ajuda))
    app.add_handler(CallbackQueryHandler(botoes))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensagem_livre))

    # Agendamento da palavra diária às 8h da manhã
    app.job_queue.run_daily(
        enviar_palavra_diaria,
        time=time(hour=8, minute=0),
    )

    print("✝️ Bot da Bíblia rodando! Pressione Ctrl+C para parar.")
    app.run_polling()

if __name__ == "__main__":
    main()
