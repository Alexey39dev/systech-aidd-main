"""FastAPI приложение для статистики диалогов."""

from datetime import datetime

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware

from ..config import Config
from ..database import DatabaseClient
from ..dialog_manager import DialogManager
from ..llm_client import LLMClient
from .chat_schemas import ChatMessageRequest, ChatMessageResponse, ChatHistoryResponse
from .mock_database import MockDatabaseClient
from .mock_stat_collector import MockStatCollector
from .schemas import StatsResponse
from .session_manager import SessionManager
from .stat_collector import StatCollector
from .text_to_sql import TextToSQLProcessor

# Инициализация конфигурации
config = Config()

# Создание FastAPI приложения
app = FastAPI(
    title="Dialog Statistics API",
    description="API для получения статистики диалогов с AI-ассистентом",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Настройка CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Глобальные экземпляры
_stat_collector: StatCollector | None = None
_db_client: DatabaseClient | None = None
_llm_client: LLMClient | None = None
_session_manager: SessionManager | None = None
_text_to_sql_processor: TextToSQLProcessor | None = None


def get_stat_collector() -> StatCollector:
    """
    Dependency для получения экземпляра StatCollector.

    Returns:
        StatCollector: Сборщик статистики (Mock или Real)
    """
    global _stat_collector

    if _stat_collector is None:
        # Инициализация в зависимости от конфигурации
        if config.stat_collector_type == "mock":
            _stat_collector = MockStatCollector()
        else:
            # В будущем здесь будет RealStatCollector
            raise NotImplementedError("Real stat collector not implemented yet")

    return _stat_collector


def get_db_client() -> DatabaseClient | MockDatabaseClient:
    """
    Dependency для получения клиента БД.

    Returns:
        DatabaseClient или MockDatabaseClient: Клиент для работы с БД
    """
    global _db_client

    if _db_client is None:
        # Используем mock-клиент для тестирования без БД
        _db_client = MockDatabaseClient(
            database_url=config.database_url,
            pool_min_size=config.database_pool_min_size,
            pool_max_size=config.database_pool_max_size,
        )

    return _db_client


def get_llm_client() -> LLMClient:
    """
    Dependency для получения LLM клиента.

    Returns:
        LLMClient: Клиент для работы с LLM
    """
    global _llm_client

    if _llm_client is None:
        _llm_client = LLMClient(config)

    return _llm_client


def get_session_manager() -> SessionManager:
    """
    Dependency для получения менеджера сессий.

    Returns:
        SessionManager: Менеджер сессий
    """
    global _session_manager

    if _session_manager is None:
        db_client = get_db_client()
        _session_manager = SessionManager(db_client, config.session_expire_hours)

    return _session_manager


def get_text_to_sql_processor() -> TextToSQLProcessor:
    """
    Dependency для получения text-to-SQL процессора.

    Returns:
        TextToSQLProcessor: Процессор для text-to-SQL
    """
    global _text_to_sql_processor

    if _text_to_sql_processor is None:
        llm_client = get_llm_client()
        db_client = get_db_client()
        _text_to_sql_processor = TextToSQLProcessor(llm_client, db_client)

    return _text_to_sql_processor


@app.get("/")
async def root() -> dict[str, str | dict[str, str]]:
    """
    Корневой endpoint с информацией об API.

    Returns:
        Информация об API
    """
    return {
        "name": "Dialog Statistics API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "stats": "/api/stats?period={day|week|month}",
        },
    }


@app.get("/test")
async def test_endpoint() -> dict[str, str]:
    """
    Простой тестовый endpoint для проверки работы сервера.
    """
    return {"message": "Server is working!", "status": "ok"}


@app.get("/api/stats", response_model=StatsResponse)
async def get_stats(
    period: str = Query(
        "day",
        description="Период для статистики",
        pattern="^(day|week|month)$",
    )
) -> StatsResponse:
    """
    Получить статистику диалогов за указанный период.

    Args:
        period: Период статистики ("day", "week", "month")

    Returns:
        StatsResponse: Полная статистика с метриками, timeline, топами

    Raises:
        HTTPException: 400 если период некорректен
        HTTPException: 500 при ошибке сервера
    """
    try:
        collector = get_stat_collector()
        stats = await collector.get_stats(period)
        return stats
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}",
        )


