"""
ClickUp Interactive Subtask Creator
=====================================
Script interaktif untuk membuat subtask di ClickUp.

Cara pakai:
  - Klik 2x file clickup_interactive.bat
  - Atau jalankan: python clickup_interactive.py

Alur:
  1. Paste link ClickUp task (parent) → ID otomatis ter-extract
  2. Pilih file CSV lewat popup Windows Explorer
  3. Script membuat subtask secara otomatis

Catatan:
  - API Token disimpan di file .env (sekali setup)
  - File CSV auto-detect format (Simple / Template Test Case QA)
"""

import csv
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

# ── File konfigurasi token ──────────────────────────────────
ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
BASE_URL = "https://api.clickup.com/api/v2"
MAX_RETRIES = 3
RETRY_DELAY_SEC = 2


# ── Warna terminal ──────────────────────────────────────────
class Color:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def log_success(msg):
    print(f"{Color.GREEN}✔ {msg}{Color.RESET}")


def log_error(msg):
    print(f"{Color.RED}✖ {msg}{Color.RESET}")


def log_info(msg):
    print(f"{Color.CYAN}ℹ {msg}{Color.RESET}")


def log_warn(msg):
    print(f"{Color.YELLOW}⚠ {msg}{Color.RESET}")


# ── Token management ────────────────────────────────────────
def load_token():
    """Baca API token dari file .env"""
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("CLICKUP_API_TOKEN="):
                    token = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if token:
                        return token
    return None


def save_token(token):
    """Simpan API token ke file .env"""
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.write(f'CLICKUP_API_TOKEN="{token}"\n')
    log_success(f"Token disimpan ke: {ENV_FILE}")


def get_or_ask_token():
    """Ambil token dari .env atau minta input user."""
    token = load_token()
    if token:
        masked = token[:8] + "..." + token[-4:]
        log_info(f"Token ditemukan: {masked}")
        return token

    print()
    log_warn("API Token belum tersimpan.")
    log_info("Dapatkan token di: https://app.clickup.com/settings/apps")
    print()
    token = input(f"{Color.CYAN}Paste API Token: {Color.RESET}").strip()

    if not token:
        log_error("Token tidak boleh kosong.")
        sys.exit(1)

    save_token(token)
    return token


# ── URL parser ───────────────────────────────────────────────
def extract_task_id(url_or_id):
    """
    Extract task ID dari URL ClickUp atau string ID langsung.

    Mendukung format:
      - https://app.clickup.com/t/90181489899/z8xmdvgw4r
      - https://app.clickup.com/t/z8xmdvgw4r
      - z8xmdvgw4r (langsung ID)
    """
    url_or_id = url_or_id.strip()

    # Pattern: .../t/xxxxx/task_id atau .../t/task_id
    match = re.search(r'/t/(?:\d+/)?([a-zA-Z0-9]+)/?$', url_or_id)
    if match:
        return match.group(1)

    # Jika bukan URL, anggap langsung task ID
    if re.match(r'^[a-zA-Z0-9]+$', url_or_id):
        return url_or_id

    return None


# ── File picker ──────────────────────────────────────────────
def pick_csv_file():
    """Buka dialog Windows Explorer untuk memilih file CSV."""
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    file_path = filedialog.askopenfilename(
        title="Pilih File CSV Test Case",
        filetypes=[
            ("CSV files", "*.csv"),
            ("All files", "*.*"),
        ],
        initialdir=os.path.expanduser("~\\Downloads"),
    )

    root.destroy()
    return file_path


# ── API Call ─────────────────────────────────────────────────
def clickup_request(api_token, method, path, data=None):
    """Kirim HTTP request ke ClickUp API."""
    url = f"{BASE_URL}{path}"
    headers = {
        "Authorization": api_token,
        "Content-Type": "application/json",
    }

    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as resp:
            response_body = resp.read().decode("utf-8")
            return resp.status, json.loads(response_body)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        try:
            error_json = json.loads(error_body)
        except json.JSONDecodeError:
            error_json = {"err": error_body}
        return e.code, error_json
    except urllib.error.URLError as e:
        return 0, {"err": str(e.reason)}


def get_task_info(api_token, task_id):
    """Ambil info task dari ClickUp API."""
    status_code, response = clickup_request(api_token, "GET", f"/task/{task_id}")
    if status_code == 200:
        return response
    else:
        err_msg = response.get("err", "Unknown error")
        log_error(f"Gagal mengambil info task '{task_id}' (HTTP {status_code}): {err_msg}")
        return None


