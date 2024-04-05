from funcs.db import create_tables
from init_bot import bot
from handler import register_handlers
import telebot


if __name__ == "__main__":
    create_tables()
    register_handlers()
    print("Бот запущен")
    bot.add_custom_filter(telebot.custom_filters.StateFilter(bot))
    bot.infinity_polling()
    print("Бот остановлен")
