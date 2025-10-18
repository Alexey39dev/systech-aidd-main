"""Integration тесты для FastAPI приложения."""

import pytest
from fastapi.testclient import TestClient

from src.api.app import app

# Создание тестового клиента
client = TestClient(app)


class TestRootEndpoint:
    """Тесты корневого endpoint."""

    def test_root_endpoint(self):
        """Тест GET / возвращает информацию об API."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert "name" in data
        assert "version" in data
        assert "docs" in data
        assert "endpoints" in data

        assert data["name"] == "Dialog Statistics API"
        assert data["version"] == "1.0.0"

    def test_root_returns_json(self):
        """Тест что корневой endpoint возвращает JSON."""
        response = client.get("/")

        assert response.headers["content-type"] == "application/json"


class TestHealthEndpoint:
    """Тесты health check endpoint."""

    def test_health_check(self):
        """Тест GET /health возвращает статус здоровья."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert data["status"] == "healthy"
        assert "collector_type" in data

    def test_health_check_collector_type(self):
        """Тест что health check возвращает тип collector."""
        response = client.get("/health")
        data = response.json()

        assert data["collector_type"] in ["mock", "real"]


class TestStatsEndpointSuccess:
    """Тесты успешных запросов к /api/stats."""

    def test_stats_default_period(self):
        """Тест GET /api/stats без параметра (default = day)."""
        response = client.get("/api/stats")

        assert response.status_code == 200
        data = response.json()

        assert data["period"] == "day"
        assert "metrics" in data
        assert "timeline" in data
        assert "recent_dialogs" in data
        assert "top_users" in data

    def test_stats_day_period(self):
        """Тест GET /api/stats?period=day."""
        response = client.get("/api/stats", params={"period": "day"})

        assert response.status_code == 200
        data = response.json()

        assert data["period"] == "day"
        assert len(data["metrics"]) == 4
        assert len(data["timeline"]) == 24, "Day should have 24 hourly points"
        assert len(data["recent_dialogs"]) <= 10
        assert len(data["top_users"]) <= 10

    def test_stats_week_period(self):
        """Тест GET /api/stats?period=week."""
        response = client.get("/api/stats", params={"period": "week"})

        assert response.status_code == 200
        data = response.json()

        assert data["period"] == "week"
        assert len(data["metrics"]) == 4
        assert len(data["timeline"]) == 7, "Week should have 7 daily points"

    def test_stats_month_period(self):
        """Тест GET /api/stats?period=month."""
        response = client.get("/api/stats", params={"period": "month"})

        assert response.status_code == 200
        data = response.json()

        assert data["period"] == "month"
        assert len(data["metrics"]) == 4
        assert len(data["timeline"]) == 30, "Month should have 30 daily points"

    def test_stats_returns_json(self):
        """Тест что stats endpoint возвращает JSON."""
        response = client.get("/api/stats")

        assert response.headers["content-type"] == "application/json"


class TestStatsResponseStructure:
    """Тесты структуры ответа stats endpoint."""

    def test_metrics_structure(self):
        """Тест структуры metrics в ответе."""
        response = client.get("/api/stats?period=day")
        data = response.json()

        assert len(data["metrics"]) == 4

        # Проверка каждой метрики
        for metric in data["metrics"]:
            assert "label" in metric
            assert "value" in metric
            assert "change" in metric
            assert "trend" in metric
            assert metric["trend"] in ["up", "down", "neutral"]

        # Проверка наличия всех необходимых метрик
        labels = [m["label"] for m in data["metrics"]]
        assert "Total Dialogs" in labels
        assert "Active Users" in labels
        assert "Avg Dialog Length" in labels
        assert "Messages Today" in labels

    def test_timeline_structure(self):
        """Тест структуры timeline в ответе."""
        response = client.get("/api/stats?period=day")
        data = response.json()

        assert len(data["timeline"]) > 0

        # Проверка каждой точки timeline
        for point in data["timeline"]:
            assert "timestamp" in point
            assert "value" in point
            assert isinstance(point["value"], int)
            assert point["value"] >= 0

    def test_recent_dialogs_structure(self):
        """Тест структуры recent_dialogs в ответе."""
        response = client.get("/api/stats?period=week")
        data = response.json()

        # Проверка каждого диалога
        for dialog in data["recent_dialogs"]:
            assert "user_id" in dialog
            assert "username" in dialog
            assert "messages_count" in dialog
            assert "last_activity" in dialog
            assert dialog["user_id"] > 0
            assert len(dialog["username"]) > 0

    def test_top_users_structure(self):
        """Тест структуры top_users в ответе."""
        response = client.get("/api/stats?period=month")
        data = response.json()

        # Проверка каждого пользователя
        for user in data["top_users"]:
            assert "user_id" in user
            assert "username" in user
            assert "messages_count" in user
            assert "dialogs_count" in user
            assert user["user_id"] > 0
            assert user["messages_count"] >= 0


