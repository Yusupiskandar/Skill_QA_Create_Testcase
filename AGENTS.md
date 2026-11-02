# Paxel QA Test Case & PRD Workspace Guidelines

Dokumen ini adalah acuan utama bagi AI Agent dalam mengelola dan men-generate test case di workspace repository ini.

---

## 1. Perintah `/testcase` (PRD to Test Case Workflow)

Setiap kali user mengetik perintah dengan awalan `/testcase` (misalnya: `/testcase "docs/PRD-Feature.pdf"` atau path absolut lokal), AI Agent **WAJIB** mengikuti alur 4 tahap berikut:

### Tahap 1: Ekstraksi & Analisis PRD PDF
1. AI mengambil path PDF yang diberikan user (mendukung path berkutip `"` maupun tanpa kutip, path lokal workspace, maupun path di luar workspace seperti folder `Downloads`).
2. AI membaca dan menganalisis seluruh isi dokumen PRD (deskripsi fitur, acceptance criteria, role matrix, workflow, edge cases, error handling).

### Tahap 2: Merumuskan Skenario Test Case Lengkap
AI merumuskan test case komprehensif yang mencakup:
- **Positive Scenarios (Happy Path)**: Alur normal pengujian untuk setiap role/aktor yang berhak.
- **Negative Scenarios**: Validasi input gagal, hak akses ditolak (HTTP 401/403), status shipment tidak sesuai, dsb.
- **Edge Cases & Race Condition**: Dua user submit bersamaan, data bernilai `null`, koneksi DB log timeout, dsb.

### Tahap 3: REVIEW KE USER (DILARANG LANGSUNG BIKIN CSV!) ⚠️
- AI **TIDAK BOLEH** langsung membuat file `.csv` pada respon pertama.
- AI menampilkan tabel / daftar review test case terlebih dahulu kepada user dalam format Markdown yang rapi:
  - Ringkasan fitur & requirement yang diekstrak dari PRD.
  - Tabel usulan test case lengkap dengan kolom:
    `Test Case ID` | `Requirement` | `Scenario Type` | `Test Scenario` | `Test Step` | `When (Action)` | `Then (Expected Result)` | `Est (Menit)` *(kosongkan / `-`)*
  - Highlight skenario kritis atau asumsi jika ada ambiguitas pada PRD.
- AI mengakhiri respon dengan meminta konfirmasi:
  > *"Apakah daftar test case di atas sudah sesuai, atau ada skenario yang ingin ditambahkan/disesuaikan? Jika sudah OK, silakan balas **'Lanjut'** untuk men-generate file CSV-nya."*

### Tahap 4: Generate File CSV (Hanya Setelah Konfirmasi User)
- Ketika user merespon konfirmasi setuju (misal: *"lanjut"*, *"ok"*, *"lanjutkan untuk di buatkan csv nya"*, *"buatkan csv"*):
  1. AI membuat file CSV baru di root workspace (`<workspace_root>/<nama_fitur>.csv`).
  2. Format CSV **WAJIB** mengikuti struktur baku di bawah ini.
  3. AI menginformasikan lokasi file CSV dan mengingatkan user bahwa file siap di-import ke ClickUp via `Click Subtask/clickup_interactive.bat`.

---

## 2. Struktur Baku Template CSV

Header CSV **WAJIB PERSIS** sebagai berikut:

```csv
Test Case ID,Requirement,Scenario Type,Test Scenario,Test Step,When (Action),Then (Expected Result),time estimate
```

### Spesifikasi Kolom:

| Nama Kolom | Wajib | Keterangan & Aturan Nilai | Contoh Nilai |
| :--- | :---: | :--- | :--- |
| **Test Case ID** | Ya | Format `TC-XX.YY` (Modul 2 digit, nomor urut 2 digit). | `TC-01.01`, `TC-01.02` |
| **Requirement** | Ya | Kode requirement & judul fitur dari PRD. | `RSR01 - Perluasan Rules Akses List Shipment HAPH` |
| **Scenario Type** | Ya | Hanya `Positive` atau `Negative`. | `Positive` |
| **Test Scenario** | Ya | Judul ringkas skenario pengujian. | `Scenario 1.1 : Current locker = admin hub user` |
| **Test Step** | Ya | Prekondisi akun, setup data, atau kondisi awal. | `User login dengan role yang berhak; Shipment status HAPH` |
| **When (Action)** | Ya | Langkah tindakan yang dieksekusi penguji / sistem. | `User membuka menu Return dan mencari shipment terkait` |
| **Then (Expected Result)**| Ya | Ekspektasi hasil pengujian / response validasi sistem. | `Shipment muncul di list dan dapat dipilih untuk diretur` |
| **time estimate** | Ya (Header) | **BIARKAN KOSONG** (`""`) agar diisi manual oleh tim QA. | `""` *(kosong)* |

---

## 3. Integrasi ke ClickUp Subtask

Template CSV di atas dirancang untuk langsung diproses oleh [`Click Subtask/clickup_interactive.py`](file:///c:/PAXEL/Testcase/Click%20Subtask/clickup_interactive.py):
- **Subtask Name** = `Test Case ID` - `Test Scenario`
- **Subtask Description** = Gabungan rapi dari `Requirement`, `Scenario Type`, `Test Step`, `When (Action)`, `Then (Expected Result)`
- **Subtask Status** = `to do`
- **Subtask Time Estimate** = `time estimate` (jika kosong, subtask dibuat tanpa estimate dan siap diisi tim di ClickUp)
