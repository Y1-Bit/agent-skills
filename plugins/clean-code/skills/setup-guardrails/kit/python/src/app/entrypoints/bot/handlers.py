"""Multi-step cataloging as a DATA-DRIVEN FSM.

Instead of N copy-pasted step handlers (parse → store → set next state → ask),
the flow is a table of `Step`s and one handler factory. Adding a field = adding a row.
Each step parses into a value object, so invalid input raises InvalidValueError,
the middleware replies, and the user stays on the same step.
"""

import itertools
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from app.books.domain.value_objects import (
    BookTitle,
    CountryCode,
    Genre,
    Isbn,
)
from app.entrypoints.bot.forms import message_text, sender_id, to_command
from app.entrypoints.container import Container


class Cataloging(StatesGroup):
    title = State()
    country = State()
    isbn = State()
    genre = State()


@dataclass(frozen=True, slots=True)
class Step:
    state: State
    field: str
    parse: Callable[[str], object]
    prompt: str


STEPS: tuple[Step, ...] = (
    Step(Cataloging.title, "title", BookTitle.parse, "Title?"),
    Step(
        Cataloging.country,
        "country",
        CountryCode.parse,
        "Country of publication (ISO code, e.g. DE)?",
    ),
    Step(
        Cataloging.isbn,
        "isbn",
        Isbn.parse,
        "ISBN?",
    ),
    Step(Cataloging.genre, "genre", Genre.parse, f"Genre ({', '.join(Genre)})?"),
)


async def _start_cataloging(message: Message, state: FSMContext) -> None:
    await state.set_state(STEPS[0].state)
    await message.answer(STEPS[0].prompt)


def _intermediate_step(step: Step, following: Step) -> Callable[..., Awaitable[None]]:
    async def handle(message: Message, state: FSMContext) -> None:
        value = step.parse(message_text(message))
        await state.update_data({step.field: str(value)})
        await state.set_state(following.state)
        await message.answer(following.prompt)

    return handle


async def _final_step(message: Message, *, state: FSMContext, container: Container) -> None:
    last = STEPS[-1]
    value = last.parse(message_text(message))
    data = {**await state.get_data(), last.field: str(value)}
    book_id = await container.catalog_book()(to_command(data, sender_id(message)))
    await state.clear()
    await message.answer(f"Cataloged ✅ {book_id}")


def build_router() -> Router:
    """A factory, not a module-level router: aiogram routers attach to ONE dispatcher."""
    router = Router(name="book-cataloging")
    router.message(Command("catalog"))(_start_cataloging)
    for step, following in itertools.pairwise(STEPS):
        router.message(step.state, F.text)(_intermediate_step(step, following))
    router.message(STEPS[-1].state, F.text)(_final_step)
    return router