def create_subtask(api_token, list_id, parent_task_id, name, description="", status="to do", time_estimate=0):
    """Buat satu subtask di ClickUp."""
    payload = {
        "name": name,
        "description": description,
        "status": status,
        "parent": parent_task_id,
    }

    if time_estimate and time_estimate > 0:
        payload["time_estimate"] = int(time_estimate * 60 * 1000)

    for attempt in range(1, MAX_RETRIES + 1):
        status_code, response = clickup_request(
            api_token, "POST", f"/list/{list_id}/task", payload
        )

        if status_code == 200:
            task_id = response.get("id", "N/A")
            task_url = response.get("url", "")
            log_success(f"Subtask dibuat: \"{name}\"  →  ID: {task_id}")
            log_info(f"  URL: {task_url}")
            return {
                "task_id": task_id,
                "name": name,
                "url": task_url,
                "status_code": status_code,
            }

        if status_code == 429:
            wait = RETRY_DELAY_SEC * attempt
            log_warn(f"Rate limited. Retry {attempt}/{MAX_RETRIES} dalam {wait}s...")
            time.sleep(wait)
            continue

        err_msg = response.get("err", response.get("ECODE", "Unknown error"))
        log_error(f"Gagal membuat subtask \"{name}\" (HTTP {status_code}): {err_msg}")

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY_SEC)
        else:
            return None

    return None


# ── CSV parsing ──────────────────────────────────────────────
TEMPLATE_COLS = {
    "test_case_id": "Test Case ID",
    "requirement": "Requirement",
    "scenario_type": "Scenario Type",
    "test_scenario": "Test Scenario",
    "test_step": "Test Step",
    "when_action": "When (Action)",
    "then_expected": "Then (Expected Result)",
    "time_estimate": "time estimate",
}


def detect_csv_format(fieldnames):
    """Deteksi format CSV: 'template' atau 'simple'."""
    if not fieldnames:
        return "simple"
    cols_lower = [c.strip().lower() for c in fieldnames if c]
    if "test case id" in cols_lower and "test scenario" in cols_lower:
        return "template"
    return "simple"


def parse_row_template(row):
    """Parse baris CSV format template test case QA."""
    tc_id = row.get(TEMPLATE_COLS["test_case_id"], "").strip()
    requirement = row.get(TEMPLATE_COLS["requirement"], "").strip()
    scenario_type = row.get(TEMPLATE_COLS["scenario_type"], "").strip()
    test_scenario = row.get(TEMPLATE_COLS["test_scenario"], "").strip()
    test_step = row.get(TEMPLATE_COLS["test_step"], "").strip()
    when_action = row.get(TEMPLATE_COLS["when_action"], "").strip()
    then_expected = row.get(TEMPLATE_COLS["then_expected"], "").strip()

    name_parts = [p for p in [tc_id, test_scenario] if p]
    name = " - ".join(name_parts) if name_parts else ""

    desc_lines = []
    if requirement:
        desc_lines.append(f"📋 Requirement: {requirement}")
    if scenario_type:
        desc_lines.append(f"🏷️ Scenario Type: {scenario_type}")
    if test_step:
        desc_lines.append(f"📝 Test Step: {test_step}")
    if when_action:
        desc_lines.append(f"▶️ When (Action): {when_action}")
    if then_expected:
        desc_lines.append(f"✅ Then (Expected Result): {then_expected}")
    description = "\n".join(desc_lines)

    status = "to do"

    raw_te = row.get(TEMPLATE_COLS["time_estimate"], "0")
    raw_te = raw_te.strip() if raw_te else "0"

    return name, description, status, raw_te


def parse_row_simple(row):
    """Parse baris CSV format simple."""
    name = row.get("name", "").strip()
    description = row.get("description", "").strip()
    status = row.get("status", "to do").strip()
    raw_te = row.get("time_estimate", "0")
    raw_te = raw_te.strip() if raw_te else "0"
    return name, description, status, raw_te


