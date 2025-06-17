#імпортовані бібліотеки
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters, ConversationHandler
)
import sqlite3

# Тексти повідомлень
ABOUT = (
    "Сайт https://homkazapas.pp.ua/ створений в лютому 2025 року, але до цього з листопада 2017року працювали виключно в групі Хомячі запаси https://www.facebook.com/groups/bead10 і групі Замовлення Хомячі запаси https://www.facebook.com/zakazhomiakzapas в Facebook . Основним напрямком діяльності є продаж бісеру та супутніх товарів-фурнітури, інструментів, намистин, пакування, тощо."
)

QUESTION_ABOUT = (
    "Відповіді на ваші запитання:\n"
    "❓Які є види доставок? \n"
    "💡Доставка-Нова пошта або Укрпошта.\n"
    "\n"
    "❓Чи є накладний платіж?\n"
    "💡Накладного платежа немає.\n"
    "\n"
    "❓Чи є безкоштовна доставка?\n"
    "💡Безкоштовна доставка при замовленнях від 3000 грн.\n"
    "\n"
    "❓Що робити якщо немає потрібних мені позицій на сайті?\n"
    "💡Якщо потрібних вам позицій немає на сайті, то їх можна дописати в коментарі.\n"
    "\n"
    "❓Який термін обробки замовлення?\n"
    "💡1-2 дні для наявних товарів, 3-7 днів під замовлення.\n"
    "\n"
    "❓Коли завмовляєте зі складу?\n"
    "💡Щовівторка замовлення, в середу-четвер — оновлення на сайті.\n"
    "\n"
    "❓Коли оплачується замовлення?\n"
    "💡оплачується лише після підтвердження що замовлення зібрано на рахунок ФОП.\n"
)

ORDER_INFO = (
    "🛒 **Як оформити замовлення?**\n"
    "*Через сайт або повідомлення на сторінці Facebook «Замовлення Хомячі запаси»."
)

CONTACT = (
    "📞 Якщо виникли питання, звертайтесь:\n"
    "• Facebook: https://www.facebook.com/zakazhomiakzapas/\n"
    "• Телефон: +380993220877"
)

SITE_LINK = ("🌐 Перейти на сайт: https://homkazapas.pp.ua \n"
             "\n"
             "🌐 перейти на групу замовлень Facebook: https://www.facebook.com/zakazhomiakzapas/"
)


# функції опитування
Q1, Q2, Q3 = range(3)

# функція старт та варіанти
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🛒 Як оформити замовлення", "📞 Додаткова інформація"],
        ["ℹ️ Про магазин", "🌐 Перейти на сайт та групу facebook", "💡відповіді на ваші запитання"],
        ["📝 Опитування"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Ласкаво просимо до Хомячих запасів! Оберіть опцію в меню:", reply_markup=reply_markup)

# повідомлення
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "замовлення" in text:
        await update.message.reply_text(ORDER_INFO)
    elif "Додаткова" in text:
        await update.message.reply_text(CONTACT)
    elif "Про магазин" in text:
        await update.message.reply_text(ABOUT)
    elif "Перейти" in text:
        await update.message.reply_text(SITE_LINK)
    elif "запитання" in text:
        await update.message.reply_text(QUESTION_ABOUT)
    else:
        await update.message.reply_text("🔍 Я вас не розумію. Оберіть опцію з меню.")

# Варіанти опитування
async def survey_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📝 Опитування\n\n1. Чи сподобався вам наш сайт? (Так/Ні/Інше)")
    return Q1

async def survey_q1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_response(update, "Сайт", update.message.text)
    await update.message.reply_text("2. Чи задоволені ви роботою телеграм-бота? (Так/Ні/Інше)")
    return Q2

async def survey_q2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_response(update, "Бот", update.message.text)
    await update.message.reply_text("3. Якість послуг (Добре/Погано/Інше):")
    return Q3

async def survey_q3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_response(update, "Якість", update.message.text)
    await update.message.reply_text("✅ Дякуємо за проходження опитування!")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Опитування скасовано.")
    return ConversationHandler.END

# Збереження в БД
def save_response(update, question, answer):
    conn = sqlite3.connect("survey.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO survey (user_id, question, answer) VALUES (?, ?, ?)",
                   (update.effective_user.id, question, answer))
    conn.commit()
    conn.close()

# Ініціалізація БД
def init_db():
    conn = sqlite3.connect("survey.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS survey (
            user_id INTEGER,
            question TEXT,
            answer TEXT
        )
    """)
    conn.commit()
    conn.close()

# функція main
def main():
    init_db()

    app = ApplicationBuilder().token("7334295147:AAGI0wybEdACz1a7cRE8HGSlInf6aVd4XiM").build()

    # Опитування
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.TEXT & filters.Regex("Опитування"), survey_start)
        ],
        states={
            Q1: [MessageHandler(filters.TEXT & ~filters.COMMAND, survey_q1)],
            Q2: [MessageHandler(filters.TEXT & ~filters.COMMAND, survey_q2)],
            Q3: [MessageHandler(filters.TEXT & ~filters.COMMAND, survey_q3)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)  # оброблення опитування
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
# Виведення роботи бота
    print("ВОНО ЖИВЕ!!!")
    app.run_polling()

if __name__ == "__main__":
    main()
