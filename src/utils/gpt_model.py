from typing import List

# List of available GPT models
gpt_models: List[str] = [
    "gpt-4.1",
    "gpt-4.1-turbo",
    "gpt-4.1-mini",
    "gpt-4.1-nano",
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4o-nano"
]

class GPTModels:
    """Access GPT model names as attributes."""
    v41: str = "gpt-4.1"
    v41_turbo: str = "gpt-4.1-turbo"
    v41_mini: str = "gpt-4.1-mini"
    v41_nano: str = "gpt-4.1-nano"
    v4o: str = "gpt-4o"
    o4mini: str = "gpt-4o-mini"
    o4nano: str = "gpt-4o-nano"

gpt_default: str = "gpt-4o"

# Instantiate for easy attribute access
gpt = GPTModels()
