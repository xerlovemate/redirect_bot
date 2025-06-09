from aiogram import Router, Bot, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from sqlalchemy import select, delete

import config
from database.db import async_session, Link

router = Router()
router.message.filter(F.chat.type == 'private')
API_TOKEN = config.TOKEN

bot = Bot(token=API_TOKEN)


async def get_all_links():
    async with async_session() as session:
        result = await session.execute(select(Link))
        links = result.scalars().all()
        return links


@router.message(CommandStart())
async def cmd_start(message: Message):
    if str(message.from_user.id) not in config.ADMIN_ID:
        return
    links = await get_all_links()

    if links:
        text = "Редиректы:\n\n"
        for link in links:
            text += f"<b>{link.id}. /{link.request} -> {link.redirect_url}</b>\n"
    else:
        text = "Нет доступных редиректов."

    await message.answer(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)


@router.message(Command("add"))
async def cmd_add(message: Message):
    if str(message.from_user.id) not in config.ADMIN_ID:
        return
    command_text = message.text.strip().lower()

    if "|" not in command_text:
        await message.answer("Неверный формат. Используй: /add {request}|{redirect_url}")
        return

    request, redirect_url = command_text[5:].split("|", 1)

    if not request or not redirect_url:
        await message.answer("Укажи и request, и redirect_url.")
        return

    # Добавляем данные в базу
    async with async_session() as session:
        async with session.begin():
            new_link = Link(request=request, redirect_url=redirect_url)

            session.add(new_link)

        await session.commit()

    await message.answer(f"Редирект добавлен: /{request} -> {redirect_url}", parse_mode=ParseMode.HTML)


@router.message(Command("delete"))
async def cmd_delete(message: Message):
    if str(message.from_user.id) not in config.ADMIN_ID:
        return
    command_text = message.text.strip().lower()

    if len(command_text.split()) < 2:
        await message.answer("Неверный формат. Используй: /delete {id}")
        return

    try:
        redirect_id = int(command_text.split()[1])
    except ValueError:
        await message.answer("Неверный формат ID. Убедись, что это число.")
        return

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(Link).filter(Link.id == redirect_id))
            link = result.scalars().first()

            if link:
                await session.execute(delete(Link).where(Link.id == redirect_id))
                await session.commit()
                await message.answer(f"Редирект с ID {redirect_id} удален.", parse_mode=ParseMode.HTML)
            else:
                await message.answer(f"Редирект с ID {redirect_id} не найден.", parse_mode=ParseMode.HTML)