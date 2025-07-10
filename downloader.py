# downloader.py

import os

async def download_proof(context, file_id, user_id, ext="jpg"):
    try:
        file = await context.bot.get_file(file_id)
        folder = "bukti_transfer"
        os.makedirs(folder, exist_ok=True)
        filename = f"{folder}/user_{user_id}_{file_id}.{ext}"
        await file.download_to_drive(filename)
        print(f"✅ Bukti disimpan: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Gagal mengunduh file: {e}")
        return None
