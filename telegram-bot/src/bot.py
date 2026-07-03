"""Build the bot application, register handlers, and run it."""
from __future__ import annotations

import logging

from telegram import BotCommand, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from . import config
from .data_loader import get_categories
from .handlers import commands
from .handlers.callbacks import on_callback
from .handlers.search import on_text

logger = logging.getLogger(__name__)


async def _post_init(app: Application) -> None:
    """Set the command list shown in the Telegram UI."""
    base = [
        BotCommand("start", "🕌 البداية"),
        BotCommand("menu", "📿 القائمة الرئيسية"),
        BotCommand("search", "🔎 البحث عن دعاء"),
        BotCommand("help", "ℹ️ المساعدة"),
    ]
    cat_cmds = [
        BotCommand(c.command, f"{c.emoji} {c.title}") for c in get_categories()
    ]
    await app.bot.set_my_commands(base + cat_cmds)
    logger.info("Bot commands set.")


async def _on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Error while handling update:", exc_info=context.error)


def build_application() -> Application:
    app = (
        Application.builder()
        .token(config.BOT_TOKEN)
        .post_init(_post_init)
        .build()
    )

    # Core commands
    app.add_handler(CommandHandler("start", commands.start))
    app.add_handler(CommandHandler("help", commands.help_command))
    app.add_handler(CommandHandler("menu", commands.menu_command))
    app.add_handler(CommandHandler("search", commands.search_command))

    # Category commands (e.g. /sabah /masaa ...)
    for category in get_categories():
        app.add_handler(
            CommandHandler(category.command, commands.make_category_command(category.id))
        )

    # Buttons
    app.add_handler(CallbackQueryHandler(on_callback))

    # Free-text search (any non-command text)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))

    app.add_error_handler(_on_error)
    return app


def main() -> None:
    config.configure_logging()
    config.validate()

    app = build_application()
    logger.info("🚀 Bot started... (press Ctrl+C to stop)")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
