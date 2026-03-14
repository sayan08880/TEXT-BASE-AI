from groq import Groq
import time
import sys
import os
import textwrap
import shutil
import datetime

# ────────────────────────────────────────────────
#  CONFIG
# ────────────────────────────────────────────────
API_KEY  = "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"
MODEL    = "llama-3.3-70b-versatile"
client   = Groq(api_key=API_KEY)

MAX_HISTORY = 40   # keep last N messages to avoid token blowout

# ────────────────────────────────────────────────
#  ANSI COLOR / STYLE PALETTE
# ────────────────────────────────────────────────
R          = "\033[0m"
BOLD       = "\033[1m"
DIM        = "\033[2m"
ITALIC     = "\033[3m"
UNDERLINE  = "\033[4m"

FG_WHITE   = "\033[97m"
FG_CYAN    = "\033[38;5;51m"
FG_YELLOW  = "\033[38;5;220m"
FG_MAGENTA = "\033[38;5;213m"
FG_GREEN   = "\033[38;5;120m"
FG_GRAY    = "\033[38;5;244m"
FG_SILVER  = "\033[38;5;252m"
FG_RED     = "\033[38;5;203m"
FG_BLUE    = "\033[38;5;75m"
FG_ORANGE  = "\033[38;5;215m"
FG_PINK    = "\033[38;5;219m"

BG_DARK    = "\033[48;5;234m"
BG_USER    = "\033[48;5;22m"
BG_AI      = "\033[48;5;52m"
BG_STATUS  = "\033[48;5;236m"


# ────────────────────────────────────────────────
#  TERMINAL HELPERS
# ────────────────────────────────────────────────

def term_width():
    return shutil.get_terminal_size((100, 24)).columns


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def hr(char="─", color=FG_GRAY, width=None):
    w = width or term_width()
    print(f"{color}{char * w}{R}")


