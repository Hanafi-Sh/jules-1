# Aethera (SkillForge): Buku Panduan Lengkap & Sejarah Pengembangan

Dokumen ini adalah arsip hidup, visi utama, dan peta jalan teknis dari **Aethera** (sebelumnya disebut SkillForge)—sebuah platform penguasaan keahlian (*skill mastery*) yang terpersonalisasi, komprehensif, dan memecah kompleksitas pembelajaran menjadi langkah-langkah logis dan tidak tumpang tindih (MECE - *Mutually Exclusive, Collectively Exhaustive*).

---

## BAGIAN I: Visi Utama & Identitas Produk

### 1. Konsep & Tujuan
Aethera dibangun untuk membunuh tutorial yang terpisah-pisah, video YouTube yang tidak terstruktur, dan dokumentasi resmi yang membosankan. Tujuannya adalah menciptakan **satu perjalanan belajar vertikal yang digenerasi secara *real-time*** oleh kecerdasan buatan (*Artificial Intelligence*).

Kurikulum ini tidak statis. Ia disesuaikan secara dinamis dengan:
1.  **Gaya Belajar Pengguna:** Menggunakan analogi yang mudah dipahami, pemecahan paragraf panjang menjadi *micro-chunks*, dan bahasa yang bersahabat (*pedagogical*).
2.  **Konteks Awal Pengguna:** Sistem harus tahu apa yang pengguna *sudah* tahu (untuk dilewati) dan apa yang *belum* mereka tahu (fondasi prasyarat yang harus diajarkan lebih dulu).

### 2. Desain UI/UX: *The Cozy Vertical Journey*
Estetika Aethera menolak konsep "halaman web" atau "dashboard" konvensional.
*   **Vibe:** *Cozy* (Nyaman), memberikan rasa pencapaian progresif (*rewarding*), layaknya *game* simulasi kehidupan.
*   **Palet Warna:** *Earth tones* (hijau hutan, cokelat kayu, biru malam) dengan elemen UI bersudut membulat (*rounded corners*).
*   **Topografi:** Pengguna tidak berpindah halaman. Halaman utama adalah ilustrasi jalur/peta yang memanjang ke bawah. Setiap "Bab" adalah sebuah stasiun/pos. Pengguna menscroll ke bawah untuk membuka kunci (*unlock*) materi selanjutnya.
*   **Komponen Interaktif:** Teks diformat dengan komponen UI khusus seperti akordeon (*accordion*) untuk penjelasan ekstra (*Deep Dives*), kotak peringatan (*InfoBox*), blok kode dengan tombol salin, dan cincin progres (*Progress Ring*) di sudut layar yang terisi saat membaca.

---

## BAGIAN II: Arsitektur *Multi-Agent AI* (Pendekatan *Top-Down DAG*)

Untuk menangani kurikulum yang sangat fluktuatif—dari topik sederhana yang butuh 3 Bab hingga topik kompleks seperti "Membangun LLM" yang butuh 50 Bab—Aethera tidak memaksakan AI untuk memuntahkan seluruh JSON dalam satu *prompt*.

Aethera menggunakan arsitektur **Directed Acyclic Graph (DAG)** dan hierarki berlapis (Pilar -> Bab -> Level) yang dijalankan oleh **14 Agen AI Terspesialisasi**.

### Filosofi *The Critic Loop* (Sistem X.1)
Setiap agen yang bertugas *menulis/merancang* (Agen X) selalu diawasi oleh agen *Reviewer* (Agen X.1). Agen X.1 bertugas mencari kelemahan, halusinasi, tumpang tindih materi, dan memperbaikinya.

### Filosofi *Decoupled JSON Formatting*
Agen pemikir (*Deep Thinking*) tidak boleh dibebani dengan tugas menjaga sintaks JSON tetap valid, karena itu merusak kualitas pedagogi. Seluruh Agen X dan X.1 hanya mengeluarkan **Teks Mentah (*Raw Text*)**. Setelah teks mentah disempurnakan, teks tersebut dioper ke **JSONStructurer**, sebuah utilitas AI cepat yang murni bertugas mengubah teks menjadi JSON tanpa mengubah satu makna kata pun.

### Daftar Lengkap Agen (Pipeline Aethera)

1.  **Tahap Asesmen (Triage)**
    *   **Agent 0 (Triage Analyst):** Menilai skor kompleksitas topik (1-10) dan mendeteksi konsep prasyarat fundamental yang wajib dikuasai sebelum belajar topik utama.
    *   **Agent 0.1 (Triage Reviewer):** Memastikan tidak ada fondasi krusial yang tertinggal.
