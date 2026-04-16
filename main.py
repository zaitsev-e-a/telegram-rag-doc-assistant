from telegram import BotCommand
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

from bot.handlers import (
    document_handler,
    restart_handler,
    start_handler,
    text_message_handler,
)
from core.config import settings


async def post_init(application):
    await application.bot.set_my_commands(
        [
            BotCommand("start", "Запустить бота"),
            BotCommand("restart", "Сбросить контекст и память"),
        ]
    )

    await application.bot.set_my_description(
        "Я — AI-ассистент для анализа документов.\n\n"
        "Загрузи файл (pdf, docx, doc, txt), и я помогу ответить на вопросы по нему.\n"
        "Поддерживается работа с несколькими файлами."
    )

    await application.bot.set_my_short_description(
        "RAG-бот для анализа документов"
    )


def build_application():
    if not settings.TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN не найден в .env")

    app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("restart", restart_handler))
    app.add_handler(MessageHandler(filters.Document.ALL, document_handler))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler)
    )

    app.post_init = post_init

    return app


def main():
    app = build_application()
    app.run_polling()


if __name__ == "__main__":
    main()