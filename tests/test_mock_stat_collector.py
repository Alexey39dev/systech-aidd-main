"""Unit тесты для MockStatCollector."""

import pytest

from src.api.mock_stat_collector import MockStatCollector
from src.api.schemas import StatsResponse


@pytest.fixture
def collector():
    """Фикстура для создания экземпляра MockStatCollector."""
    return MockStatCollector()


class TestMockDataGeneration:
    """Тесты генерации mock данных."""

    def test_users_generation(self, collector):
        """Тест генерации пользователей."""
        # Проверка количества пользователей
        assert 50 <= len(collector._users) <= 70, "Should generate 50-70 users"

        # Проверка структуры данных пользователя
        user = collector._users[0]
        assert "id" in user
        assert "username" in user
        assert "created_at" in user

        # Проверка уникальности ID
        user_ids = [u["id"] for u in collector._users]
        assert len(user_ids) == len(set(user_ids)), "User IDs should be unique"

        # Проверка уникальности usernames
        usernames = [u["username"] for u in collector._users]
        assert len(usernames) == len(set(usernames)), "Usernames should be unique"

    def test_messages_generation(self, collector):
        """Тест генерации сообщений."""
        # Проверка количества сообщений
        assert 1000 <= len(collector._messages) <= 1500, "Should generate 1000-1500 messages"

        # Проверка структуры данных сообщения
        message = collector._messages[0]
        assert "id" in message
        assert "user_id" in message
        assert "role" in message
        assert "content" in message
        assert "length" in message
        assert "created_at" in message

        # Проверка ролей
        roles = [m["role"] for m in collector._messages]
        unique_roles = set(roles)
        assert "user" in unique_roles
        assert "assistant" in unique_roles
        assert "system" in unique_roles

        # Проверка распределения ролей (примерно 40/40/20)
        user_count = roles.count("user")
        assistant_count = roles.count("assistant")
        system_count = roles.count("system")

        total = len(roles)
        # Допускаем отклонение в 10%
        assert 0.30 <= user_count / total <= 0.50, "User messages should be ~40%"
        assert 0.30 <= assistant_count / total <= 0.50, "Assistant messages should be ~40%"
        assert 0.10 <= system_count / total <= 0.30, "System messages should be ~20%"

        # Проверка сортировки по времени
        timestamps = [m["created_at"] for m in collector._messages]
        assert timestamps == sorted(timestamps), "Messages should be sorted by created_at"

    def test_username_generation(self, collector):
        """Тест генерации реалистичных username."""
        usernames = [u["username"] for u in collector._users]

        # Все usernames должны быть непустыми строками
        assert all(isinstance(u, str) and len(u) > 0 for u in usernames)

        # Проверка наличия разных типов username
        has_underscore = any("_" in u for u in usernames)
        has_number = any(any(c.isdigit() for c in u) for u in usernames)

        assert has_underscore, "Should have usernames with underscores"
        assert has_number, "Should have usernames with numbers"


class TestGetStatsDay:
    """Тесты получения статистики за день."""

    @pytest.mark.asyncio
    async def test_get_stats_day(self, collector):
        """Тест получения статистики за день."""
        stats = await collector.get_stats("day")

        # Проверка типа возвращаемого значения
        assert isinstance(stats, StatsResponse)

        # Проверка периода
        assert stats.period == "day"

        # Проверка наличия всех компонентов
        assert len(stats.metrics) == 4
        assert len(stats.timeline) == 24, "Day should have 24 hourly points"
        assert len(stats.recent_dialogs) <= 10
        assert len(stats.top_users) <= 10

    @pytest.mark.asyncio
    async def test_metrics_structure(self, collector):
        """Тест структуры метрик."""
        stats = await collector.get_stats("day")

        # Проверка меток метрик
        labels = [m.label for m in stats.metrics]
        assert "Total Dialogs" in labels
        assert "Active Users" in labels
        assert "Avg Dialog Length" in labels
        assert "Messages Today" in labels

        # Проверка значений метрик
        for metric in stats.metrics:
            assert metric.value is not None
            assert metric.change is not None
            assert metric.trend in ["up", "down", "neutral"]

    @pytest.mark.asyncio
    async def test_timeline_hourly(self, collector):
        """Тест почасовой разбивки timeline для дня."""
        stats = await collector.get_stats("day")

        assert len(stats.timeline) == 24, "Should have 24 hourly points"

        # Проверка структуры точек timeline
        for point in stats.timeline:
            assert point.timestamp is not None
            assert point.value >= 0
            assert "T" in point.timestamp, "Timestamp should be in ISO format"


class TestGetStatsWeek:
    """Тесты получения статистики за неделю."""

    @pytest.mark.asyncio
    async def test_get_stats_week(self, collector):
        """Тест получения статистики за неделю."""
        stats = await collector.get_stats("week")

        assert isinstance(stats, StatsResponse)
        assert stats.period == "week"
        assert len(stats.metrics) == 4
        assert len(stats.timeline) == 7, "Week should have 7 daily points"

    @pytest.mark.asyncio
    async def test_timeline_daily(self, collector):
        """Тест ежедневной разбивки timeline для недели."""
        stats = await collector.get_stats("week")

        assert len(stats.timeline) == 7, "Should have 7 daily points"

        # Проверка значений
        for point in stats.timeline:
            assert point.value >= 0


