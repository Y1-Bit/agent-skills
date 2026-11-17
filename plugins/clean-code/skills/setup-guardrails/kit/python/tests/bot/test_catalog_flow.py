"""End-to-end through the real Dispatcher, FSM and middleware.

The bot is a recorder: it never talks to Telegram, it captures what we would send.
"""

import pytest
from aiogram import Bot
from aiogram.methods import SendMessage, TelegramMethod
from aiogram.types import Chat, Message, Update, User

from app.books.infrastructure.in_memory import InMemoryUnitOfWork
from app.entrypoints.bot.app import create_dispatcher
from app.entrypoints.container import Container
from tests.fakes import FIXED_NOW, FixedClock, SequentialIds

USER = User(id=7, is_bot=False, first_name="Y")
CHAT = Chat(id=7, type="private")


class RecordingBot(Bot):
    def __init__(self) -> None:
        super().__init__(token="42:TEST")
        self.sent: list[str] = []

    async def __call__(
        self, method: TelegramMethod[object], request_timeout: int | None = None
    ) -> None:
        if isinstance(method, SendMessage):
            self.sent.append(str(method.text))


class Chatter:
    def __init__(self) -> None:
        self.uow = InMemoryUnitOfWork()
        container = Container(uow=self.uow, ids=SequentialIds(), clock=FixedClock())
        self.dispatcher = create_dispatcher(container)
        self.bot = RecordingBot()
        self._update_id = 0

    async def say(self, text: str) -> str:
        self._update_id += 1
        message = Message(
            message_id=self._update_id, date=FIXED_NOW, chat=CHAT, from_user=USER, text=text
        )
        await self.dispatcher.feed_update(
            self.bot, Update(update_id=self._update_id, message=message)
        )
        return self.bot.sent[-1]


@pytest.fixture
def chat() -> Chatter:
    return Chatter()


async def test_happy_path_catalogs_book(chat: Chatter) -> None:
    assert await chat.say("/catalog") == "Title?"
    assert await chat.say("Dune") == "Country of publication (ISO code, e.g. DE)?"
    assert await chat.say("de") == "ISBN?"
    assert await chat.say("9780441013593") == "Genre (fiction, science, history)?"
    assert await chat.say("science") == "Cataloged ✅ bk_00000001"
    assert chat.uow.commits == 1


async def test_invalid_value_replies_and_stays_on_step(chat: Chatter) -> None:
    await chat.say("/catalog")
    await chat.say("Dune")

    reply = await chat.say("Germany")

    assert reply.startswith("⚠️ CountryCode: must be an ISO 3166-1 alpha-2 code")
    assert await chat.say("DE") == "ISBN?"


async def test_unknown_genre_is_a_domain_error_not_a_crash(chat: Chatter) -> None:
    for text in ("/catalog", "Dune", "DE", "9780441013593"):
        await chat.say(text)

    reply = await chat.say("poetry")

    assert reply == "⚠️ Genre: must be one of: fiction, science, history. Please try again."


async def test_duplicate_book_maps_to_conflict_reply(chat: Chatter) -> None:
    for text in ("/catalog", "Dune", "DE", "9780441013593", "science"):
        await chat.say(text)
    for text in ("/catalog", "Dune", "DE", "9780441013593"):
        await chat.say(text)

    reply = await chat.say("science")

    assert reply == "⛔ ISBN 9780441013593 is already in the catalog"