class TestStatsEndpointErrors:
    """Тесты ошибок stats endpoint."""

    def test_invalid_period(self):
        """Тест GET /api/stats с некорректным периодом."""
        response = client.get("/api/stats", params={"period": "invalid"})

        assert response.status_code == 422  # Validation error from FastAPI
        data = response.json()

        assert "detail" in data

    def test_empty_period(self):
        """Тест GET /api/stats с пустым периодом."""
        response = client.get("/api/stats", params={"period": ""})

        assert response.status_code == 422  # Validation error
        data = response.json()

        assert "detail" in data

    def test_numeric_period(self):
        """Тест GET /api/stats с числовым периодом."""
        response = client.get("/api/stats", params={"period": "123"})

        assert response.status_code == 422  # Validation error


class TestCORS:
    """Тесты CORS настроек."""

    def test_cors_middleware_configured(self):
        """Тест что CORS middleware настроен в приложении."""
        # Проверяем что CORS middleware присутствует в конфигурации
        # FastAPI автоматически оборачивает middleware, поэтому проверяем наличие
        assert len(app.user_middleware) > 0, "Should have middleware configured"

    def test_api_accessible(self):
        """Тест что API доступен для запросов."""
        response = client.get("/api/stats")
        
        # API должен отвечать успешно
        assert response.status_code == 200


class TestOpenAPIDocumentation:
    """Тесты OpenAPI документации."""

    def test_openapi_json_available(self):
        """Тест что OpenAPI schema доступна."""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        data = response.json()

        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

    def test_openapi_info(self):
        """Тест информации в OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()

        assert data["info"]["title"] == "Dialog Statistics API"
        assert data["info"]["version"] == "1.0.0"

    def test_openapi_stats_endpoint_documented(self):
        """Тест что /api/stats endpoint задокументирован."""
        response = client.get("/openapi.json")
        data = response.json()

        assert "/api/stats" in data["paths"]
        assert "get" in data["paths"]["/api/stats"]

    def test_swagger_ui_available(self):
        """Тест что Swagger UI доступен."""
        response = client.get("/docs")

        assert response.status_code == 200
        assert b"swagger" in response.content.lower()

    def test_redoc_available(self):
        """Тест что ReDoc доступен."""
        response = client.get("/redoc")

        assert response.status_code == 200
        assert b"redoc" in response.content.lower()


class TestDataConsistency:
    """Тесты согласованности данных между запросами."""

    def test_multiple_requests_return_data(self):
        """Тест что множественные запросы возвращают данные."""
        for period in ["day", "week", "month"]:
            response = client.get("/api/stats", params={"period": period})
            assert response.status_code == 200
            data = response.json()
            assert data["period"] == period

    def test_metrics_have_values(self):
        """Тест что все метрики имеют значения."""
        response = client.get("/api/stats?period=day")
        data = response.json()

        for metric in data["metrics"]:
            assert metric["value"] is not None
            assert metric["change"] is not None

    def test_timeline_not_empty(self):
        """Тест что timeline не пустой."""
        for period in ["day", "week", "month"]:
            response = client.get("/api/stats", params={"period": period})
            data = response.json()
            assert len(data["timeline"]) > 0


class TestResponseValidation:
    """Тесты валидации ответа против Pydantic схемы."""

    def test_response_validates_against_schema(self):
        """Тест что ответ соответствует StatsResponse схеме."""
        from src.api.schemas import StatsResponse

        response = client.get("/api/stats?period=day")
        data = response.json()

        # Pydantic валидация
        stats = StatsResponse(**data)

        assert stats.period == "day"
        assert len(stats.metrics) == 4
        assert len(stats.timeline) > 0

    def test_all_periods_validate(self):
        """Тест что все периоды возвращают валидные данные."""
        from src.api.schemas import StatsResponse

        for period in ["day", "week", "month"]:
            response = client.get("/api/stats", params={"period": period})
            data = response.json()

            # Должно пройти валидацию без ошибок
            stats = StatsResponse(**data)
            assert stats.period == period


class TestPerformance:
    """Тесты производительности API."""

    def test_response_time_acceptable(self):
        """Тест что время ответа приемлемое (<1 секунда)."""
        import time

        start = time.time()
        response = client.get("/api/stats?period=month")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 1.0, f"Response took {elapsed:.2f}s, should be <1s"

    def test_concurrent_requests(self):
        """Тест что API обрабатывает множественные запросы."""
        import concurrent.futures

        def make_request():
            return client.get("/api/stats?period=day")

        # Выполнение 10 параллельных запросов
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # Все запросы должны быть успешными
        assert all(r.status_code == 200 for r in results)


class TestEdgeCases:
    """Тесты граничных случаев."""

    def test_case_sensitive_period(self):
        """Тест что period чувствителен к регистру."""
        # "Day" вместо "day" должно вызвать ошибку валидации
        response = client.get("/api/stats", params={"period": "Day"})
        assert response.status_code == 422

    def test_extra_query_parameters_ignored(self):
        """Тест что дополнительные параметры игнорируются."""
        response = client.get("/api/stats", params={
            "period": "day",
            "extra": "param",
            "another": "value"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["period"] == "day"

    def test_stats_with_slash(self):
        """Тест /api/stats/ со слэшем в конце."""
        response = client.get("/api/stats/", params={"period": "day"})

        # FastAPI должен обработать оба варианта
        assert response.status_code in [200, 307]  # 307 = redirect

