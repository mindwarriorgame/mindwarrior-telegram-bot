import asyncio
import datetime
import os

import telegram
from telegram import Bot, WebAppInfo, Update, \
    InlineKeyboardMarkup, InlineKeyboardButton, Message
from telegram.ext import CommandHandler, Application, MessageHandler, filters, CallbackQueryHandler

from game_manager import GameManager, Reply
from lang_provider import LangProvider
# import pydevd_pycharm
# pydevd_pycharm.settrace('localhost', port=53509, stdoutToServer=True, stderrToServer=True)

TOKEN = os.environ.get('TOKEN')
ENV = os.environ.get('ENV')
FRONTEND_BASE_URL = os.environ.get('FRONTEND_BASE_URL')

bot = Bot(token=TOKEN)

game_manager = GameManager("mindwarrior2.db", ENV, FRONTEND_BASE_URL)

async def process_ticks():
    global game_manager
    replies = game_manager.process_tick()
    for reply in replies:
        await send_reply_with_bot(reply)


async def send_reply(message: Message, ret: Reply):
    if len(ret['message']) > 0:
        if len(ret['buttons']) == 0:
            await message.reply_text(ret['message'], parse_mode='HTML')
        else:
            keyboard = [
                [
                    InlineKeyboardButton(button['text'], web_app=WebAppInfo(url=button['url'])) if button.get('url') is not None else
                    InlineKeyboardButton(button['text'], callback_data=button['data'])
                ] for button in ret['buttons']
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await message.reply_text(ret['message'], parse_mode='HTML', reply_markup=reply_markup)

    if len(ret['menu_commands']) > 0:
        await bot.set_my_commands(
            commands=ret['menu_commands'],
            scope=telegram.BotCommandScopeChat(
                chat_id=message.chat.id
            )
        )

    if 'image' in ret and ret['image'] is not None:
        await message.reply_photo(photo=ret['image'])
        if ret['image'].startswith('tmp_'):
            os.remove(ret['image'])


async def send_reply_with_bot(ret: Reply):
    global bot
    if len(ret['message']) > 0:
        if len(ret['buttons']) == 0:
            await bot.send_message(ret['to_chat_id'], ret['message'], parse_mode='HTML')
        else:
            keyboard = [[InlineKeyboardButton(button['text'], web_app=WebAppInfo(url=button['url']))] for button in ret['buttons']]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await bot.send_message(ret['to_chat_id'], ret['message'], parse_mode='HTML', reply_markup=reply_markup)

    if 'image' in ret and ret['image'] is not None:
        if ret['image'].endswith('.txt'):
            with open(ret['image'], "rb") as file:
                await bot.send_document(ret['to_chat_id'], document=file, filename='user_data.txt')
        else:
            await bot.send_photo(ret['to_chat_id'], photo=ret['image'])

        if ret['image'].startswith('tmp_'):
            os.remove(ret['image'])

def get_message(update: Update):
    return update.message if update.message is not None else update.callback_query.message


async def start_command(update, context):
    global game_manager
    message = get_message(update)
    chat_id = message.chat.id
    ret = game_manager.on_start_command(chat_id)
    await send_reply(message, ret)

async def review_command(update, context):
    global game_manager
    message = get_message(update)
    chat_id = message.chat.id
    ret = game_manager.on_review_command(chat_id)
    await send_reply(message, ret)


async def help_command(update: Update, context):
    global game_manager
    message = get_message(update)
    chat_id = message.chat.id
    ret = game_manager.on_help_command(chat_id)
    await send_reply(message, ret)


async def lang_command(update: Update, context):
    global game_manager
    message = get_message(update)
    chat_id = message.chat.id
    ret = game_manager.on_lang_input(chat_id, update.message.text)
    await send_reply(message, ret)

async def pause_command(update: Update, context):
    global game_manager
    message = get_message(update)
    chat_id = message.chat.id
    ret = game_manager.on_pause_command(chat_id)
    await send_reply(message, ret)

async def sleep_command(update: Update, context):
    global game_manager
    message = get_message(update)
    chat_id = message.chat.id
    ret = game_manager.on_sleep_command(chat_id)
    await send_reply(message, ret)

async def stats_command(update: Update, context):
    global game_manager
    message = get_message(update)
    chat_id = message.chat.id
    ret = game_manager.on_stats_command(chat_id)
    await send_reply(message, ret)

async def formula_command(update: Update, context):
    global game_manager
    message = get_message(update)
    chat_id = message.chat.id
    ret = game_manager.on_formula_command(chat_id)
    await send_reply(message, ret)

async def difficulty_command(update: Update, context):
    global game_manager
    message = get_message(update)
    chat_id = message.chat.id
    ret = game_manager.on_difficulty_command(chat_id)
    await send_reply(message, ret)

async def feedback_command(update: Update, context):
    global game_manager
    message = get_message(update)
    chat_id = message.chat.id
    ret = game_manager.on_feedback_command(chat_id)
    await send_reply(message, ret)


async def settings_command(update: Update, context):
    global game_manager
    message = get_message(update)
    chat_id = message.chat.id
    ret = game_manager.on_settings_command(chat_id)
    await send_reply(message, ret)

async def data_command(update: Update, context):
    global game_manager
    message = get_message(update)
    chat_id = message.chat.id
    rets = game_manager.on_data_command(chat_id)
    for ret in rets:
        await send_reply_with_bot(ret)

async def fallback_command(update: Update, context):
    global game_manager
    message = get_message(update)
    chat_id = message.chat.id
    ret = game_manager.on_data_provided(chat_id, message.text)
    for reply in ret:
        if reply['to_chat_id'] == chat_id:
            await send_reply(message, reply)
        else:
            await send_reply_with_bot(reply)



async def fetch_and_process_updates(app: Application):
    offset = None

    while True:
        updates = await app.bot.get_updates(offset=offset, timeout=10, allowed_updates=["message",
                                                                                    "edited_channel_post", "callback_query", "message_reaction"])  # Fetch updates from Telegram
        if len(updates) > 0:
            print('Received ' + str(len(updates)) + ' updates at ' + str(datetime.datetime.now()))
        for update in updates:
            # print(update)
            await app.process_update(update)
            offset = update.update_id + 1

        await asyncio.sleep(1)
        await process_ticks()

async def button(update: Update, ctx) -> None:
    query = update.callback_query

    await query.answer()

    if query.data == "data":
        await data_command(update, ctx)
    elif query.data == "sleep":
        await sleep_command(update, ctx)
    elif query.data == "difficulty":
        await difficulty_command(update, ctx)
    elif query.data == "feedback":
        await feedback_command(update, ctx)


async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start_command))

    app.add_handler(CommandHandler('review', review_command))
    app.add_handler(CommandHandler('pause', pause_command))
    app.add_handler(CommandHandler('stats', stats_command))
    app.add_handler(CommandHandler('formula', formula_command))
    app.add_handler(CommandHandler('settings', settings_command))

    app.add_handler(CommandHandler('sleep', sleep_command))
    app.add_handler(CommandHandler('data', data_command))
    app.add_handler(CommandHandler('difficulty', difficulty_command))
    app.add_handler(CommandHandler('feedback', feedback_command))

    app.add_handler(CallbackQueryHandler(button))

    for lang_code, lang in LangProvider.get_available_languages().items():
        app.add_handler(CommandHandler(lang_code, lang_command))
    app.add_handler(MessageHandler(filters.TEXT, fallback_command))

    await app.initialize()
    print("Bot is running...")

    await fetch_and_process_updates(app)

asyncio.run(main())