2.  **Tahap Makro (Pilar/Fase)**
    *   **Agent 1 (Syllabus Architect):** Membuat *Macro Pillars* (Fase/Pilar Utama). Ia membandingkan prasyarat yang *sudah* diketahui pengguna dan yang *belum*, lalu memaksa Fase awal untuk mengajarkan prasyarat yang belum diketahui.
    *   **Agent 1.1 (Syllabus Reviewer):** Memvalidasi aliran logis antar Pilar Utama agar memenuhi standar MECE.
3.  **Tahap Spesifik (Bab)**
    *   **Agent 2 (Phase Designer):** Memecah satu Fase Makro menjadi Bab-Bab (*Chapters*) spesifik.
    *   **Agent 2.1 (Phase Reviewer):** Memastikan Bab-Bab tersebut tidak tumpang tindih.
4.  **Tahap Mikro (Level)**
    *   **Agent 3 (Chapter Designer):** Memecah satu Bab menjadi Level-Level (*Sub-topics*) yang bisa diselesaikan dalam 5-10 menit membaca.
    *   **Agent 3.1 (Chapter Reviewer):** Menyempurnakan alur Level.
5.  **Tahap Konten (Buku Teks)**
    *   **Agent 4 (Content Author):** Penulis utama. Menggunakan *deep reasoning* untuk menulis narasi buku teks yang sangat komprehensif, mendalam, dan kaya analogi untuk satu Level.
    *   **Agent 4.1 (Content Reviewer):** Sang Editor. Mengidentifikasi halusinasi AI, memperbaiki penjelasan yang terlalu dangkal, dan memastikan keselarasan dengan Konteks Kurikulum Master.
6.  **Tahap Presentasi UI**
    *   **Agent 5 (Formatter):** Menggunakan model AI cepat (`deepseek-chat`) untuk membungkus narasi dari Agent 4.1 ke dalam tag HTML/Markdown *custom* (misal `<InfoBox>`, `<Accordion>`) agar siap di-*render* oleh *Frontend* Next.js.
7.  **Tahap Validasi (Kuis)**
    *   **Agent 6 (Quiz Master):** Membuat 2-3 pertanyaan pilihan ganda yang menguji konsep, bukan hafalan buta.
    *   **Agent 6.1 (Quiz Reviewer):** Memverifikasi bahwa kunci jawaban benar secara faktual dan pengecoh (*distractors*) masuk akal.
8.  **Tahap Interaktivitas (*Curiosity*)**
    *   **Agent 7 (Question Suggester):** Menganalisis teks Level untuk menemukan istilah teknis yang rumit, lalu menyodorkan 3-5 "Pertanyaan Pancingan" (Misal: *"Apa sebenarnya fungsi .backward() di balik layar?"*) yang bisa diklik pengguna untuk ditanyakan ke *Chatbot* pendamping.
    *   **Agent 7.1 (Question Reviewer):** Memastikan pertanyaan pancingan tersebut benar-benar menggugah rasa ingin tahu yang relevan.

---

## BAGIAN III: Rekayasa *Backend* Kelas Produksi (*Production-Grade Engineering*)

Aethera tidak hanya canggih di atas kertas, tetapi dibangun untuk bertahan dari kegagalan jaringan, batas waktu HTTP, dan beban komputasi masif.

1.  **FastAPI & Asynchronous Routing:** *Backend* dibangun menggunakan Python FastAPI yang sepenuhnya *non-blocking* (`async`/`await`).
2.  **Optimasi *Cache Hit* DeepSeek (Hemat Biaya 90%):** Karena setiap Agen (mulai dari Agent 2 hingga 7.1) membutuhkan referensi silabus lengkap agar konteksnya tidak melenceng, kita selalu mengirimkan *Master Curriculum Context*. Untuk mencegah biaya token API membengkak, fungsi `build_context_prefix` menaruh JSON raksasa ini di karakter pertama (*prefix*) dari `system_prompt`. DeepSeek secara otomatis mendeteksi *prefix* yang sama persis ini dan memberikan diskon *Cache Hit* ($0.028/1M Token vs $0.28/1M Token).
3.  **Generasi Dinamis *Just-in-Time* (*Lazy Loading*):**
    *   Jika sistem mencoba memanggil API untuk men-*generate* isi teks 50 Bab sekaligus, pengguna harus menunggu 1 jam.
    *   Aethera memecahnya: Endpoint `/jobs/start` (via *Background Tasks*) **hanya** menghasilkan kerangka JSON kosong (Fase -> Bab -> Level) dalam 3-5 menit.
    *   Isi materi teks, UI Formatter, Kuis, dan Pertanyaan baru akan digenerate saat pengguna men-*scroll* ke level tersebut, dengan memanggil *endpoint* `/level/lazy-load`. Menunggu 1 Level hanya butuh ~20 detik!
