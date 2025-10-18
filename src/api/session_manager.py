"""Менеджер сессий для Chat API."""

import uuid
from datetime import datetime, timedelta
from typing import Final

from .chat_schemas import ChatSession
from ..database import DatabaseClient
from ..logger import get_logger


class SessionManager:
    """Менеджер сессий пользователей для чата."""

    # Константы
    DEFAULT_SESSION_EXPIRE_HOURS: Final[int] = 24
    SESSION_CLEANUP_INTERVAL_HOURS: Final[int] = 1

    def __init__(self, db_client: DatabaseClient, session_expire_hours: int = DEFAULT_SESSION_EXPIRE_HOURS):
        """
        Инициализация менеджера сессий.

        Args:
            db_client: Клиент для работы с БД
            session_expire_hours: Время жизни сессии в часах
        """
        self.db_client = db_client
        self.session_expire_hours = session_expire_hours
        self.logger = get_logger("session_manager")
        
        # Кэш активных сессий (в production лучше использовать Redis)
        self._session_cache: dict[str, ChatSession] = {}

    def generate_session_id(self) -> str:
        """
        Генерировать новый UUID для сессии.

        Returns:
            Строка с UUID сессии
        """
        session_id = str(uuid.uuid4())
        self.logger.debug("Сгенерирован новый session_id", session_id=session_id)
        return session_id

    async def create_session(self, user_id: int | None = None) -> ChatSession:
        """
        Создать новую сессию.

        Args:
            user_id: ID пользователя (если None, создается новый пользователь)

        Returns:
            Информация о созданной сессии
        """
        session_id = self.generate_session_id()
        now = datetime.utcnow()

        # Если user_id не указан, создаем нового пользователя
        if user_id is None:
            # Создаем временного пользователя для веб-чата
            # Используем session_id как telegram_id для уникальности
            user_id = await self._create_web_user(session_id)

        # Создаем сессию
        session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            message_count=0,
        )

        # Сохраняем в кэш
        self._session_cache[session_id] = session

        self.logger.info(
            "Создана новая сессия",
            session_id=session_id,
            user_id=user_id,
        )

        return session

    async def get_session(self, session_id: str) -> ChatSession | None:
        """
        Получить информацию о сессии.

        Args:
            session_id: ID сессии

        Returns:
            Информация о сессии или None если не найдена
        """
        # Проверяем кэш
        if session_id in self._session_cache:
            session = self._session_cache[session_id]
            
            # Проверяем не истекла ли сессия
            if self._is_session_expired(session):
                await self.delete_session(session_id)
                return None
                
            return session

        # Если не в кэше, пытаемся восстановить из БД
        session = await self._restore_session_from_db(session_id)
        if session:
            self._session_cache[session_id] = session

        return session

    async def update_session_activity(self, session_id: str) -> bool:
        """
        Обновить время последней активности сессии.

        Args:
            session_id: ID сессии

        Returns:
            True если сессия обновлена, False если не найдена
        """
        session = await self.get_session(session_id)
        if not session:
            return False

        session.last_activity = datetime.utcnow()
        self._session_cache[session_id] = session

        self.logger.debug("Обновлена активность сессии", session_id=session_id)
        return True

    async def increment_message_count(self, session_id: str) -> bool:
        """
        Увеличить счетчик сообщений в сессии.

        Args:
            session_id: ID сессии

        Returns:
            True если счетчик обновлен, False если сессия не найдена
        """
        session = await self.get_session(session_id)
        if not session:
            return False

        session.message_count += 1
        self._session_cache[session_id] = session

        self.logger.debug(
            "Увеличен счетчик сообщений",
            session_id=session_id,
            message_count=session.message_count,
        )
        return True

    async def delete_session(self, session_id: str) -> bool:
        """
        Удалить сессию.

        Args:
            session_id: ID сессии

        Returns:
            True если сессия удалена, False если не найдена
        """
        if session_id in self._session_cache:
            del self._session_cache[session_id]
            self.logger.info("Сессия удалена из кэша", session_id=session_id)
            return True

        return False

    async def cleanup_expired_sessions(self) -> int:
        """
        Очистить истекшие сессии.

        Returns:
            Количество удаленных сессий
        """
        expired_sessions = []
        now = datetime.utcnow()

        for session_id, session in self._session_cache.items():
            if self._is_session_expired(session):
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            await self.delete_session(session_id)

        self.logger.info(
            "Очищены истекшие сессии",
            expired_count=len(expired_sessions),
        )

        return len(expired_sessions)

    def _is_session_expired(self, session: ChatSession) -> bool:
        """
        Проверить истекла ли сессия.

        Args:
            session: Сессия для проверки

        Returns:
            True если сессия истекла
        """
        if not session.last_activity:
            return True

        expire_time = session.last_activity + timedelta(hours=self.session_expire_hours)
        return datetime.utcnow() > expire_time

    async def _create_web_user(self, session_id: str) -> int:
        """
        Создать пользователя для веб-чата.

        Args:
            session_id: ID сессии (используется как telegram_id)

        Returns:
            ID созданного пользователя
        """
        # Создаем пользователя с уникальным username на основе session_id
        username = f"web_user_{session_id[:8]}"

        # Добавляем пользователя в БД
        user_id, _ = await self.db_client.get_or_create_user(username)

        self.logger.info(
            "Создан пользователь для веб-чата",
            user_id=user_id,
            username=username,
        )

        return user_id

    async def _restore_session_from_db(self, session_id: str) -> ChatSession | None:
        """
        Восстановить сессию из БД (заглушка).

        В реальной реализации здесь должен быть запрос к БД для восстановления сессии.
        Пока возвращаем None, так как сессии хранятся только в памяти.

        Args:
            session_id: ID сессии

        Returns:
            Восстановленная сессия или None
        """
        # TODO: Реализовать восстановление сессии из БД
        # Пока сессии хранятся только в памяти
        self.logger.debug("Попытка восстановления сессии из БД (не реализовано)", session_id=session_id)
        return None

    def get_session_stats(self) -> dict[str, int]:
        """
        Получить статистику по сессиям.

        Returns:
            Словарь со статистикой
        """
        active_sessions = len(self._session_cache)
        expired_sessions = sum(
            1 for session in self._session_cache.values() 
            if self._is_session_expired(session)
        )

        return {
            "active_sessions": active_sessions,
            "expired_sessions": expired_sessions,
            "total_sessions": active_sessions + expired_sessions,
        }