@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint для мониторинга.

    Returns:
        Статус работоспособности сервиса
    """
    try:
        return {
            "status": "healthy",
            "collector_type": config.stat_collector_type,
            "chat_enabled": str(config.chat_enabled),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "collector_type": "unknown",
            "chat_enabled": "false",
        }


# Chat API endpoints
@app.post("/api/chat/message", response_model=ChatMessageResponse)
async def send_chat_message(
    request: ChatMessageRequest,
    http_request: Request,
) -> ChatMessageResponse:
    """
    Отправить сообщение в чат.

    Args:
        request: Запрос с сообщением
        http_request: HTTP запрос для получения session_id из заголовков

    Returns:
        ChatMessageResponse: Ответ ассистента

    Raises:
        HTTPException: 400 если запрос некорректен
        HTTPException: 500 при ошибке сервера
    """
    if not config.chat_enabled:
        raise HTTPException(status_code=503, detail="Chat API is disabled")

    try:
        # Получаем session_id из заголовков или создаем новый
        session_id = request.session_id or http_request.headers.get("X-Session-ID")
        
        session_manager = get_session_manager()
        llm_client = get_llm_client()
        db_client = get_db_client()

        # Получаем или создаем сессию
        if session_id:
            session = await session_manager.get_session(session_id)
            if not session:
                # Сессия истекла, создаем новую
                session = await session_manager.create_session()
                session_id = session.session_id
        else:
            # Создаем новую сессию
            session = await session_manager.create_session()
            session_id = session.session_id

        # Обновляем активность сессии
        await session_manager.update_session_activity(session_id)

        # Создаем DialogManager для этой сессии
        dialog_manager = DialogManager(db_client, session.user_id, config.max_history)

        # Добавляем сообщение пользователя в историю
        await dialog_manager.add_user_message(request.message)

        # Обрабатываем запрос в зависимости от режима
        if request.mode == "admin" and config.text_to_sql_enabled:
            # Режим администратора с text-to-SQL
            text_to_sql = get_text_to_sql_processor()
            response_text, sql_query, _ = await text_to_sql.process_admin_query(request.message)
            
            # Добавляем ответ ассистента в историю
            await dialog_manager.add_assistant_message(response_text)
            
            # Увеличиваем счетчик сообщений
            await session_manager.increment_message_count(session_id)
            
            return ChatMessageResponse(
                message=response_text,
                mode=request.mode,
                sql_query=sql_query,
                metadata={"session_id": session_id, "user_id": session.user_id},
            )
        else:
            # Обычный режим
            # Получаем историю диалога
            history = await dialog_manager.get_history()
            
            # Получаем ответ от LLM
            response_text = await llm_client.get_response(
                user_message=request.message,
                conversation_history=history[:-1],  # Исключаем последнее сообщение (текущий запрос)
            )
            
            # Добавляем ответ ассистента в историю
            await dialog_manager.add_assistant_message(response_text)
            
            # Увеличиваем счетчик сообщений
            await session_manager.increment_message_count(session_id)
            
            return ChatMessageResponse(
                message=response_text,
                mode=request.mode,
                metadata={"session_id": session_id, "user_id": session.user_id},
            )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}",
        )


@app.get("/api/chat/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str = Query(..., description="ID сессии"),
) -> ChatHistoryResponse:
    """
    Получить историю диалога.

    Args:
        session_id: ID сессии

    Returns:
        ChatHistoryResponse: История диалога

    Raises:
        HTTPException: 404 если сессия не найдена
        HTTPException: 500 при ошибке сервера
    """
    if not config.chat_enabled:
        raise HTTPException(status_code=503, detail="Chat API is disabled")

    try:
        session_manager = get_session_manager()
        db_client = get_db_client()

        # Получаем сессию
        session = await session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Создаем DialogManager для этой сессии
        dialog_manager = DialogManager(db_client, session.user_id, config.max_history)

        # Получаем историю диалога
        history = await dialog_manager.get_history()

        # Конвертируем в формат API
        messages = []
        for msg in history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"],
                "timestamp": datetime.utcnow(),  # TODO: Получать реальное время из БД
                "mode": None,  # TODO: Сохранять режим в БД
            })

        return ChatHistoryResponse(
            messages=messages,
            session_id=session_id,
            total_messages=len(messages),
            last_activity=session.last_activity,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}",
        )


@app.delete("/api/chat/history")
async def clear_chat_history(
    session_id: str = Query(..., description="ID сессии"),
) -> dict[str, str]:
    """
    Очистить историю диалога.

    Args:
        session_id: ID сессии

    Returns:
        dict: Результат операции

    Raises:
        HTTPException: 404 если сессия не найдена
        HTTPException: 500 при ошибке сервера
    """
    if not config.chat_enabled:
        raise HTTPException(status_code=503, detail="Chat API is disabled")

    try:
        session_manager = get_session_manager()
        db_client = get_db_client()

        # Получаем сессию
        session = await session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Создаем DialogManager для этой сессии
        dialog_manager = DialogManager(db_client, session.user_id, config.max_history)

        # Очищаем историю
        await dialog_manager.clear_history()

        return {"message": "Chat history cleared successfully", "session_id": session_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}",
        )