4.  **Paralelisasi & Ketahanan (*Resilience*):**
    *   Fungsi `generate_structural_tree_async` menggunakan `asyncio.gather` untuk merancang puluhan Bab secara bersamaan.
    *   Dilengkapi dengan `asyncio.Semaphore` untuk mencegah *rate limit* (Error 429) dari server DeepSeek.
    *   Dilengkapi parameter `return_exceptions=True` sehingga jika desain Bab 7 gagal, Bab 1-6 dan 8-50 tetap berhasil tersimpan.
    *   Setiap pemanggilan API LLM dibungkus pustaka `tenacity` (Mekanisme *Auto-Retry* dengan *Exponential Backoff*) yang akan mengulang otomatis jika JSON gagal di-*parse* atau server API terputus.
5.  **Keamanan Konkurensi Database (SQLite *Locks*):**
    *   Karena banyak Agen bekerja paralel dan mencoba memperbarui *Progress Bar* di *database* secara bersamaan, sistem menggunakan `asyncio.Lock()` sebelum melakukan `db.commit()` untuk menghindari *crash* sistemik *"database is locked"*.
6.  **Sistem *Logging* Lengkap:**
    *   Setiap koin yang dibelanjakan untuk API disimpan. Fungsi `log_api_call` merekam `system_prompt`, `user_prompt`, dan `response` utuh ke dalam file lokal `llm_api_logs.jsonl` agar tidak ada token yang terbuang sia-sia meski skrip terhenti.

---

## BAGIAN IV: Sejarah Lengkap Pengembangan Aethera

Aethera (SkillForge) lahir dari sebuah kanvas kosong dan berevolusi melalui serangkaian iterasi diskusi teknis yang sangat intensif antara Pengguna (Visioner Produk) dan AI *Software Engineer*. Berikut adalah rekam jejak lengkap pembangunannya:

### Fase 1: Konseptualisasi dan Fondasi Awal
*   **Awal Mula:** Pengguna memberikan *prompt* raksasa yang berisi visi "Buku Teks Masa Depan" yang interaktif, menolak halaman web biasa, berfokus pada "Perjalanan Vertikal", dan menggunakan 3 Agen AI (*Syllabus Architect, Content Author, Formatter*).
*   **Klarifikasi Teknis:** Sebelum menulis satu baris kode pun, AI melakukan *Deep Planning Mode*. AI menanyakan tumpukan teknologi (Frontend: Next.js/Tailwind, Backend: FastAPI), akses ke model API (Pengguna memilih DeepSeek), autentikasi, dan batasan MVP. Pengguna setuju untuk menunda Database/UI dan berfokus murni pada logika Backend dan Kurikulum.
*   **Penambahan Agen:** Pengguna menyarankan agar transisi dari Silabus yang luas ke Konten yang spesifik tidak terlalu curam. Maka, lahirlah hierarki **Course -> Chapter (BAB) -> Level**, dan sistem ditambahkan 2 agen baru: *Chapter Designer* dan *Quiz Master* (Total 5 Agen).
*   **Eksekusi Pertama:** AI mengatur struktur folder FastAPI (`app/api`, `app/models`, dll), membuat file `requirements.txt`, menyiapkan `.env` untuk API Key (secara aman), menyusun Pydantic Models untuk struktur hierarki, dan menulis logika pemanggilan `AsyncOpenAI` ke API DeepSeek. Skrip uji coba dijalankan dan *database* SQLite diinisialisasi.

### Fase 2: Implementasi *DeepSeek Reasoner* & Refleksi Evaluasi Diri
*   **Upgrade Kualitas:** Pengguna menyadari bahwa untuk menyusun kurikulum MECE yang brilian, sistem harus dipaksa menggunakan model "berpikir" (`deepseek-reasoner`). Namun *Formatter* harus tetap menggunakan `deepseek-chat` karena ia hanya bertugas membungkus teks dengan komponen UI.
*   **Tantangan Ekstraksi JSON:** Model *reasoner* sering memberikan "jejak pemikiran" (*reasoning traces*) dan membungkus JSON di dalam blok *markdown*, yang membuat `json.loads()` standar hancur. AI merespons dengan menulis fungsi *Regex Extractor* khusus (`extract_json_from_text`) yang sangat tangguh untuk memanen JSON dari tumpukan teks model *reasoner*.
*   **Kelahiran Agen Kritikus (Sistem X.1):** Pengguna mengusulkan ide brilian: Bagaimana jika ada agen pengawas (Agen ke-6) yang mengawasi hasil Agen 1? Ide ini disetujui, dan `CurriculumSupervisor` lahir. Namun, evolusi tidak berhenti di situ. Di interaksi selanjutnya, pengguna memutuskan bahwa **semua** agen pemikir harus diawasi. AI merombak total `agents.py` dan menciptakan agen cermin (Agent 0.1, 1.1, 2.1, 3.1, 5.1, 7.1) untuk membentuk "Lingkaran Validasi Kritis" (*The Critic Loop*).