# ── Main ─────────────────────────────────────────────────────
def main():
    os.system("cls" if os.name == "nt" else "clear")

    print(f"{Color.BOLD}{Color.CYAN}")
    print("╔══════════════════════════════════════════════════════╗")
    print("║     ClickUp Interactive Subtask Creator              ║")
    print("║     Buat subtask dari CSV ke ClickUp                 ║")
    print("╚══════════════════════════════════════════════════════╝")
    print(f"{Color.RESET}")

    # ── Step 1: API Token ──
    print(f"{Color.BOLD}[Step 1/3] API Token{Color.RESET}")
    api_token = get_or_ask_token()
    print()

    # ── Step 2: Paste URL ClickUp ──
    print(f"{Color.BOLD}[Step 2/3] Parent Task{Color.RESET}")
    log_info("Paste link task ClickUp (atau ketik task ID langsung)")
    log_info("Contoh: https://app.clickup.com/t/90181489899/z8xmdvgw4r")
    print()
    url_input = input(f"{Color.CYAN}Link/ID task: {Color.RESET}").strip()

    if not url_input:
        log_error("Input tidak boleh kosong.")
        input("\nTekan Enter untuk keluar...")
        sys.exit(1)

    parent_task_id = extract_task_id(url_input)
    if not parent_task_id:
        log_error(f"Tidak bisa extract task ID dari: {url_input}")
        input("\nTekan Enter untuk keluar...")
        sys.exit(1)

    log_info(f"Task ID: {parent_task_id}")

    # Ambil info parent task
    log_info("Mengambil info task...")
    task_info = get_task_info(api_token, parent_task_id)
    if not task_info:
        log_error("Gagal mengambil info task. Periksa URL dan API Token.")
        input("\nTekan Enter untuk keluar...")
        sys.exit(1)

    task_name = task_info.get("name", "Unknown")
    list_info = task_info.get("list", {})
    list_id = list_info.get("id", "")
    list_name = list_info.get("name", "Unknown")

    if not list_id:
        log_error("List ID tidak ditemukan di parent task.")
        input("\nTekan Enter untuk keluar...")
        sys.exit(1)

    log_success(f"Parent task : {task_name}")
    log_success(f"List        : {list_name} (ID: {list_id})")
    print()

    # ── Step 3: Pilih file CSV ──
    print(f"{Color.BOLD}[Step 3/3] Pilih File CSV{Color.RESET}")
    log_info("Membuka file picker...")
    csv_path = pick_csv_file()

    if not csv_path:
        log_error("Tidak ada file yang dipilih.")
        input("\nTekan Enter untuk keluar...")
        sys.exit(1)

    log_success(f"File: {csv_path}")
    print()

    # ── Baca CSV ──
    try:
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            sample = f.read(4096)
            f.seek(0)
            delimiter = ","
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
                delimiter = dialect.delimiter
            except Exception:
                first_line = sample.splitlines()[0] if sample else ""
                if first_line.count(";") > first_line.count(","):
                    delimiter = ";"
            reader = csv.DictReader(f, delimiter=delimiter)
            fieldnames = reader.fieldnames
            csv_format = detect_csv_format(fieldnames)
            rows = list(reader)
    except FileNotFoundError:
        log_error(f"File tidak ditemukan: {csv_path}")
        input("\nTekan Enter untuk keluar...")
        sys.exit(1)
    except Exception as e:
        log_error(f"Gagal membaca CSV: {e}")
        input("\nTekan Enter untuk keluar...")
        sys.exit(1)

    if csv_format == "simple":
        required_cols = {"name"}
        if not required_cols.issubset(set(fieldnames or [])):
            log_error(f"CSV (simple) harus memiliki kolom: {required_cols}")
            log_info(f"Kolom ditemukan: {fieldnames}")
            input("\nTekan Enter untuk keluar...")
            sys.exit(1)

    total = len(rows)
    if total == 0:
        log_warn("CSV kosong, tidak ada task untuk dibuat.")
        input("\nTekan Enter untuk keluar...")
        return

    format_label = "Test Case Template" if csv_format == "template" else "Simple"

    print(f"{Color.BOLD}{'='*60}")
    print(f"  RINGKASAN")
    print(f"{'='*60}")
    print(f"  Parent Task : {task_name}")
    print(f"  List        : {list_name}")
    print(f"  File CSV    : {os.path.basename(csv_path)}")
    print(f"  Format      : {format_label}")
    print(f"  Total       : {total} subtask(s)")
    print(f"{'='*60}{Color.RESET}")
    print()

    confirm = input(f"{Color.YELLOW}Lanjut buat {total} subtask? (y/n): {Color.RESET}").strip().lower()
    if confirm not in ("y", "yes", "ya"):
        log_warn("Dibatalkan.")
        input("\nTekan Enter untuk keluar...")
        return

    print()

    # ── Proses bulk create ──
    results = []
    success_count = 0
    fail_count = 0

    for i, row in enumerate(rows, start=1):
        if csv_format == "template":
            name, description, status, raw_te = parse_row_template(row)
        else:
            name, description, status, raw_te = parse_row_simple(row)

        try:
            time_estimate = float(raw_te) if raw_te else 0
        except ValueError:
            log_warn(f"[{i}/{total}] time_estimate '{raw_te}' bukan angka, diset 0.")
            time_estimate = 0

        if not name:
            log_warn(f"[{i}/{total}] Baris dilewati — name/Test Case ID kosong.")
            results.append({
                "row": i, "name": "", "result": "SKIPPED",
                "task_id": "", "url": "",
            })
            continue

        te_label = f" | est: {int(time_estimate)} menit" if time_estimate > 0 else ""
        log_info(f"[{i}/{total}] Membuat subtask: \"{name}\"{te_label}")

        result = create_subtask(
            api_token, list_id, parent_task_id,
            name, description, status, time_estimate
        )

        if result:
            success_count += 1
            results.append({
                "row": i, "name": name, "result": "SUCCESS",
                "task_id": result["task_id"], "url": result["url"],
            })
        else:
            fail_count += 1
            results.append({
                "row": i, "name": name, "result": "FAILED",
                "task_id": "", "url": "",
            })

        if i < total:
            time.sleep(0.5)

    # ── Simpan hasil ──
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_dir = os.path.dirname(csv_path) or "."
    result_file = os.path.join(result_dir, f"clickup_result_{timestamp}.csv")

    with open(result_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["row", "name", "result", "task_id", "url"])
        writer.writeheader()
        writer.writerows(results)

    # ── Ringkasan ──
    print()
    print(f"{Color.BOLD}{'='*60}")
    print(f"  HASIL")
    print(f"{'='*60}{Color.RESET}")
    log_success(f"Berhasil : {success_count}")
    if fail_count:
        log_error(f"Gagal    : {fail_count}")
    log_info(f"Hasil disimpan ke: {result_file}")
    print()

    input("Tekan Enter untuk keluar...")


if __name__ == "__main__":
    main()
