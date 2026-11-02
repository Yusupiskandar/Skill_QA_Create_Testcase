# Test Case CSV Generation Rules & Guidelines

> **CRITICAL MANDATORY RULE FOR AI AGENT**:
> Ketika user meminta pembuatan test case atau mengetik `/testcase <path_to_pdf>`, AI Agent **WAJIB** mengikuti alur 2 tahap:
> 1. Berikan **Review Preview** skenario test case ke user terlebih dahulu dalam bentuk tabel Markdown (kolom `Est (Menit)` dibiarkan `-` atau kosong).
> 2. **JANGAN** membuat file CSV sebelum user mengonfirmasi atau menyetujui daftar test case tersebut.
> 3. Setelah konfirmasi, buat file CSV dengan template standar 8 kolom di bawah ini, dengan nilai `time estimate` dikosongkan agar diisi manual oleh tim QA.

---

## 1. Header Structure CSV

Header file CSV **WAJIB** persis seperti ini:

```csv
Test Case ID,Requirement,Scenario Type,Test Scenario,Test Step,When (Action),Then (Expected Result),time estimate
```

---

## 2. Definisi & Aturan Kolom

| Nama Kolom | Wajib | Aturan & Format |
| :--- | :---: | :--- |
| **Test Case ID** | Ya | `TC-XX.YY` (Modul 2 digit, nomor urut 2 digit). Unik per baris. |
| **Requirement** | Ya | Kode requirement & ringkasan judul (contoh: `RSR01 - Perluasan Rules Akses List`). |
| **Scenario Type** | Ya | Nilai valid: `Positive` atau `Negative`. |
| **Test Scenario** | Ya | Deskripsi singkat skenario yang diuji. |
| **Test Step** | Ya | Prekondisi akun, data awal, atau setting sistem sebelum aksi. |
| **When (Action)** | Ya | Aksi yang dieksekusi (klik tombol, panggil API, dsb). |
| **Then (Expected Result)** | Ya | Ekspektasi hasil yang dapat diverifikasi (UI & respons sistem). |
| **time estimate** | Ya (Header) | **BIARKAN KOSONG** (`""`) agar diisi manual oleh tim QA. |

---

## 3. Cakupan Pengujian Wajib (Coverage)

Setiap PRD yang dianalisis harus menghasilkan kombinasi:
1. **Positive Flows**: Happy path untuk semua variasi role / user persona yang memiliki izin.
2. **Negative Flows**: Validasi data form, authorization error (HTTP 403), invalid status transition.
3. **Edge Cases**:
   - Kondisi data bernilai `null` / kosong.
   - Race condition (2 user mengeksekusi data yang sama secara simultan).
   - Atomic rollback jika pembuatan entitas turunan gagal (misal gagal generate -R).
   - Audit trail / logging failure handling.

---

## 4. Contoh Baris CSV Standar

```csv
Test Case ID,Requirement,Scenario Type,Test Scenario,Test Step,When (Action),Then (Expected Result),time estimate
TC-01.01,RSR01 - Perluasan Rules Akses List Shipment HAPH pada Menu Return,Positive,Scenario 1.1 : Current locker = admin hub user (existing behaviour),User login dengan role yang berhak melakukan retur; Terdapat shipment HAPH dengan current locker = admin hub,User membuka menu Return / Return Shipment Batch,Shipment muncul di list dan bisa dipilih untuk diretur,
TC-01.02,RSR01 - Perluasan Rules Akses List Shipment HAPH pada Menu Return,Negative,Scenario 1.2 : User tanpa akses submit retur,User tidak memiliki akses ke shipment terkait,User mencoba submit form retur via manipulasi API,Ditolak HTTP 403 dengan pesan error akses ditolak,
```