### Fase 3: Skalabilitas, DAG, dan Asesmen Prasyarat
*   **Masalah Pemula vs Ahli:** Pengguna menyoroti bahwa tidak mungkin seseorang belajar "PyTorch Advanced" tanpa tahu apa itu "Tensor". Jika prasyarat ini digabung dalam Silabus utama, babnya akan membludak atau terlewat.
*   **Solusi Asesmen:** Lahirlah Agent 0 (`PrerequisiteAssessor`). Kini sistem meminta pengguna mencentang apa yang sudah mereka tahu, lalu AI memodifikasi *prompt* Agen Arsitek untuk *memaksa* pembuatan bab pengantar khusus untuk prasyarat yang *tidak diketahui* pengguna, dan melewati apa yang sudah mereka kuasai. Hierarki diperluas menjadi pendekatan *Top-Down Directed Acyclic Graph* (DAG) dengan menyisipkan tingkat `Phase` (Pilar Makro) di atas `Chapter`.

### Fase 4: *Just-in-Time Generation* & Agen Rasa Ingin Tahu
*   **Fitur *Curiosity*:** Pengguna meminta agar platform aktif menyarankan pertanyaan. AI menciptakan `QuestionSuggester` (Agent 7) yang membaca teks level dan menghasilkan pertanyaan pancingan interaktif untuk *Chatbot*.
*   **Penyelesaian Bom Waktu (Timeout):** Jika AI disuruh membuat 50 Bab sekaligus, API akan *timeout*. Pengguna mengusulkan generasi asinkronus (hanya meng-generate isi bab saat pengguna men-*scroll* ke bab tersebut).
*   **Perombakan Orkestrator:** AI membelah orkestrator menjadi dua. Endpoint `/jobs/start` (dijalankan di *background tasks*) kini hanya bertugas memanggil Agent 0 hingga Agent 2.1 secara paralel untuk membangun kerangka *JSON Tree* yang kosong (Hanya Judul & Deskripsi, tanpa teks materi). Lalu, diciptakan endpoint baru `/level/lazy-load` yang akan ditembak oleh frontend secara *on-demand*. Di endpoint ini, Agent 3 (Konten), Agent 4 (Formatter), Agent 5 (Kuis), dan Agent 7 (Curiosity) bekerja menyusun isi materi yang berat dalam hitungan detik.

### Fase 5: *Engineering Hardening* (Stabilitas Produksi)
*   **Titik Kritis Kegagalan:** Dengan puluhan agen bekerja bersamaan (*Concurrency*), sistem menghadapi risiko besar: (1) SQLite *Crash* karena *Concurrent Writes*, (2) API DeepSeek *Timeout*, dan (3) *Cascading Failures* (satu Bab error menggagalkan seluruh pembuatan *Course*).
*   **Penambalan (*Patching*):** AI menambahkan `tenacity` untuk *Auto-Retry*. AI membungkus *progress update callback* dengan `asyncio.Lock()` untuk mengatur antrean penulisan ke database lokal. Terakhir, AI memodifikasi `asyncio.gather` dengan `return_exceptions=True` dan membungkus *worker* dengan `try/except` sehingga setiap agen terisolasi; kegagalan satu Bab tidak lagi menghancurkan keseluruhan kurikulum.

### Fase 6: Dekopel JSON (*Decoupled JSON Structuring*)
*   **Puncak *Prompt Engineering*:** Di akhir perjalanan, pengguna menyadari bahwa memaksa model *Deep Thinking* untuk mematuhi kurung kurawal `{}` dari JSON telah mengurangi fokus AI dalam menulis materi berkualitas tinggi.
*   **Solusi Utama:** AI menghapus semua instruksi JSON dari *prompt* agen pemikir. Kini, mereka menulis esai bebas, *bullet points*, dan kerangka kerja murni dalam *Plain Text*. Setelah teks tersebut disetujui oleh para Reviewer, teks murni itu dilempar ke sebuah utilitas baru, `JSONStructurer`, yang menggunakan model cepat `deepseek-chat` murni untuk merapikan teks tersebut menjadi Pydantic-JSON. Ini mengembalikan 100% kapasitas otak AI ke tugas intinya: Pendidikan.

### Penutup Sejarah
Pada tahap ini, *backend* Aethera telah bertransformasi dari sekadar "pembungkus API biasa" menjadi sebuah **Pabrik EdTech Otonom**. Seluruh kode tersimpan aman. Tidak ada API Key yang bocor ke repositori publik. Tidak ada token yang terbuang sia-sia berkat *Logger* `.jsonl` dan sistem *Prefix Context Caching*.

Sistem ini berdiri tegak, siap untuk diintegrasikan dengan *Frontend Next.js* untuk mewujudkan UI *The Cozy Vertical Journey*.

*(Dokumen ini dibuat secara otomatis pada iterasi terakhir komitmen pengembangan Backend MVP).*
