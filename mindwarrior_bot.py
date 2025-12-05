import asyncio
import datetime
import os

import telegram
from telegram import Bot, MaybeInaccessibleMessage, WebAppInfo, Update, \
    InlineKeyboardMarkup, InlineKeyboardButton, Message
from telegram.ext import CommandHandler, Application, MessageHandler, filters, CallbackQueryHandler

from game_manager import SET_SERVER_PREFIX, GameManager, Reply
from lang_provider import LangProvider
from users_orm import UsersOrm, User
# import pydevd_pycharm
# pydevd_pycharm.settrace('localhost', port=53509, stdoutToServer=True, stderrToServer=True)

TOKEN = os.environ.get('TOKEN')
if TOKEN is None:
    raise Exception("No token was provided!")
ENV = os.environ.get('ENV')

bot = Bot(token=TOKEN)

user_orm = UsersOrm("mindwarrior2.db")

async def process_ticks():
    replies = GameManager.process_tick(user_orm, ENV)
    for reply in replies:
        try:
            await send_reply_with_bot(reply)
        except Exception as e:
            if type(e).__name__ == 'Forbidden' and 'bot was blocked by the user' in e.message: # type: ignore
                print('Deleting blocked user')
                user_orm.remove_user(reply['to_chat_id'])


async def send_reply(message: Message, ret: Reply):
    if len(ret['message']) > 0:
        if len(ret['buttons']) == 0:
            await message.reply_text(ret['message'], parse_mode='HTML')
        else:
            keyboard = [
                [
                    InlineKeyboardButton(button['text'], web_app=WebAppInfo(url=button.get('url', 'undefined'))) if button.get('url') is not None else
                    InlineKeyboardButton(button['text'], callback_data=button.get('data', 'undefined'))
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
            keyboard = [
                [
                    InlineKeyboardButton(button['text'], web_app=WebAppInfo(url=button.get('url', 'undefined'))) if button.get('url') is not None else
                    InlineKeyboardButton(button['text'], callback_data=button.get('data', 'undefined'))
                ] for button in ret['buttons']
            ]
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

def get_message(update: Update) -> Message | None:
    if update.message:
        return update.message
    if update.callback_query:
        if isinstance(update.callback_query.message, Message):
            return update.callback_query.message
    return None

def get_user_and_game_manager(chat_id: int):
    user = user_orm.get_user_by_id(chat_id)
    return (user, GameManager(user, ENV))

async def start_command(update, context):
    message = get_message(update)
    if not message:
        return
    chat_id = message.chat.id

    user, game_manager = get_user_and_game_manager(chat_id)
    ret = game_manager.on_start_command()
    user_orm.upsert_user(user)

    await send_reply(message, ret)

async def review_command(update, context):
    message = get_message(update)
    if not message:
        return
    chat_id = message.chat.id

    user, game_manager = get_user_and_game_manager(chat_id)
    ret = game_manager.on_review_command()
    user_orm.upsert_user(user)

    await send_reply(message, ret)


async def lang_command(update: Update, context):
    message = get_message(update)
    if not message:
        return
    if not message.text:
        message.text = "null"
    chat_id = message.chat.id

    user, game_manager = get_user_and_game_manager(chat_id)
    ret = game_manager.on_lang_input(message.text)
    user_orm.upsert_user(user)

    await send_reply(message, ret)

async def pause_command(update: Update, context):
    message = get_message(update)
    if not message:
        return
    chat_id = message.chat.id

    user, game_manager = get_user_and_game_manager(chat_id)
    ret = game_manager.on_pause_command()
    user_orm.upsert_user(user)

    await send_reply(message, ret)

async def sleep_command(update: Update, context):
    message = get_message(update)
    if not message:
        return
    chat_id = message.chat.id

    user, game_manager = get_user_and_game_manager(chat_id)
    ret = game_manager.on_sleep_command()
    user_orm.upsert_user(user)

    await send_reply(message, ret)

async def stats_command(update: Update, context):
    message = get_message(update)
    if not message:
        return
    chat_id = message.chat.id

    user, game_manager = get_user_and_game_manager(chat_id)
    ret = game_manager.on_stats_command()
    user_orm.upsert_user(user)

    await send_reply(message, ret)

async def shop_command(update: Update, context):
    message = get_message(update)
    if not message:
        return
    chat_id = message.chat.id

    user, game_manager = get_user_and_game_manager(chat_id)
    ret = game_manager.on_shop_command()
    user_orm.upsert_user(user)

    await send_reply(message, ret)


async def formula_command(update: Update, context):
    message = get_message(update)
    if not message:
        return
    chat_id = message.chat.id

    user, game_manager = get_user_and_game_manager(chat_id)
    ret = game_manager.on_formula_command()
    user_orm.upsert_user(user)

    await send_reply(message, ret)

async def difficulty_command(update: Update, context):
    message = get_message(update)
    if not message:
        return
    chat_id = message.chat.id

    user, game_manager = get_user_and_game_manager(chat_id)
    ret = game_manager.on_difficulty_command()
    user_orm.upsert_user(user)

    await send_reply(message, ret)

async def feedback_command(update: Update, context):
    message = get_message(update)
    if not message:
        return
    chat_id = message.chat.id

    user, game_manager = get_user_and_game_manager(chat_id)
    ret = game_manager.on_feedback_command()
    user_orm.upsert_user(user)
    
    await send_reply(message, ret)

async def shop_unblock_command(update: Update, context):
    message = get_message(update)
    if not message:
        return
    chat_id = message.chat.id

    user, game_manager = get_user_and_game_manager(chat_id)
    ret = game_manager.on_shop_unblock_command()
    user_orm.upsert_user(user)

    await send_reply(message, ret)

async def shop_progress_command(update: Update, context):
    message = get_message(update)
    if not message:
        return
    chat_id = message.chat.id

    user, game_manager = get_user_and_game_manager(chat_id)
    ret = game_manager.on_shop_progress_command()
    user_orm.upsert_user(user)

    await send_reply(message, ret)

async def change_server_command(update: Update, context):
    message = get_message(update)
    if not message:
        return
    chat_id = message.chat.id

    user, game_manager = get_user_and_game_manager(chat_id)
    ret = game_manager.change_server_command()
    user_orm.upsert_user(user)

    await send_reply(message, ret)

async def settings_command(update: Update, context):
    message = get_message(update)
    if not message:
        return
    chat_id = message.chat.id

    user, game_manager = get_user_and_game_manager(chat_id)
    ret = game_manager.on_settings_command()
    user_orm.upsert_user(user)

    await send_reply(message, ret)

async def data_command(update: Update, context):
    message = get_message(update)
    if not message:
        return
    chat_id = message.chat.id

    user, game_manager = get_user_and_game_manager(chat_id)
    rets = game_manager.on_data_command()
    user_orm.upsert_user(user)

    for ret in rets:
        await send_reply_with_bot(ret)

async def fallback_command(update: Update, context):
    message = get_message(update)
    if not message:
        return
    if not message.text:
        message.text="<null>"
    chat_id = message.chat.id

    user, game_manager = get_user_and_game_manager(chat_id)
    ret = game_manager.on_data_provided(message.text)
    if user['user_id'] == -1:
        user_orm.remove_user(chat_id)
    else:
        user_orm.upsert_user(user)

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
    if not query:
        return
    
    message = get_message(update)
    if not message:
        return
    chat_id = message.chat.id

    await query.answer()

    for lang_code, lang in LangProvider.get_available_languages().items():
        if query.data == lang_code:
            user, game_manager = get_user_and_game_manager(chat_id)
            await send_reply(message, game_manager.on_lang_input(lang_code))
            user_orm.upsert_user(user)
            return
    if not query.data:
        return

    if query.data == "data":
        await data_command(update, ctx)
    elif query.data == "sleep":
        await sleep_command(update, ctx)
    elif query.data == "difficulty":
        await difficulty_command(update, ctx)
    elif query.data == "feedback":
        await feedback_command(update, ctx)
    elif query.data == "shop_unblock":
        await shop_unblock_command(update, ctx)
    elif query.data == "shop_progress":
        await shop_progress_command(update, ctx)
    elif query.data == "change_server":
        await change_server_command(update, ctx)
    elif SET_SERVER_PREFIX in query.data:
        user, game_manager = get_user_and_game_manager(chat_id)
        await send_reply(message, game_manager.on_set_server_command(query.data.split(SET_SERVER_PREFIX)[1]))
        user_orm.upsert_user(user)
        return


async def main():
    if not TOKEN:
        raise BaseException("Cannot run without token")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start_command))

    app.add_handler(CommandHandler('review', review_command))
    app.add_handler(CommandHandler('pause', pause_command))
    app.add_handler(CommandHandler('stats', stats_command))
    app.add_handler(CommandHandler('shop', shop_command))
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
