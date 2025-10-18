"""Text-to-SQL процессор для режима администратора."""

import re
from typing import Any

from ..llm_client import LLMClient
from ..logger import get_logger
from ..database import DatabaseClient


class TextToSQLProcessor:
    """Процессор для преобразования естественного языка в SQL запросы."""

    # Промпт для генерации SQL
    SQL_GENERATION_PROMPT = """You are a SQL expert. Generate PostgreSQL queries based on user questions.

Database schema:
- users (id, telegram_id, username, created_at, updated_at, is_deleted)
- messages (id, role, content, length, user_id, created_at, is_deleted)

Rules:
- Only SELECT queries allowed
- Always include LIMIT clause (max 100 rows)
- Filter out is_deleted = true
- Return valid PostgreSQL syntax
- Use proper JOINs when needed
- Format dates in readable format
- Be specific about time ranges

Question: {question}

Generate only the SQL query, no explanations:"""

    # Промпт для форматирования результатов
    RESULT_FORMATTING_PROMPT = """You are a data analyst. Format SQL query results into a clear, human-readable response.

Original question: {question}
SQL query: {sql_query}
Query results: {results}

Format the results as a clear answer to the user's question. Include:
- Summary of findings
- Key numbers and statistics
- Trends or patterns if visible
- Keep it concise but informative

Response:"""

    def __init__(self, llm_client: LLMClient, db_client: DatabaseClient):
        """
        Инициализация процессора.

        Args:
            llm_client: Клиент для работы с LLM
            db_client: Клиент для работы с БД
        """
        self.llm_client = llm_client
        self.db_client = db_client
        self.logger = get_logger("text_to_sql")

    async def process_admin_query(self, question: str) -> tuple[str, str, list[dict[str, Any]]]:
        """
        Обработать запрос администратора.

        Args:
            question: Вопрос пользователя на естественном языке

        Returns:
            Tuple с (ответ, sql_query, результаты)
        """
        try:
            # 1. Генерируем SQL запрос
            sql_query = await self.generate_sql(question)
            self.logger.info("SQL запрос сгенерирован", sql_query=sql_query)

            # 2. Выполняем SQL запрос
            results = await self.execute_sql(sql_query)
            self.logger.info("SQL запрос выполнен", results_count=len(results))

            # 3. Форматируем результаты
            formatted_response = await self.format_results(question, sql_query, results)
            self.logger.info("Результаты отформатированы", response_length=len(formatted_response))

            return formatted_response, sql_query, results

        except Exception as e:
            self.logger.error("Ошибка обработки admin запроса", error=str(e), question=question)
            raise

    async def generate_sql(self, question: str) -> str:
        """
        Генерировать SQL запрос из вопроса.

        Args:
            question: Вопрос на естественном языке

        Returns:
            SQL запрос

        Raises:
            ValueError: Если сгенерированный SQL невалиден
        """
        # Формируем промпт
        prompt = self.SQL_GENERATION_PROMPT.format(question=question)

        try:
            # Получаем ответ от LLM
            response = await self.llm_client.get_response(
                user_message=prompt,
                system_prompt="You are a SQL expert. Generate only valid PostgreSQL queries.",
            )

            # Извлекаем SQL из ответа
            sql_query = self._extract_sql_from_response(response)

            # Валидируем SQL
            self._validate_sql(sql_query)

            self.logger.debug("SQL запрос сгенерирован", sql_query=sql_query)
            return sql_query

        except Exception as e:
            self.logger.error("Ошибка генерации SQL", error=str(e), question=question)
            raise ValueError(f"Не удалось сгенерировать SQL запрос: {str(e)}")

    async def execute_sql(self, sql_query: str) -> list[dict[str, Any]]:
        """
        Выполнить SQL запрос.

        Args:
            sql_query: SQL запрос для выполнения

        Returns:
            Результаты запроса

        Raises:
            ValueError: Если запрос невалиден или выполнение не удалось
        """
        try:
            # Выполняем запрос через БД клиент
            results = await self.db_client.execute_raw_query(sql_query)
            
            self.logger.debug("SQL запрос выполнен", results_count=len(results))
            return results

        except Exception as e:
            self.logger.error("Ошибка выполнения SQL", error=str(e), sql_query=sql_query)
            raise ValueError(f"Не удалось выполнить SQL запрос: {str(e)}")

    async def format_results(self, question: str, sql_query: str, results: list[dict[str, Any]]) -> str:
        """
        Форматировать результаты SQL в человекочитаемый ответ.

        Args:
            question: Исходный вопрос пользователя
            sql_query: Выполненный SQL запрос
            results: Результаты запроса

        Returns:
            Отформатированный ответ
        """
        # Подготавливаем данные для промпта
        results_str = self._format_results_for_prompt(results)

        # Формируем промпт
        prompt = self.RESULT_FORMATTING_PROMPT.format(
            question=question,
            sql_query=sql_query,
            results=results_str,
        )

        try:
            # Получаем отформатированный ответ
            response = await self.llm_client.get_response(
                user_message=prompt,
                system_prompt="You are a data analyst. Format query results clearly and concisely.",
            )

            self.logger.debug("Результаты отформатированы", response_length=len(response))
            return response

        except Exception as e:
            self.logger.error("Ошибка форматирования результатов", error=str(e))
            # Fallback: простое форматирование
            return self._simple_format_results(question, results)

    def _extract_sql_from_response(self, response: str) -> str:
        """
        Извлечь SQL запрос из ответа LLM.

        Args:
            response: Ответ от LLM

        Returns:
            SQL запрос

        Raises:
            ValueError: Если SQL не найден в ответе
        """
        # Ищем SQL запрос в ответе
        # Убираем markdown блоки если есть
        sql_match = re.search(r'```(?:sql)?\s*(.*?)\s*```', response, re.DOTALL | re.IGNORECASE)
        if sql_match:
            return sql_match.group(1).strip()

        # Если нет markdown блоков, ищем SELECT
        select_match = re.search(r'(SELECT\s+.*?)(?:\n\n|\Z)', response, re.DOTALL | re.IGNORECASE)
        if select_match:
            return select_match.group(1).strip()

        # Если ничего не найдено, возвращаем весь ответ
        return response.strip()

    def _validate_sql(self, sql_query: str) -> None:
        """
        Валидировать SQL запрос.

        Args:
            sql_query: SQL запрос для валидации

        Raises:
            ValueError: Если запрос невалиден
        """
        sql_upper = sql_query.upper().strip()

        # Проверяем что это SELECT запрос
        if not sql_upper.startswith('SELECT'):
            raise ValueError("Разрешены только SELECT запросы")

        # Запрещенные операции
        forbidden_operations = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
        for operation in forbidden_operations:
            if operation in sql_upper:
                raise ValueError(f"Операция {operation} запрещена")

        # Проверяем наличие LIMIT
        if 'LIMIT' not in sql_upper:
            raise ValueError("Все запросы должны содержать LIMIT")

        # Проверяем максимальный LIMIT
        limit_match = re.search(r'LIMIT\s+(\d+)', sql_upper)
        if limit_match:
            limit_value = int(limit_match.group(1))
            if limit_value > 100:
                raise ValueError("LIMIT не может быть больше 100")

    def _format_results_for_prompt(self, results: list[dict[str, Any]]) -> str:
        """
        Форматировать результаты для промпта.

        Args:
            results: Результаты SQL запроса

        Returns:
            Отформатированная строка
        """
        if not results:
            return "Нет данных"

        # Берем первые 10 результатов для промпта
        limited_results = results[:10]
        
        formatted_lines = []
        for i, row in enumerate(limited_results, 1):
            row_str = f"Row {i}: " + ", ".join(f"{k}={v}" for k, v in row.items())
            formatted_lines.append(row_str)

        result = "\n".join(formatted_lines)
        
        if len(results) > 10:
            result += f"\n... и еще {len(results) - 10} строк"

        return result

    def _simple_format_results(self, question: str, results: list[dict[str, Any]]) -> str:
        """
        Простое форматирование результатов (fallback).

        Args:
            question: Исходный вопрос
            results: Результаты запроса

        Returns:
            Просто отформатированный ответ
        """
        if not results:
            return "По вашему запросу данных не найдено."

        count = len(results)
        if count == 1:
            return f"Найдена 1 запись:\n{results[0]}"
        else:
            return f"Найдено {count} записей. Первые результаты:\n{results[:3]}"
