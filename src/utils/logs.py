from src.conf.settings import DEBUG


def debug_log(message: str) -> None:
    """
    Logs a debug message to the console.
    
    Args:
        message (str): The message to log.
    """
    if DEBUG:
        print(f"➡️ 🐞 DEBUG: {message}")