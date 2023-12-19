import traceback
from django.utils import timezone

from django.conf import settings
import requests
from django.core.management.base import BaseCommand
from telegram import Bot
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler
from telegram.utils.request import Request
from debug.models import User, Platform, Debug, Asnwering

FIRST, SECOND, FOURTH, THIRD, FIVE, SIX = range(6)
share, get_question, answer, send_answer, take_debug, platform_list, faq, platform, today = range(9)


def split_array(arr, size):
    two_dim_arr = []
    while len(arr) > size:
        part = arr[:size]
        two_dim_arr.append(part)
        arr = arr[size:]
    two_dim_arr.append(arr)
    return two_dim_arr


def log_errors(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:

            error_message = f'Произошла ошибка: {e}'
            print(error_message)
            raise e

    return inner


@log_errors
def start(update: Update, context: CallbackContext):
    name = update.effective_user.first_name
    if not name:
        name = ''
    chat_id = update.effective_chat.id
    username = update.message.chat.username
    if not username:
        username = ''
    p, _ = User.objects.get_or_create(
        iduser=chat_id,
        defaults={
            'username': username,
            'name': name,
        }
    )
    keyboard = [
        [
            InlineKeyboardButton('Platforms', callback_data=str(platform)),

        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        f'{name}\nЭто бот для решение проблем связонные по коду насчет платформ ', reply_markup=reply_markup)
    return FIRST


@log_errors
def platform_list(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    platforms = Platform.objects.all()

    keyboard = []
    for platform in platforms:
        keyboard.append([InlineKeyboardButton(platform.name, callback_data=f'URL---{platform.id}')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(
        text=f'Выбери платформу',
        reply_markup=reply_markup
    )
    return SECOND


@log_errors
def take_debug(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    chat_id = update.effective_chat.id
    user = User.objects.filter(iduser=chat_id).first()
    url = Platform.objects.filter(id=query.data.split('---')[1]).first()
    new_debug = Debug(
        platform=url,
        from_user=user,
    )
    new_debug.save()
    query.edit_message_text(
        text=f'{url.name}\nНапиши проблему',
    )
    return THIRD


@log_errors
def take_debug_text(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user = User.objects.filter(iduser=chat_id).first()
    debug = Debug.objects.filter(from_user=user).last()
    debug.request_text = update.message.text
    debug.save()
    context.bot.sendMessage(chat_id, 'Отправь скрин (как фото)')
    return FOURTH


@log_errors
def take_debug_image(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user = User.objects.filter(iduser=chat_id).first()
    debug = Debug.objects.filter(from_user=user).last()
    file = context.bot.get_file(update.message.photo[0].file_id)
    debug.file = file['file_id']
    debug.save()
    to_sent = debug.platform.user.iduser
    text = f'DEBUG\n' \
           f'по платформе {debug.platform.name}\n\n' \
           f'{debug.request_text}'
    context.bot.sendMessage(to_sent, 'Новый Debug\nчтобы посмотреть нажмите на /debug')
    context.bot.sendMessage(chat_id, "Спасибо запрос успешно создался, ждите ответа")
    return ConversationHandler.END


@log_errors
def debug(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user = User.objects.filter(iduser=chat_id).first()
    if user.is_admin:
        debugs = Debug.objects.filter(is_answered=False, platform__user=user).order_by('-id')
        keyboard_list = []
        for deb in debugs:
            keyboard_list.append(
                InlineKeyboardButton(f'{deb.request_text[:20]} {deb.platform.name}', callback_data=f'Debug---{deb.id}'))
        keyboard = split_array(keyboard_list, 1)
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.sendMessage(
            chat_id,
            text=f'Выберите debug:', reply_markup=reply_markup
        )
        if debugs.count() > 0:
            return FIVE
        else:
            context.bot.sendMessage(
                chat_id,
                text=f'Предложении нет'
            )
            return ConversationHandler.END
    else:
        context.bot.sendMessage(
            chat_id,
            text=f'У вас нету доступа'
        )
        return ConversationHandler.END

@log_errors
def debug_show(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user = User.objects.filter(iduser=chat_id).first()
    query = update.callback_query
    query.answer()
    debug = Debug.objects.filter(id=query.data.split('---')[1]).first()
    answering = Asnwering(
        from_user=debug.platform.user,
        ans_user=user,
        problem=debug,
        active=True
    )
    answering.save()

    context.bot.sendMessage(chat_id, f'__{debug.from_user.name} отправил__')
    context.bot.sendMessage(chat_id, debug.request_text)
    context.bot.send_photo(chat_id, photo=debug.file)
    context.bot.sendMessage(chat_id, "_____Напишите ответ____")
    return SIX


@log_errors
def take_debug_answer(update: Update, context: CallbackContext):
    name = update.effective_user.first_name

    chat_id = update.effective_chat.id
    user = User.objects.filter(iduser=chat_id).first()
    ans = Asnwering.objects.filter(ans_user=user, active=True).first()
    bug = ans.problem
    bug.answer = update.message.text
    bug.is_answered = True
    ans.active = False
    ans.save()
    bug.save()
    context.bot.sendMessage(chat_id, "Отвечено")
    context.bot.sendMessage(bug.from_user.iduser,
                            f'Тебе ответили на вопрос\n{bug.request_text}\n\n{update.message.text}')
    reply_text2 = f'{name}, принято, следующий раз нажмите на /debug'
    context.bot.sendMessage(chat_id, reply_text2)
    return ConversationHandler.END


class Command(BaseCommand):
    start = 'Telegram bot'

    def handle(self, *args, **options):
        request = Request(
            connect_timeout=0.5,
            read_timeout=1.0,

        )
        bot = Bot(
            request=request,
            token=settings.TOKEN

        )
        print(bot.get_me())
        updater = Updater(
            bot=bot,
            use_context=True,
        )
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start),
                          CommandHandler('debug', debug)],
            states={
                FIRST: [
                    CallbackQueryHandler(platform_list, pattern='^' + str(platform) + '$')
                ],
                SECOND: [
                    CallbackQueryHandler(take_debug, pattern='^(.+)---(.+)')
                ],
                THIRD: [
                    MessageHandler(Filters.text, take_debug_text)
                ],
                FOURTH: [
                    MessageHandler(Filters.photo, take_debug_image),

                ],
                FIVE: [
                    CallbackQueryHandler(debug_show, pattern='^(.+)---(.+)')
                ],
                SIX: [
                    MessageHandler(Filters.text, take_debug_answer)
                ],
            },
            fallbacks=[CommandHandler('start', start)],
            per_user=True,
            per_chat=False
        )
        updater.dispatcher.add_handler(CommandHandler('share', share))
        updater.dispatcher.add_handler(conv_handler)
        updater.start_polling()
        updater.idle()
