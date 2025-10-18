"""Mock реализация сборщика статистики с тестовыми данными."""

import random
from datetime import datetime, timedelta
from typing import Any

from .schemas import MetricCard, RecentDialog, StatsResponse, TimelinePoint, TopUser
from .stat_collector import StatCollector


class MockStatCollector(StatCollector):
    """Mock сборщик статистики с генерацией реалистичных тестовых данных."""

    def __init__(self) -> None:
        """Инициализация с генерацией mock данных."""
        self._users: list[dict[str, Any]] = []
        self._messages: list[dict[str, Any]] = []
        self._generate_mock_data()

    def _generate_mock_data(self) -> None:
        """Генерация тестовых данных: пользователи и сообщения."""
        # Генерация пользователей (50-70 штук)
        user_count = random.randint(50, 70)
        usernames = self._generate_usernames(user_count)

        now = datetime.now()
        for user_id in range(1, user_count + 1):
            # Пользователи созданы в течение последних 60 дней
            created_days_ago = random.randint(0, 60)
            created_at = now - timedelta(days=created_days_ago)

            self._users.append(
                {
                    "id": user_id,
                    "username": usernames[user_id - 1],
                    "created_at": created_at,
                }
            )

        # Генерация сообщений (1000-1500 штук)
        message_count = random.randint(1000, 1500)
        roles = ["user", "assistant", "system"]
        role_weights = [0.4, 0.4, 0.2]  # 40% user, 40% assistant, 20% system

        for msg_id in range(1, message_count + 1):
            # Сообщения созданы в течение последних 30 дней
            days_ago = random.randint(0, 30)
            hours = random.randint(0, 23)
            minutes = random.randint(0, 59)
            seconds = random.randint(0, 59)

            created_at = now - timedelta(days=days_ago, hours=hours, minutes=minutes, seconds=seconds)

            # Выбор случайного пользователя
            user = random.choice(self._users)
            role = random.choices(roles, weights=role_weights)[0]

            # Генерация контента разной длины
            content_length = random.randint(10, 500)
            content = self._generate_message_content(role, content_length)

            self._messages.append(
                {
                    "id": msg_id,
                    "user_id": user["id"],
                    "role": role,
                    "content": content,
                    "length": len(content),
                    "created_at": created_at,
                }
            )

        # Сортировка сообщений по времени
        self._messages.sort(key=lambda m: m["created_at"])

    def _generate_usernames(self, count: int) -> list[str]:
        """
        Генерация реалистичных username.

        Args:
            count: Количество username для генерации

        Returns:
            Список уникальных username
        """
        prefixes = [
            "alex", "sam", "chris", "jordan", "taylor", "casey", "morgan", "riley",
            "avery", "quinn", "blake", "drew", "sage", "logan", "kai", "phoenix",
            "rowan", "skyler", "charlie", "jamie", "dev", "code", "tech", "ai",
            "bot", "user", "admin", "power", "super", "mega", "ultra", "pro",
        ]

        suffixes = [
            "master", "genius", "wizard", "ninja", "guru", "expert", "dev",
            "coder", "hacker", "builder", "maker", "creator", "pro", "star",
            "hero", "legend", "champion", "ace", "boss", "king", "queen",
            "wonder", "magic", "swift", "tech", "bot", "ai", "mind",
        ]

        usernames = []
        for i in range(count):
            if i < 30:
                # Первые 30 - комбинации префикс + суффикс
                prefix = random.choice(prefixes)
                suffix = random.choice(suffixes)
                username = f"{prefix}_{suffix}"
            else:
                # Остальные - префикс + число
                prefix = random.choice(prefixes)
                number = random.randint(1, 9999)
                username = f"{prefix}{number}"

            # Проверка уникальности
            while username in usernames:
                number = random.randint(1, 9999)
                username = f"{random.choice(prefixes)}{number}"

            usernames.append(username)

        return usernames

    def _generate_message_content(self, role: str, target_length: int) -> str:
        """
        Генерация контента сообщения.

        Args:
            role: Роль отправителя
            target_length: Целевая длина контента

        Returns:
            Сгенерированный текст сообщения
        """
        templates = {
            "user": [
                "How can I help with ",
                "What is the best way to ",
                "Can you explain ",
                "I need assistance with ",
                "Please help me understand ",
            ],
            "assistant": [
                "I can help you with that. ",
                "Here's what you need to know: ",
                "Let me explain: ",
                "The best approach is to ",
                "I'd be happy to assist. ",
            ],
            "system": [
                "System notification: ",
                "Status update: ",
                "Configuration changed: ",
                "Process completed: ",
                "Alert: ",
            ],
        }

        base = random.choice(templates.get(role, templates["user"]))
        filler = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 10

        content = base + filler
        return content[:target_length]

    async def get_stats(self, period: str) -> StatsResponse:
        """
        Получить статистику за указанный период.

        Args:
            period: Период статистики ("day", "week", "month")

        Returns:
            StatsResponse с полной статистикой

        Raises:
            ValueError: Если период некорректен
        """
        if period not in ["day", "week", "month"]:
            raise ValueError(f"Invalid period: {period}. Must be 'day', 'week', or 'month'")

        now = datetime.now()

        # Определение границ периода
        if period == "day":
            period_start = now - timedelta(days=1)
            prev_period_start = now - timedelta(days=2)
            prev_period_end = now - timedelta(days=1)
        elif period == "week":
            period_start = now - timedelta(days=7)
            prev_period_start = now - timedelta(days=14)
            prev_period_end = now - timedelta(days=7)
        else:  # month
            period_start = now - timedelta(days=30)
            prev_period_start = now - timedelta(days=60)
            prev_period_end = now - timedelta(days=30)

        # Фильтрация сообщений по периоду
        period_messages = [m for m in self._messages if m["created_at"] >= period_start]
        prev_period_messages = [
            m for m in self._messages 
            if prev_period_start <= m["created_at"] < prev_period_end
        ]

        # Расчет метрик
        metrics = self._calculate_metrics(period, period_messages, prev_period_messages)

        # Генерация timeline
        timeline = self._generate_timeline(period, period_messages, period_start, now)

        # Получение последних диалогов
        recent_dialogs = self._get_recent_dialogs(period_messages)

        # Получение топ пользователей
        top_users = self._get_top_users()

        return StatsResponse(
            period=period,
            metrics=metrics,
            timeline=timeline,
            recent_dialogs=recent_dialogs,
            top_users=top_users,
        )

    def _calculate_metrics(
        self,
        period: str,
        current_messages: list[dict[str, Any]],
        prev_messages: list[dict[str, Any]],
    ) -> list[MetricCard]:
        """Расчет метрик с трендами."""
        # Total Dialogs (примерная оценка: количество уникальных пользователей с сообщениями)
        current_users = len(set(m["user_id"] for m in current_messages if m["role"] == "user"))
        prev_users = len(set(m["user_id"] for m in prev_messages if m["role"] == "user"))
        dialogs_change = self._calculate_change(current_users, prev_users)

        # Active Users
        active_users = len(set(m["user_id"] for m in current_messages))
        prev_active_users = len(set(m["user_id"] for m in prev_messages))
        users_change = self._calculate_change(active_users, prev_active_users)

        # Avg Dialog Length (среднее количество сообщений на пользователя)
        avg_length = len(current_messages) / active_users if active_users > 0 else 0
        prev_avg_length = len(prev_messages) / prev_active_users if prev_active_users > 0 else 0
        length_change = self._calculate_change(avg_length, prev_avg_length)

        # Messages Today
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)
        
        messages_today = len([m for m in current_messages if m["created_at"] >= today_start])
        messages_yesterday = len([
            m for m in self._messages 
            if yesterday_start <= m["created_at"] < today_start
        ])
        today_change = self._calculate_change(messages_today, messages_yesterday)

        return [
            MetricCard(
                label="Total Dialogs",
                value=current_users * 2,  # Приблизительная оценка диалогов
                change=dialogs_change["text"],
                trend=dialogs_change["trend"],
            ),
            MetricCard(
                label="Active Users",
                value=active_users,
                change=users_change["text"],
                trend=users_change["trend"],
            ),
            MetricCard(
                label="Avg Dialog Length",
                value=round(avg_length, 1),
                change=length_change["text"],
                trend=length_change["trend"],
            ),
            MetricCard(
                label="Messages Today",
                value=messages_today,
                change=today_change["text"],
                trend=today_change["trend"],
            ),
        ]

    def _calculate_change(self, current: float, previous: float) -> dict[str, Any]:
        """Расчет процентного изменения и тренда."""
        if previous == 0:
            if current > 0:
                return {"text": "+100%", "trend": "up"}
            return {"text": "0%", "trend": "neutral"}

        change_percent = ((current - previous) / previous) * 100

        if abs(change_percent) < 1:
            return {"text": "0%", "trend": "neutral"}

        sign = "+" if change_percent > 0 else ""
        trend = "up" if change_percent > 0 else "down"

        return {"text": f"{sign}{change_percent:.1f}%", "trend": trend}

    def _generate_timeline(
        self,
        period: str,
        messages: list[dict[str, Any]],
        start: datetime,
        end: datetime,
    ) -> list[TimelinePoint]:
        """Генерация данных для timeline графика."""
        timeline: list[TimelinePoint] = []

        if period == "day":
            # Почасовая разбивка (24 точки)
            for hour in range(24):
                hour_start = start.replace(hour=hour, minute=0, second=0, microsecond=0)
                hour_end = hour_start + timedelta(hours=1)

                count = len([
                    m for m in messages
                    if hour_start <= m["created_at"] < hour_end
                ])

                timeline.append(
                    TimelinePoint(
                        timestamp=hour_start.isoformat() + "Z",
                        value=count,
                    )
                )

        elif period == "week":
            # Ежедневная разбивка (7 точек)
            for day in range(7):
                day_start = (start + timedelta(days=day)).replace(hour=0, minute=0, second=0, microsecond=0)
                day_end = day_start + timedelta(days=1)

                count = len([
                    m for m in messages
                    if day_start <= m["created_at"] < day_end
                ])

                timeline.append(
                    TimelinePoint(
                        timestamp=day_start.isoformat() + "Z",
                        value=count,
                    )
                )

        else:  # month
            # Ежедневная разбивка (30 точек)
            for day in range(30):
                day_start = (start + timedelta(days=day)).replace(hour=0, minute=0, second=0, microsecond=0)
                day_end = day_start + timedelta(days=1)

                count = len([
                    m for m in messages
                    if day_start <= m["created_at"] < day_end
                ])

                timeline.append(
                    TimelinePoint(
                        timestamp=day_start.isoformat() + "Z",
                        value=count,
                    )
                )

        return timeline

    def _get_recent_dialogs(self, messages: list[dict[str, Any]]) -> list[RecentDialog]:
        """Получение списка последних диалогов."""
        # Группировка сообщений по пользователям
        user_messages: dict[int, list[dict[str, Any]]] = {}
        for msg in messages:
            if msg["role"] == "user" or msg["role"] == "assistant":
                user_id = msg["user_id"]
                if user_id not in user_messages:
                    user_messages[user_id] = []
                user_messages[user_id].append(msg)

        # Создание списка диалогов
        dialogs = []
        for user_id, msgs in user_messages.items():
            user = next((u for u in self._users if u["id"] == user_id), None)
            if user:
                last_msg = max(msgs, key=lambda m: m["created_at"])
                dialogs.append(
                    RecentDialog(
                        user_id=user_id,
                        username=user["username"],
                        messages_count=len(msgs),
                        last_activity=last_msg["created_at"].isoformat() + "Z",
                    )
                )

        # Сортировка по последней активности и ограничение до 10
        dialogs.sort(key=lambda d: d.last_activity, reverse=True)
        return dialogs[:10]

    def _get_top_users(self) -> list[TopUser]:
        """Получение топ пользователей по активности."""
        # Подсчет статистики по пользователям
        user_stats: dict[int, dict[str, Any]] = {}

        for msg in self._messages:
            user_id = msg["user_id"]
            if user_id not in user_stats:
                user_stats[user_id] = {
                    "messages_count": 0,
                    "dialog_days": set(),
                }

            user_stats[user_id]["messages_count"] += 1
            # Учитываем день как "диалог"
            day = msg["created_at"].date()
            user_stats[user_id]["dialog_days"].add(day)

        # Создание списка топ пользователей
        top_users_list = []
        for user_id, stats in user_stats.items():
            user = next((u for u in self._users if u["id"] == user_id), None)
            if user:
                top_users_list.append(
                    TopUser(
                        user_id=user_id,
                        username=user["username"],
                        messages_count=stats["messages_count"],
                        dialogs_count=len(stats["dialog_days"]),
                    )
                )

        # Сортировка по количеству сообщений и ограничение до 10
        top_users_list.sort(key=lambda u: u.messages_count, reverse=True)
        return top_users_list[:10]

