"""Entrypoint для запуска API сервера."""

import uvicorn

from ..config import Config


def main() -> None:
    """Запуск API сервера с конфигурацией из Config."""
    config = Config()

    uvicorn.run(
        "src.api.app:app",
        host=config.api_host,
        port=config.api_port,
        reload=config.api_reload,
        log_level=config.log_level.lower(),
    )


if __name__ == "__main__":
    main()