def center(text, color=FG_WHITE):
    w = term_width()
    # Strip ANSI for length calculation
    import re
    clean = re.sub(r'\033\[[0-9;]*m', '', text)
    padding = max((w - len(clean)) // 2, 0)
    print(f"{color}{' ' * padding}{text}{R}")


def timestamp():
    return datetime.datetime.now().strftime("%H:%M:%S")


def wrap_text(text, indent=6):
    w = max(term_width() - indent - 2, 40)
    lines = text.splitlines()
    wrapped = []
    for line in lines:
        if line.strip() == "":
            wrapped.append("")
        else:
            wrapped.extend(textwrap.wrap(line, width=w) or [""])
    return wrapped


# ────────────────────────────────────────────────
#  TOKEN COUNTER (rough estimate)
# ────────────────────────────────────────────────

def estimate_tokens(text):
    return max(1, len(text) // 4)


total_tokens_used = 0


# ────────────────────────────────────────────────
#  CHAT BUBBLE PRINTERS
# ────────────────────────────────────────────────

def bubble_user(text):
    w         = term_width()
    lines     = wrap_text(text, indent=4)
    ts        = timestamp()
    ts_str    = f"{DIM}{FG_GRAY} {ts} {R}"
    inner_w   = w - 2        # inside the box borders

    print()
    print(f"{FG_CYAN}╭{'─' * (inner_w)}╮{R}")
    # header row: icon + label left, timestamp right
    label     = f" {BOLD}{FG_WHITE}👤  YOU{R}"
    label_vis = "  👤  YOU"
    pad       = inner_w - len(label_vis) - len(ts) - 3
    print(f"{FG_CYAN}│{R}{BG_USER}{label}{BG_USER}{' ' * max(pad, 1)}{DIM}{FG_GRAY}{ts}{R}{BG_USER} {R}{FG_CYAN}│{R}")
    print(f"{FG_CYAN}├{'─' * (inner_w)}┤{R}")
    for line in lines:
        content = f"    {line}"
        vis_len = len(content)
        pad     = max(inner_w - vis_len - 1, 0)
        print(f"{FG_CYAN}│{R} {FG_WHITE}{content}{' ' * pad}{R}{FG_CYAN}│{R}")
    print(f"{FG_CYAN}╰{'─' * (inner_w)}╯{R}")


def bubble_ai_start(turn_num):
    w       = term_width()
    inner_w = w - 2
    ts      = timestamp()
    label   = f" {BOLD}{FG_WHITE}🤖  AI ASSISTANT{R}"
    label_v = "  🤖  AI ASSISTANT"
    model_s = f"{DIM}{FG_GRAY}#{turn_num} · {MODEL[:20]}  {ts}{R}"
    model_v = f"#{turn_num} · {MODEL[:20]}  {ts}"
    pad     = max(inner_w - len(label_v) - len(model_v) - 2, 1)

    print()
    print(f"{FG_YELLOW}╭{'─' * (inner_w)}╮{R}")
    print(f"{FG_YELLOW}│{R}{BG_AI}{label}{BG_AI}{' ' * pad}{model_s}{BG_AI} {R}{FG_YELLOW}│{R}")
    print(f"{FG_YELLOW}├{'─' * (inner_w)}┤{R}")
    print(f"{FG_YELLOW}│{R}  ", end="", flush=True)


def bubble_ai_end(lines):
    w       = term_width()
    inner_w = w - 2
    for line in lines[1:]:
        content = f"    {line}"
        vis_len = len(content)
        pad     = max(inner_w - vis_len - 1, 0)
        print(f"{FG_YELLOW}│{R} {FG_SILVER}{content}{' ' * pad}{R}{FG_YELLOW}│{R}")
    print(f"{FG_YELLOW}╰{'─' * (inner_w)}╯{R}")


# ────────────────────────────────────────────────
#  STATUS BAR  – printed live after every reply
# ────────────────────────────────────────────────

def status_bar(msg_count, token_est):
    """Inline bar printed directly in the chat stream – always current."""
    w       = term_width()
    left    = f"  {FG_GREEN}●{R} {DIM}{FG_SILVER}Connected{R}   {FG_GRAY}msgs:{R} {FG_CYAN}{msg_count}{R}"
    right   = f"{FG_GRAY}tokens~{R}{FG_ORANGE}{token_est}{R}  "
    left_v  = f"  ● Connected   msgs: {msg_count}"
    right_v = f"tokens~{token_est}  "
    gap     = max(w - len(left_v) - len(right_v), 1)
    print(f"{BG_STATUS}{left}{' ' * gap}{right}{R}")


# ────────────────────────────────────────────────
#  THINKING ANIMATION  (improved multi-phase)
# ────────────────────────────────────────────────

SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
PHASES         = [
    (FG_MAGENTA, "Thinking…   "),
    (FG_BLUE,    "Processing… "),
    (FG_YELLOW,  "Composing…  "),
]

def thinking_animation(duration=1.6):
    start    = time.time()
    i        = 0
    phase_i  = 0
    phase_t  = start
    color, label = PHASES[0]
    while time.time() - start < duration:
        # rotate phase label every 0.5s
        if time.time() - phase_t > 0.5:
            phase_i  = (phase_i + 1) % len(PHASES)
            color, label = PHASES[phase_i]
            phase_t  = time.time()
        frame = SPINNER_FRAMES[i % len(SPINNER_FRAMES)]
        sys.stdout.write(f"\r  {color}{BOLD}{frame}{R}  {DIM}{FG_SILVER}{label}{R}")
        sys.stdout.flush()
        time.sleep(0.08)
        i += 1
    sys.stdout.write("\r" + " " * 35 + "\r")
    sys.stdout.flush()


# ────────────────────────────────────────────────
#  STREAMING TYPE EFFECT
# ────────────────────────────────────────────────

def type_effect(text, delay=0.009):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


# ────────────────────────────────────────────────
#  HEADER / FOOTER
# ────────────────────────────────────────────────

def print_header():
    clear_screen()
    print()
    hr("═", FG_MAGENTA)
    center(f"{BOLD}{FG_WHITE}  ✦  AI  CHAT  ✦  ")
    hr("═", FG_MAGENTA)
    print()


def print_farewell():
    print()
    hr("═", FG_MAGENTA)
    center(f"{BOLD}{FG_WHITE}  See you next time!  ")
    center(f"{DIM}{FG_GRAY}  Session ended at {timestamp()}  ")
    hr("═", FG_MAGENTA)
    print()


# ────────────────────────────────────────────────
#  HISTORY PRUNING
# ────────────────────────────────────────────────

def prune_history(messages, max_pairs=MAX_HISTORY // 2):
    system = [m for m in messages if m["role"] == "system"]
    convo  = [m for m in messages if m["role"] != "system"]
    # keep last max_pairs * 2 messages
    if len(convo) > max_pairs * 2:
        convo = convo[-(max_pairs * 2):]
    return system + convo


# ────────────────────────────────────────────────
#  MAIN LOOP
# ────────────────────────────────────────────────

messages     = [{"role": "system", "content": "You are a helpful, knowledgeable, and concise assistant."}]
turn_count   = 0
total_tokens = 0

print_header()

while True:
    try:
        # ── Prompt ────────────────────────────────────────
        print(f"{FG_CYAN}{BOLD}You ›{R} ", end="", flush=True)
        user_input = input("").strip()

        # ── Exit ──────────────────────────────────────────
        if user_input.lower() in ("exit", "quit", "bye", "q", ":q"):
            print_farewell()
            break

        # ── Utility ───────────────────────────────────────
        if user_input.lower() == "clear":
            print_header()
            continue

        if user_input.lower() == "reset":
            messages     = [{"role": "system", "content": "You are a helpful, knowledgeable, and concise assistant."}]
            turn_count   = 0
            total_tokens = 0
            print_header()
            continue

        if not user_input:
            continue

        # ── Echo user bubble ──────────────────────────────
        bubble_user(user_input)
        messages.append({"role": "user", "content": user_input})

        # ── Thinking ──────────────────────────────────────
        thinking_animation()

        # ── API call ──────────────────────────────────────
        messages = prune_history(messages)
        try:
            response  = client.chat.completions.create(
                messages=messages,
                model=MODEL,
                temperature=0.7,
                max_tokens=2048,
            )
            ai_text   = response.choices[0].message.content.strip()

            # Update token tracking
            usage = getattr(response, "usage", None)
            if usage:
                total_tokens += getattr(usage, "total_tokens", 0)
            else:
                total_tokens += estimate_tokens(user_input) + estimate_tokens(ai_text)

        except Exception as e:
            ai_text = f"⚠  Error contacting API: {e}"

        # ── AI bubble ─────────────────────────────────────
        turn_count += 1
        wrapped = wrap_text(ai_text, indent=4) or [""]

        bubble_ai_start(turn_count)
        type_effect(f"{FG_SILVER}{wrapped[0]}{R}", delay=0.009)
        bubble_ai_end(wrapped)

        # ── Refresh status in header next render ──────────
        messages.append({"role": "assistant", "content": ai_text})
        print()
        status_bar(turn_count, total_tokens)
        print()

    except KeyboardInterrupt:
        print_farewell()
        break

    except Exception as e:
        print(f"\n  {FG_RED}{BOLD}Unexpected error:{R} {FG_SILVER}{e}{R}\n")
        time.sleep(1.5)
        continue
