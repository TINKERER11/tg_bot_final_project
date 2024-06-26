import time
import random
from datetime import datetime
import telebot
from funcs.db import (prov_admin, delete_question, save_question, save_variants, get_my_statistic, total_statistic,
                      get_questions, get_variants, get_question, update_votes, update_statistic, poisk_quest)
from init_bot import bot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


class UserState(telebot.handler_backends.StatesGroup):
    new_quest = telebot.handler_backends.State()
    num_quest = telebot.handler_backends.State()
    variants = telebot.handler_backends.State()


@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    text = ("/get_question - ответить на вопрос\n"
            "/my_statistic - моя статистика\n"
            "/total_statistic - общая статистика\n"
            "/add_question - добавить вопрос\n"
            "/delete_question - удалить вопрос")
    bot.send_message(message.from_user.id, text=f"Привет, {message.from_user.first_name}!\n"
                                                f"Этот бот создан для <i>прохождения опроса</i>.\n"
                                                f"{text}", parse_mode='HTML')


@bot.message_handler(commands=['add_question'])
def create_quiz(message: telebot.types.Message):
    user_id = str(message.from_user.id)
    if len(prov_admin(user_id)) == 0:
        bot.send_message(message.from_user.id, text="У вас <b>нет доступа к этой команде</b>!\n"
                                                    "Вы <u>не администратор</u>!!!", parse_mode='HTML')
    else:
        bot.send_message(message.from_user.id, text="Введите свой вопрос...", parse_mode='HTML')
        bot.set_state(message.from_user.id, UserState.new_quest, message.chat.id)


@bot.message_handler(state=UserState.new_quest)
def state(message: telebot.types.Message):
    with bot.retrieve_data(message.from_user.id) as data:
        data['new_quest'] = message.text
    new_quest = data['new_quest']
    now_date = datetime.now()
    admin_id = str(message.from_user.id)
    save_question(question_text=new_quest, admin_id=admin_id, date=now_date)
    bot.send_message(message.from_user.id, text="Вопрос добавился!")
    time.sleep(1)
    bot.send_message(message.from_user.id, text="Теперь введите варианты ответов...\n"
                                                "Каждый вариант с новой строчки")
    bot.delete_state(message.from_user.id, message.chat.id)
    bot.set_state(message.from_user.id, UserState.variants, message.chat.id)


@bot.message_handler(state=UserState.variants)
def state_2(message: telebot.types.Message):
    admin_id = str(message.from_user.id)
    with bot.retrieve_data(message.from_user.id) as data:
        data['variants'] = message.text
    variants = data['variants'].split('\n')
    for variant in variants:
        save_variants(variant, admin_id)
    bot.send_message(message.from_user.id, text="Варианты ответов добавлены!")
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(commands=['delete_question'])
def delete_quiz(message: telebot.types.Message):
    user_id = str(message.from_user.id)
    if len(prov_admin(user_id)) == 0:
        bot.send_message(message.from_user.id, text="У вас <b>нет доступа к этой команде</b>!\n"
                                                    "Вы <u>не администратор</u>!!!", parse_mode='HTML')
    else:
        bot.send_message(message.from_user.id, text="Напишите <i>id вопроса</i>, "
                                                    "который хотитие удалить", parse_mode='HTML')
        bot.set_state(message.from_user.id, UserState.num_quest, message.chat.id)


@bot.message_handler(state=UserState.num_quest)
def state_1(message: telebot.types.Message):
    with bot.retrieve_data(message.from_user.id) as data:
        data['num'] = message.text
    if not data['num'].isdigit():
        bot.send_message(message.from_user.id, text="Вы ввели не число!")
        bot.delete_state(message.from_user.id, message.chat.id)
    else:
        num_int = int(data['num'])
        if num_int <= 0 or len(poisk_quest(num_int)) == 0:
            bot.send_message(message.from_user.id, text="Вопроса с таким номером не существует")
            bot.delete_state(message.from_user.id, message.chat.id)
        else:
            delete_question(num_int)
            bot.send_message(message.from_user.id, text=f"Вопрос {num_int} удален")
            bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(commands=['get_question'])
def begin(message: telebot.types.Message):
    user_id = str(message.from_user.id)
    questions = get_questions(user_id)
    if len(questions) == 0:
        bot.send_message(message.from_user.id, text="Вопросов пока нет")
    else:
        rand_question = random.choice(questions)
        question = get_question(rand_question)
        variants = get_variants(rand_question[0])
        text = f"{rand_question[0]}) {question[0]}\n"
        markup = InlineKeyboardMarkup()
        for var in variants:
            markup.add(InlineKeyboardButton(text=f"{var[0]}", callback_data=f"{var[1]}"))
        bot.send_message(message.from_user.id, text=text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def call_b(call: telebot.types.CallbackQuery):
    choice_id = int(call.data)
    update_votes(choice_id)
    update_statistic(choice_id, str(call.from_user.id))
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.from_user.id, text="Ответ учтён!")


@bot.message_handler(commands=['my_statistic'])
def statistic(message: telebot.types.Message):
    user_id = str(message.from_user.id)
    my_stat = get_my_statistic(user_id)
    arr = []
    for x in my_stat:
        arr.append(f"{x[0]}\nВаш ответ — {x[1]}\n\n")
    text = "\n".join(arr)
    if len(text) == 0:
        bot.send_message(message.from_user.id, text="Статистика пустая")
    else:
        bot.send_message(message.from_user.id, text=text)


@bot.message_handler(commands=['total_statistic'])
def statistic_1(message: telebot.types.Message):
    user_id = str(message.from_user.id)
    if len(prov_admin(user_id)) == 0:
        bot.send_message(message.from_user.id, text="У вас <b>нет доступа к этой команде</b>!\n"
                                                    "Вы <u>не администратор</u>!!!", parse_mode='HTML')
    else:
        arr = []
        questions, votes = total_statistic()
        for question in questions:
            arr.append(f"{question[0]}) {question[1]}\n")
            for vote in votes:
                if question[0] == vote[0]:
                    arr.append(f"    {vote[1]} — {vote[2]}\n")
            arr.append("\n")
        text = "".join(arr)
        if text == "":
            bot.send_message(message.from_user.id, text="Статистика пустая")
        else:
            bot.send_message(message.from_user.id, text=text)


@bot.message_handler(state='*')
def state_kon(message: telebot.types.Message):
    text = ("/get_question - ответить на вопрос\n"
            "/my_statistic - моя статистика\n"
            "/total_statistic - общая статистика\n"
            "/add_question - добавить вопрос\n"
            "/delete_question - удалить вопрос")
    bot.send_message(message.from_user.id, text=text)
