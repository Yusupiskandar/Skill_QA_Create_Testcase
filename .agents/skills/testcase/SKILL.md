---
name: testcase
description: >-
  Use this skill whenever the user types /testcase or asks to convert/generate
  QA test cases from a PRD PDF document. Analyzes the PRD, presents a structured
  review to the user, and generates a standardized CSV upon user approval.
---

# PRD to QA Test Case Generator Skill

Panduan instruksi ketika user menjalankan perintah `/testcase <path_to_pdf>`.

## Workflow Eksekusi

### 1. Baca & Pahami Path PDF
- Dapatkan path file PDF dari argumen perintah `/testcase` (contoh: `/testcase "docs/PRD-Feature.pdf"` atau path absolut).
- Baca dan ekstrak konten teks PRD menggunakan tool pembaca file / PDF extractor.

### 2. Analisis Kebutuhan QA Komprehensif
Identifikasi secara mendalam:
- **Modul & Acceptance Criteria (AC / Requirement Code)**: Kode modul dan deskripsi kriteria penerimaan.
- **Positive Scenarios (Happy Path)**: Alur pengujian normal untuk setiap variasi persona/role yang memiliki hak akses.
- **Negative Scenarios**: Validasi input gagal, batasan hak akses (HTTP 401/403 Unauthorized/Forbidden), transisi status tidak valid.
- **Edge Cases & Race Condition**: Dua user mengeksekusi bersamaan, data bernilai `null`/kosong, timeout rollback, audit log failure.

### 3. TAHAP REVIEW (PENTING: Dilarang Langsung Membuat CSV!) ⚠️
Tampilkan ringkasan requirement dan tabel preview test case ke user terlebih dahulu dalam format Markdown. Kolom estimasi waktu dibiarkan strip `-` atau kosong agar diisi manual oleh tim:

```markdown
### Ringkasan PRD & Modul:
...

### Usulan Test Case:
| Test Case ID | Requirement | Scenario Type | Test Scenario | Test Step | When (Action) | Then (Expected Result) | Est (Menit) |
|---|---|---|---|---|---|---|---|
| TC-01.01 | ... | Positive | ... | ... | ... | ... | - |
...

---
> ❓ **Konfirmasi:** Apakah daftar test case di atas sudah sesuai, atau ada skenario yang perlu disesuaikan? 
> Jika sudah sesuai, silakan balas **'Lanjut'** / **'Buatkan CSV'** agar saya buatkan file CSV-nya.
```

### 4. TAHAP GENERASI CSV (Hanya Setelah User Menyetujui)
Begitu user merespon setuju (*"lanjut"*, *"ok"*, *"lanjutkan"*, *"buatkan csv"*, dsb):
1. Tulis file CSV ke root workspace proyek: `<workspace_root>/<nama_fitur>.csv` dengan encoding UTF-8.
2. Format header CSV baku **WAJIB**:
   `Test Case ID,Requirement,Scenario Type,Test Scenario,Test Step,When (Action),Then (Expected Result),time estimate`
3. Nilai kolom `time estimate` **WAJIB DIKOSONGKAN** (`""`) agar diisi manual oleh tim QA.
4. Informasikan ke user bahwa file CSV berhasil dibuat dan siap di-import ke ClickUp subtask via `Click Subtask/clickup_interactive.bat`.

## Template Referensi
Contoh format CSV baku dapat dilihat di:
[testcase_template_sample.csv](./resources/testcase_template_sample.csv)
