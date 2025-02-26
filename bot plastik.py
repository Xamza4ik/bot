import asyncio
import requests
from telethon import TelegramClient, events, Button

# Telegram API ma'lumotlari
API_ID = YOUR_API_ID
API_HASH = "YOUR_API_HASH"
BOT_TOKEN = "YOUR_BOT_TOKEN"

# Plastik karta ma'lumotlari
PLASTIC_CARD_NUMBER = "YOUR_PLASTIC_CARD_NUMBER"
ADMIN_ID = YOUR_ADMIN_TELEGRAM_ID

# Foydalanuvchi sozlamalarini saqlash uchun
db = {}

# Telegram botini ishga tushiramiz
client = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    user_id = event.sender_id
    if user_id not in db:
        db[user_id] = {"text": "Salom! Hozirda men onlayn emasman. Keyinroq yozing!", "delay": 2, "paid": False}
    
    if not db[user_id]["paid"]:
        buttons = [[Button.text("💳 Chekni yuborish")]]
        await event.respond(f"⚠ Ushbu bot pullik. To‘lovni quyidagi plastik karta raqamiga amalga oshiring:\n\n💳 {PLASTIC_CARD_NUMBER}\n\nTo‘lovdan so‘ng chekning rasmni yuboring!", buttons=buttons)
    else:
        await event.respond("👋 Salom! Siz obuna bo‘lgansiz! /settings orqali sozlamalarni o'zgartiring.")

@client.on(events.NewMessage(pattern='/settings'))
async def settings(event):
    user_id = event.sender_id
    if not db[user_id]["paid"]:
        await event.respond("⚠ Siz hali obuna bo‘lmagansiz! Chekni yuboring.")
        return
    
    buttons = [
        [Button.text("✍ Matnni o'zgartirish")],
        [Button.text("⏳ Kechikishni o'zgartirish")]
    ]
    await event.respond("⚙ Sozlamalarni tanlang:", buttons=buttons)

@client.on(events.NewMessage())
async def user_input(event):
    user_id = event.sender_id
    if event.text.startswith("/settext"):
        db[user_id]["text"] = event.text.split("/settext ", 1)[-1]
        await event.respond("✅ Avto-javob matni o'zgartirildi!")
    elif event.text.startswith("/setdelay"):
        try:
            delay = int(event.text.split("/setdelay ", 1)[-1])
            db[user_id]["delay"] = delay
            await event.respond(f"✅ Kechikish vaqti {delay} soniyaga o'zgartirildi!")
        except ValueError:
            await event.respond("❌ Xato! Son kiritishingiz kerak!")
    elif event.photo:
        if not db[user_id]["paid"]:
            # Adminga chekning rasmini yuborish
            await client.send_message(ADMIN_ID, f"📩 Yangi to‘lov cheki!\n👤 Foydalanuvchi ID: {user_id}", file=event.photo)
            await event.respond("✅ Chek qabul qilindi! Admin tomonidan tekshirilgandan so‘ng sizga xabar beriladi.")

@client.on(events.NewMessage(from_users=ADMIN_ID, pattern='/approve'))
async def approve_payment(event):
    try:
        user_id = int(event.text.split("/approve ", 1)[-1])
        db[user_id]["paid"] = True
        await client.send_message(user_id, "✅ To‘lov tasdiqlandi! Endi botdan foydalanishingiz mumkin.")
        await event.respond(f"✅ {user_id} foydalanuvchi to‘lov tasdiqlandi!")
    except Exception as e:
        await event.respond("❌ Xato! To‘g‘ri format: /approve USER_ID")

@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    user_id = event.sender_id
    if user_id in db and db[user_id]["paid"] and not event.is_group:
        await asyncio.sleep(db[user_id]["delay"])
        await event.reply(db[user_id]["text"])

async def main():
    print("🤖 Pullik avto-javob bot ishga tushdi! Plastik to‘lov qo‘lda tasdiqlanadi.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
