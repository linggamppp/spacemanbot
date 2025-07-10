# SPACEMAN bot by LINGGA MANDALA PUTRA
import random
import hashlib
import os
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, ConversationHandler, filters
)
from downloader import download_proof


TOKEN = os.getenv('TOKEN')  # Ganti token dari BotFather
paid_users = set()
WAITING_PROOF = range(1)

def predict_result():
    now = datetime.now()
    i = 0
    fib = 1.618
    result = []
    for _ in range(5):
        i += fib
        future = now + timedelta(minutes=i)
        hash_input = future.strftime('%H%M')
        hash = hashlib.sha512(hash_input.encode('utf-8'), usedforsecurity=True).hexdigest()
        random.seed(hash)
        if random.random() < 0.144:
            multiplier = random.randint(6, 10)
        else:
            multiplier = random.randint(2, 5)
        result.append(f"{future.strftime('%H:%M')} | {multiplier}x or up")
    return "\n".join(result)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🔮 Prediksi"],
        ["📤 Verifikasi", "💳 Info Pembayaran"],
        ["❌ Tutup Menu"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "👋 Selamat datang di *Spaceman Predictor Bot!*\n\n"
        "Gunakan tombol menu di bawah ini untuk mengakses fitur.",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def predict_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in paid_users:
        await update.message.reply_text("🚫 Kamu belum memiliki akses. Silakan verifikasi pembayaran terlebih dahulu.")
        return
    prediction = predict_result()
    await update.message.reply_text(f"📈 Prediksi:\n{prediction}")

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📤 Silakan kirim screenshot bukti transfer kamu sekarang.")
    return WAITING_PROOF

async def handle_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        print(f"📷 Bukti foto dari user ID {user_id} | File ID: {file_id}")
        await download_proof(context, file_id, user_id, ext="jpg")
        await update.message.reply_text("✅ Bukti pembayaran diterima. \n\nAdmin akan verifikasi manual paling lambat 1x24 jam.")

    elif update.message.document:
        file_id = update.message.document.file_id
        file_name = update.message.document.file_name
        ext = file_name.split('.')[-1] if '.' in file_name else "file"
        print(f"📎 Bukti file dari user ID {user_id} | File ID: {file_id}")
        await download_proof(context, file_id, user_id, ext=ext)
        await update.message.reply_text("✅ Bukti pembayaran diterima. \n\nAdmin akan verifikasi manual paling lambat 1x24 jam.")

    else:
        await update.message.reply_text("❌ Format tidak dikenali. Kirim foto berformat .PNG / .JPG / .JPEG")
        return WAITING_PROOF

    return ConversationHandler.END


async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🔮 Prediksi":
        await predict_command(update, context)
    elif text == "📤 Verifikasi":
        return await verify(update, context)
    elif text == "💳 Info Pembayaran":
        await update.message.reply_text(
            "💰 Harga akses: *Rp 50.000*\n\n"
            "Transfer ke:\n\n"
            "BCA `8515102996` a.n. Lingga Mandala Putra\n"
            "DANA `081369795045` a.n. Lingga Mandala Putra\n"
            "OVO `081369795045` a.n. Lingga Mandala Putra\n"
            "GOPAY `081369795045` a.n. Lingga Mandala Putra\n"
            "\nSetelah bayar, klik 📤 Verifikasi dan kirim screenshot bukti pembayaran.",
            parse_mode="Markdown"
        )
    elif text == "❌ Tutup Menu":
        await update.message.reply_text("✅ Menu ditutup. Ketik /start untuk membuka kembali.", reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text("Silakan pilih menu yang tersedia.")

# Admin manual approval
def approve_user(user_ids):
    if isinstance(user_ids, int):
        user_ids = [user_ids]

    for uid in user_ids:
        paid_users.add(uid)
        print(f"✅ User {uid} sudah diberi akses.")


if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("predict", predict_command))

    approve_user([
        1529842786,
    ])

    conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^📤 Verifikasi$"), verify)],
    states={
        WAITING_PROOF: [
            MessageHandler(filters.PHOTO | filters.Document.ALL | filters.TEXT, handle_proof)
        ]
    },
    fallbacks=[],
)

    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))

    print("🚀 Bot aktif...")
    app.run_polling()
