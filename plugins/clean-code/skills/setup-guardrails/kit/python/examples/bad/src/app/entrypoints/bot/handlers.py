"""TYPICAL AGENT OUTPUT — fat aiogram handler. Negative example."""

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

router = Router()


@router.message()
async def got_country(message: Message, state: FSMContext, repo, session):
    try:
        code = message.text.strip().upper()
        if len(code) != 2:
            await message.answer("Country must be 2 letters")
            return
        data = await state.get_data()
        if await repo.exists(data["isbn"]):
            await message.answer("Already in the catalog")
            return
        await repo.add(code, data)
        await session.commit()
    except Exception as e:
        await session.rollback()
        await message.answer(f"Error: {e}")
