import os

# ===== RESET =====
RESET       = "\033[0m"
RESET_FG    = "\033[39m"
RESET_BG    = "\033[49m"
RESET_STYLE = "\033[22m"

# ===== ESTILOS =====
BOLD      = "\033[1m"
DIM       = "\033[2m"
ITALIC    = "\033[3m"
UNDERLINE = "\033[4m"
BLINK     = "\033[5m"

# ===== TEXTO (FORE) =====
BLACK   = "\033[30m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
MAGENTA = "\033[35m"
CYAN    = "\033[36m"
WHITE   = "\033[37m"

# ===== TEXTO CLARO =====
GRAY         = "\033[90m"
LIGHT_RED    = "\033[91m"
LIGHT_GREEN  = "\033[92m"
LIGHT_YELLOW = "\033[93m"
LIGHT_BLUE   = "\033[94m"
LIGHT_MAGENTA= "\033[95m"
LIGHT_CYAN   = "\033[96m"
LIGHT_WHITE  = "\033[97m"

# ===== FUNDO (BG) =====
BG_BLACK   = "\033[40m"
BG_RED     = "\033[41m"
BG_GREEN   = "\033[42m"
BG_YELLOW  = "\033[43m"
BG_BLUE    = "\033[44m"
BG_MAGENTA = "\033[45m"
BG_CYAN    = "\033[46m"
BG_WHITE   = "\033[47m"

# ===== FUNDO CLARO =====
BG_GRAY         = "\033[100m"
BG_LIGHT_RED    = "\033[101m"
BG_LIGHT_GREEN  = "\033[102m"
BG_LIGHT_YELLOW = "\033[103m"
BG_LIGHT_BLUE   = "\033[104m"
BG_LIGHT_MAGENTA= "\033[105m"
BG_LIGHT_CYAN   = "\033[106m"
BG_LIGHT_WHITE  = "\033[107m"


def clear():
    os.system("cls")

def clear_line():
    """
    Limpa a linha atual no terminal e move o cursor para o início.
    """
    print("\r\033[K", end="", flush=True)

def move_cursor(lines):
    """
    Move o cursor verticalmente.
    - lines > 0 : desce `lines` linhas
    - lines < 0 : sobe `abs(lines)` linhas
    """
    if lines > 0:
        print(f"\033[{lines}B", end="", flush=True)  # desce
    elif lines < 0:
        print(f"\033[{abs(lines)}A", end="", flush=True)  # sobe