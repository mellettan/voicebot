import uvicorn


def main() -> None:
    """Запускает сервис: `python -m voicebot` или `voicebot`."""
    uvicorn.run("voicebot.app:create_app", factory=True, host="0.0.0.0", port=8000, log_config=None)


if __name__ == "__main__":
    main()
