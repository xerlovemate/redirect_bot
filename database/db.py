from sqlalchemy import BigInteger, String
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

# Создание движка для асинхронного взаимодействия с базой данных SQLite
engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')

# Создание асинхронной сессии для работы с базой данных
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


class Link(Base):
    """Модель пользователя"""
    __tablename__ = 'links'

    id: Mapped[int] = mapped_column(primary_key=True)

    request: Mapped[str] = mapped_column(nullable=False, unique=True)
    redirect_url: Mapped[str] = mapped_column(nullable=False)


# Функция для создания всех таблиц в базе данных
async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
