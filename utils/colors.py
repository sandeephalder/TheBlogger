"""
Utility module for colorized console output using standard ANSI escape codes.
"""

# ANSI Color Codes
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

# Colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"

def print_cyan(text: str, *args, **kwargs):
    """Prints bold cyan text to console."""
    print(f"{CYAN}{BOLD}{text}{RESET}", *args, **kwargs)

def print_green(text: str, *args, **kwargs):
    """Prints bold green text to console."""
    print(f"{GREEN}{BOLD}{text}{RESET}", *args, **kwargs)

def print_yellow(text: str, *args, **kwargs):
    """Prints bold yellow text to console."""
    print(f"{YELLOW}{BOLD}{text}{RESET}", *args, **kwargs)

def print_red(text: str, *args, **kwargs):
    """Prints bold red text to console."""
    print(f"{RED}{BOLD}{text}{RESET}", *args, **kwargs)

def print_magenta(text: str, *args, **kwargs):
    """Prints bold magenta text to console."""
    print(f"{MAGENTA}{BOLD}{text}{RESET}", *args, **kwargs)

def print_blue(text: str, *args, **kwargs):
    """Prints bold blue text to console."""
    print(f"{BLUE}{BOLD}{text}{RESET}", *args, **kwargs)

def colorize(text: str, color_code: str) -> str:
    """Wraps text in ANSI color code."""
    return f"{color_code}{text}{RESET}"
