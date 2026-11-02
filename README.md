# 📦 Paxel QA Test Case & PRD Generator Agent

Repositori ini menyediakan **Skill & Automation Tool** untuk tim Quality Assurance (QA) dalam menganalisis dokumen Product Requirement Document (PRD) PDF, merumuskan skenario pengujian komprehensif, men-generate test case CSV terstandarisasi, dan meng-import subtask ke **ClickUp** secara otomatis.

---

## 🚀 Fitur Utama

1. **AI PRD Analysis (`/testcase`)**: Ekstraksi otomatis dari file PRD (format PDF) mencakup modul, *acceptance criteria*, role matrix, dan *business logic*.
2. **Skenario Pengujian Menyeluruh (Coverage 360°)**:
   - **Positive Flow**: Pengujian normal (*happy path*) untuk seluruh role yang berhak.
   - **Negative Flow**: Validasi input gagal, hak akses ditolak (HTTP 401/403), transisi status tidak valid.
   - **Edge Cases**: *Race condition*, *atomic rollback*, penanganan nilai `null`/kosong, dan audit logging.
3. **Alur Review Human-in-the-Loop**: AI tidak langsung membuat CSV, melainkan menyajikan tabel preview Markdown terlebih dahulu untuk disetujui atau disesuaikan oleh QA engineer.
4. **ClickUp Subtask Automation**: Meng-import file CSV hasil pengujian langsung menjadi subtask di bawah task induk ClickUp dengan satu klik.

---

## 📁 Struktur Repositori

```text
├── .agents/
│   ├── rules/
│   │   └── testcase_csv_template.md    # Aturan baku template CSV & coverage QA
│   └── skills/
│       └── testcase/
│           ├── SKILL.md                # Definisi & alur kerja skill /testcase
│           └── resources/
│               └── testcase_template_sample.csv # Contoh format CSV standar
├── Click Subtask/
│   ├── clickup_interactive.bat         # Launcher interaktif Windows (klik 2x)
│   ├── clickup_interactive.py          # Script integrasi API ClickUp v2
│   ├── .env.example                    # Template kredensial API ClickUp
│   └── .env                            # Kredensial lokal (diabaikan git)
├── AGENTS.md                           # Aturan workspace utama untuk AI Agent
├── .gitignore                          # Filter file privat, cache, dan log
└── README.md                           # Dokumentasi repositori
```

---

## 🛠️ Prasyarat (Prerequisites)

- **Python 3.8+** terinstal di sistem.
- **Antigravity IDE** atau **Gemini AI Coding Assistant**.
- Akun **ClickUp** dengan akses API Personal Token (jika menggunakan fitur import subtask).

---

## 📖 Panduan Penggunaan

### 1. Men-generate Test Case dari PRD

1. Siapkan file PRD PDF (bisa di folder project atau folder lokal seperti `Downloads`).
2. Di chat Antigravity, ketik:
   ```text
   /testcase "path/ke/file_prd.pdf"
   ```
3. AI akan mengekstrak requirement dan menyajikan **Tabel Preview Test Case**.
4. Periksa daftar skenario pengujian. Jika sudah sesuai, cukup balas:
   ```text
   Lanjut
   ```
   *(atau "ok", "buatkan csv")*.
5. AI akan men-generate file `<nama_fitur>.csv` di root workspace yang siap digunakan.

---

### 2. Meng-import Test Case ke ClickUp Subtask

1. **Setup API Token ClickUp (Sekali saja)**:
   - Buka folder `Click Subtask/`.
   - Salin file `.env.example` menjadi `.env`:
     ```bash
     cp "Click Subtask/.env.example" "Click Subtask/.env"
     ```
   - Masukkan token ClickUp Anda ke dalam file `.env`:
     ```env
     CLICKUP_API_TOKEN="pk_xxxxxxxxxxxxxxxxxxxxxx"
     ```
     *(Dapatkan token di ClickUp: Avatar Profil > Settings > Apps > Generate API Token)*.
2. **Jalankan Tool Interaktif**:
   - Di Windows: Klik dua kali file [`Click Subtask/clickup_interactive.bat`](./Click%20Subtask/clickup_interactive.bat).
   - Atau via terminal:
     ```bash
     python "Click Subtask/clickup_interactive.py"
     ```
3. **Ikuti Petunjuk di Layar**:
   - Paste link task induk ClickUp (contoh: `https://app.clickup.com/t/xxxxxxx`).
   - Pilih file CSV test case yang telah di-generate.
   - Script akan otomatis membuat seluruh subtask dengan status `to do`.

---

## 📋 Spesifikasi Format CSV Standar

File CSV menggunakan 8 kolom baku berikut:

```csv
Test Case ID,Requirement,Scenario Type,Test Scenario,Test Step,When (Action),Then (Expected Result),time estimate
```

| Nama Kolom | Wajib | Aturan Format | Keterangan |
| :--- | :---: | :--- | :--- |
| **Test Case ID** | Ya | `TC-XX.YY` | Modul 2 digit, nomor urut 2 digit (unik per baris). |
| **Requirement** | Ya | String | Kode requirement & judul fitur (contoh: `RSR01 - Perluasan Rules`). |
| **Scenario Type** | Ya | `Positive` / `Negative` | Tipe skenario pengujian. |
| **Test Scenario** | Ya | String | Judul ringkas skenario yang diuji. |
| **Test Step** | Ya | String | Prekondisi akun, setup data, atau kondisi awal. |
| **When (Action)** | Ya | String | Tindakan pengujian yang dieksekusi pengguna/sistem. |
| **Then (Expected Result)** | Ya | String | Ekspektasi hasil pengujian / respon validasi sistem. |
| **time estimate** | Ya (Header) | Kosong (`""`) | Dikosongkan agar diisi manual oleh QA engineer. |

---

## 🔒 Keamanan (Security Guidelines)

- **JANGAN PERNAH** melakukan commit file `.env` yang berisi token API asli ke version control (Git). File ini telah dimasukkan ke dalam `.gitignore`.
- Selalu gunakan file `.env.example` sebagai referensi konfigurasi publik.