class TestGetStatsMonth:
    """Тесты получения статистики за месяц."""

    @pytest.mark.asyncio
    async def test_get_stats_month(self, collector):
        """Тест получения статистики за месяц."""
        stats = await collector.get_stats("month")

        assert isinstance(stats, StatsResponse)
        assert stats.period == "month"
        assert len(stats.metrics) == 4
        assert len(stats.timeline) == 30, "Month should have 30 daily points"

    @pytest.mark.asyncio
    async def test_timeline_monthly(self, collector):
        """Тест ежедневной разбивки timeline для месяца."""
        stats = await collector.get_stats("month")

        assert len(stats.timeline) == 30, "Should have 30 daily points"


class TestRecentDialogs:
    """Тесты для списка последних диалогов."""

    @pytest.mark.asyncio
    async def test_recent_dialogs_limit(self, collector):
        """Тест ограничения количества последних диалогов."""
        stats = await collector.get_stats("day")

        assert len(stats.recent_dialogs) <= 10, "Should return max 10 recent dialogs"

    @pytest.mark.asyncio
    async def test_recent_dialogs_structure(self, collector):
        """Тест структуры данных последних диалогов."""
        stats = await collector.get_stats("week")

        for dialog in stats.recent_dialogs:
            assert dialog.user_id > 0
            assert len(dialog.username) > 0
            assert dialog.messages_count >= 0
            assert dialog.last_activity is not None

    @pytest.mark.asyncio
    async def test_recent_dialogs_sorted(self, collector):
        """Тест сортировки диалогов по времени последней активности."""
        stats = await collector.get_stats("month")

        if len(stats.recent_dialogs) > 1:
            # Проверка, что диалоги отсортированы от новых к старым
            timestamps = [d.last_activity for d in stats.recent_dialogs]
            assert timestamps == sorted(timestamps, reverse=True), "Should be sorted newest first"


class TestTopUsers:
    """Тесты для топ пользователей."""

    @pytest.mark.asyncio
    async def test_top_users_limit(self, collector):
        """Тест ограничения количества топ пользователей."""
        stats = await collector.get_stats("day")

        assert len(stats.top_users) <= 10, "Should return max 10 top users"

    @pytest.mark.asyncio
    async def test_top_users_structure(self, collector):
        """Тест структуры данных топ пользователей."""
        stats = await collector.get_stats("week")

        for user in stats.top_users:
            assert user.user_id > 0
            assert len(user.username) > 0
            assert user.messages_count >= 0
            assert user.dialogs_count >= 0

    @pytest.mark.asyncio
    async def test_top_users_sorted(self, collector):
        """Тест сортировки пользователей по количеству сообщений."""
        stats = await collector.get_stats("month")

        if len(stats.top_users) > 1:
            # Проверка, что пользователи отсортированы по убыванию количества сообщений
            message_counts = [u.messages_count for u in stats.top_users]
            assert message_counts == sorted(message_counts, reverse=True), \
                "Should be sorted by message count descending"


class TestErrorHandling:
    """Тесты обработки ошибок."""

    @pytest.mark.asyncio
    async def test_invalid_period(self, collector):
        """Тест обработки некорректного периода."""
        with pytest.raises(ValueError, match="Invalid period"):
            await collector.get_stats("invalid")

    @pytest.mark.asyncio
    async def test_empty_period(self, collector):
        """Тест обработки пустого периода."""
        with pytest.raises(ValueError):
            await collector.get_stats("")

    @pytest.mark.asyncio
    async def test_wrong_type_period(self, collector):
        """Тест обработки неправильного типа периода."""
        with pytest.raises((ValueError, AttributeError)):
            await collector.get_stats(123)  # type: ignore


class TestDataConsistency:
    """Тесты согласованности данных."""

    @pytest.mark.asyncio
    async def test_user_ids_valid(self, collector):
        """Тест валидности ID пользователей."""
        stats = await collector.get_stats("day")

        # Все user_id должны существовать в _users
        user_ids = {u["id"] for u in collector._users}

        for dialog in stats.recent_dialogs:
            assert dialog.user_id in user_ids, f"User ID {dialog.user_id} not found"

        for user in stats.top_users:
            assert user.user_id in user_ids, f"User ID {user.user_id} not found"

    @pytest.mark.asyncio
    async def test_metrics_consistency(self, collector):
        """Тест согласованности метрик."""
        stats = await collector.get_stats("week")

        # Active Users не должно быть больше total пользователей
        active_users_metric = next(m for m in stats.metrics if m.label == "Active Users")
        assert active_users_metric.value <= len(collector._users)

    @pytest.mark.asyncio
    async def test_timeline_values_consistency(self, collector):
        """Тест согласованности значений timeline."""
        stats = await collector.get_stats("month")

        # Все значения должны быть неотрицательными
        for point in stats.timeline:
            assert point.value >= 0, "Timeline values should be non-negative"


class TestDifferentPeriods:
    """Тесты сравнения разных периодов."""

    @pytest.mark.asyncio
    async def test_different_periods_different_data(self, collector):
        """Тест что разные периоды возвращают разные данные."""
        day_stats = await collector.get_stats("day")
        week_stats = await collector.get_stats("week")
        month_stats = await collector.get_stats("month")

        # Разное количество точек в timeline
        assert len(day_stats.timeline) != len(week_stats.timeline)
        assert len(week_stats.timeline) != len(month_stats.timeline)

        # Периоды корректно установлены
        assert day_stats.period == "day"
        assert week_stats.period == "week"
        assert month_stats.period == "month"

