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

# Instantiate for easy attribute access
gpt = GPTModels()

gpt_dmodel: str = gpt.o4mini

gpt_dtemp: float = 0.7 # Creative of response, from 0.0 to 1.0; 0.0 is deterministic - 1.0 is creative

gpt_max_token: int = 728 # Token is a pieces of response; about 5 characters of a word is equal 1 token
gpt_max_retrieve: int = 10 # Token is a pieces of response; about 5 characters of a word is equal 1 token
