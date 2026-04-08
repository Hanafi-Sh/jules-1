# Aethera / SkillForge - Hasil Generate End-to-End

**Target Skill:** PyTorch Dasar
**Konteks User:** Saya tahu Python dasar tapi belum pernah belajar Machine Learning.

---

## Silabus Final (Course)
**Judul Course:** Belajar PyTorch Dasar untuk Pemula Machine Learning

### BAB 1: Pengenalan Machine Learning dan PyTorch
_Memahami konsep dasar Machine Learning (supervised vs unsupervised, classification vs regression), gambaran umum Deep Learning, sejarah dan keunggulan PyTorch, serta menyiapkan lingkungan pengembangan (instalasi, Google Colab, Jupyter Notebook)._

### BAB 2: Fundamental Tensor: Blok Bangunan PyTorch
_Menguasai operasi dasar Tensor: pembuatan, tipe data, shape, operasi matematika, indexing, slicing, reshaping, dan konversi antara Tensor PyTorch dengan NumPy array._

### BAB 3: Autograd dan Computational Graph
_Memahami konsep diferensiasi otomatis (autograd), bagaimana PyTorch melacak komputasi (computational graph), menghitung gradien secara manual dan otomatis dengan backward(), serta manipulasi gradient accumulation dan detach()._

### BAB 4: Mempersiapkan Data untuk Training
_Membuat dataset kustom dengan kelas torch.utils.data.Dataset, mengelola dan mengiterasi data secara efisien dengan DataLoader, serta melakukan transformasi data dasar (normalisasi, augmentasi) menggunakan torchvision.transforms._

### BAB 5: Konsep Dasar Neural Networks
_Memahami konsep dasar neural networks: neuron buatan, layer, fungsi aktivasi (ReLU, Sigmoid, Softmax), forward propagation, backpropagation, serta arsitektur jaringan fully connected. Pengenalan tentang bagaimana neural networks belajar dari data._

### BAB 6: Membangun Model Neural Network Pertama
_Merancang arsitektur neural network sederhana menggunakan modul torch.nn (nn.Linear, nn.Sequential), mengimplementasikan fungsi aktivasi, dan mekanisme forward pass untuk membuat prediksi berdasarkan konsep yang telah dipelajari._

### BAB 7: Melatih Model: Loss Function, Optimizer, dan Training Loop
_Memilih dan mengimplementasikan loss function (seperti MSELoss, CrossEntropyLoss), mengkonfigurasi optimizer (SGD, Adam), serta merangkai seluruh komponen ke dalam training loop yang lengkap (forward pass, hitung loss, backward pass, update weights)._

### BAB 8: Evaluasi Model dan Validasi
_Melakukan evaluasi model pada data test, menghitung metrik akurasi dasar, memahami konsep overfitting/underfitting, serta memisahkan dataset menjadi training, validation, dan test set._

### BAB 9: Studi Kasus: Klasifikasi Gambar Sederhana
_Menerapkan seluruh alur workflow PyTorch secara end-to-end pada dataset standar (contoh: MNIST/Fashion-MNIST) dengan model fully connected. Mulai dari loading data, pra-pemrosesan, membangun model, training, hingga evaluasi hasil._

### BAB 10: Manajemen Model: Penyimpanan dan Pemuatan
_Menyimpan (save) dan memuat (load) model yang telah dilatih beserta state_dict-nya, serta memahami perbedaan antara torch.save dan torch.jit.script untuk deployment._

---

## Desain Level untuk BAB 1: Pengenalan Machine Learning dan PyTorch

**Level 1: Konsep Dasar Machine Learning**
- Memahami definisi dan ruang lingkup Machine Learning (ML), termasuk perbedaan utama antara pembelajaran supervised (klasifikasi dan regresi) dan unsupervised, serta contoh aplikasi dunia nyata dari setiap pendekatan.

**Level 2: Pengenalan Deep Learning**
- Menjelajahi gambaran umum Deep Learning sebagai subset dari ML, konsep Neural Networks dasar, dan peran pentingnya dalam menangani data kompleks seperti gambar, teks, dan suara.

**Level 3: Sejarah dan Keunggulan PyTorch**
- Menguraikan sejarah perkembangan PyTorch, filosofi desainnya yang berfokus pada komputasi dinamis (eager execution), serta keunggulan utamanya seperti kemudahan debug, fleksibilitas, dan komunitas yang aktif dibandingkan framework lainnya.

**Level 4: Menyiapkan Lingkungan Pengembangan**
- Panduan langkah demi langkah untuk menyiapkan lingkungan kerja PyTorch, termasuk opsi instalasi lokal (dengan pip atau conda), penggunaan platform cloud Google Colab, dan pengantar dasar penggunaan Jupyter Notebook untuk eksperimen kode.

---

## Buku Teks Interaktif (Level 1)

### Konsep Dasar Machine Learning

# **Tingkat: Konsep Dasar Machine Learning**
**Membuka Pintu Dunia Pembelajaran Mesin**

---

## **Bab 1: Dari Kode Eksplisit ke Pembelajaran Implisit**

Bayangkan Anda ingin membuat program untuk mendeteksi apakah ada kucing dalam sebuah gambar.

Dengan pemrograman tradisional (atau *rule-based*), Anda akan berusaha keras mendefinisikan aturan eksplisit: "Jika ada bulu, dua telinga segitiga, kumis, mata bersinar, dan ekor, maka itu kucing."

Anda akan menulis ratusan baris kode untuk menganalisis tepi, warna, tekstur. Hasilnya? Sangat rapuh.
- Gambar kucing hitam di latar hitam? Gagal.
- Kucing tanpa ekor? Gagal.
- Anjing shiba inu yang mirip? Terdeteksi sebagai kucing.

Pendekatan ini seperti mengajari seseorang dengan memberikan daftar instruksi mikro yang kaku untuk setiap kemungkinan variasi—sebuah tugas yang mustahil.

**Machine Learning (ML/Pembelajaran Mesin)** membalik paradigma ini. Alih-alih kita yang memberi tahu komputer *aturan* untuk mengenali kucing, kita memberinya **banyak contoh** (gambar yang berlabel "kucing" dan "bukan kucing") dan membiarkannya **menemukan pola dan aturannya sendiri** dari data tersebut.

Kita memberi komputer *data* dan *jawaban yang diinginkan*, lalu memintanya untuk **mempelajari pemetaan** di antara keduanya.

**Definisi Inti:** Machine Learning adalah bidang studi yang memberi komputer kemampuan untuk belajar **tanpa diprogram secara eksplisit** (Arthur Samuel, 1959).

Lebih formal, ini adalah proses di mana sebuah sistem (*model*) meningkatkan kinerjanya pada suatu tugas (*task*), berdasarkan pengalaman (*experience*) yang diukur menggunakan metrik kinerja (*performance measure*), tanpa perubahan kode manual.

**Analoginya:** Seperti seorang anak kecil belajar bahasa. Anda tidak memberinya buku tata bahasa terlebih dahulu. Anda menunjukkan banyak objek sambil mengucapkan namanya ("ini bola", "ini meja").

Dari ratusan contoh, otaknya secara alami menemukan pola, menggeneralisasi, dan akhirnya dapat mengenali "bola" baru yang warnanya atau ukurannya berbeda. ML adalah upaya untuk mereplikasi proses pembelajaran induktif ini di dalam mesin.

### **Mengapa Sekarang? Ledakan dalam Tiga Faktor Kunci:**

1.  **Data (Bahan Bakar):** Dunia digital menghasilkan data dalam skala yang belum pernah terjadi sebelumnya—dari media sosial, sensor IoT, transaksi online, dll. Data adalah "bahan bakar" untuk ML.
2.  **Komputasi (Mesinnya):** Kemampuan pemrosesan, terutama GPU (Graphics Processing Unit) yang awalnya untuk game, ternamat cocok untuk operasi aljabar linier masif yang menjadi inti ML. Cloud computing membuat daya ini dapat diakses.
3.  **Algoritma (Resep/Desain Mesin):** Penemuan dan penyempurnaan algoritma, khususnya dalam **Deep Learning** (jaringan saraf tiruan yang dalam), memungkinkan ekstraksi pola dari data yang sangat kompleks dan tidak terstruktur seperti gambar, teks, dan suara.

---

## **Bab 2: Dua Paradigma Utama: Supervised vs. Unsupervised Learning**

Perbedaan paling mendasar dalam ML terletak pada jenis "pengalaman" atau data yang kita berikan kepada model.

### **2.1 Supervised Learning (Pembelajaran Terawasi)**

Bayangkan belajar dengan seorang **guru yang selalu memberikan kunci jawaban**. Inilah esensi *supervised learning*.

Setiap data pelatihan yang kita berikan kepada model adalah **pasangan**: **Input (Fitur)** dan **Output/Label (Target) yang benar**.

**Tujuan Model:** Mempelajari fungsi `f` yang memetakan Input (`X`) ke Output (`Y`) sedemikian rupa sehingga `f(X) ≈ Y`. Setelah belajar, model dapat memprediksi label `Y'` untuk input baru `X_new` yang belum pernah dilihat.

**Contoh Analogi:** Anda ingin mesin bisa menilai esai. Anda memberikannya 10.000 esai yang sudah dinilai oleh guru manusia (dari nilai A sampai F).

Model menganalisis fitur seperti panjang kalimat, variasi kosakata, struktur paragraf, dan mencoba menemukan korelasi dengan nilai akhir. Setelah "belajar", Anda memberinya esai baru, dan model akan memberikan prediksi nilainya.

**Dua Tugas Utama dalam Supervised Learning:**

#### **A. Klasifikasi (Classification)**
*   **Tujuan:** Memetakan input ke dalam **kategori diskrit (kelas)**.
*   **Pertanyaan Inti:** "Ini termasuk yang mana?"
*   **Output:** Label kategori. Biner (2 kelas: spam/bukan spam, sakit/sehat) atau Multikelas (>2 kelas: kucing/anjing/kuda, sentiment positif/netral/negatif).

**Contoh Aplikasi Dunia Nyata:**
*   **Deteksi Penipuan Transaksi:** Input = data transaksi (jumlah, lokasi, waktu). Output = "Penipuan" atau "Legal".
*   **Diagnosis Medis dari Citra:** Input = gambar MRI otak. Output = "Tumor Jinak", "Tumor Ganas", "Sehat".
*   **Klasifikasi Dokumen:** Input = teks email. Output = "Promosi", "Social", "Utama", "Spam".
*   **Pengenalan Wajah:** Input = gambar wajah. Output = ID orang (misal, "User_123").

#### **B. Regresi (Regression)**
*   **Tujuan:** Memprediksi **nilai kontinu (angka)**.
*   **Pertanyaan Inti:** "Berapa banyak?" atau "Berapa harganya?"
*   **Output:** Sebuah bilangan riil.

**Contoh Aplikasi Dunia Nyata:**
*   **Prediksi Harga Rumah:** Input = fitur rumah (luas, jumlah kamar, lokasi). Output = harga prediksi (misal, 2.1 Miliar).
*   **Peramalan Cuaca:** Input = data sensor hari ini (suhu, kelembaban, tekanan). Output = suhu besok (misal, 28.5°C).
*   **Estimasi Pertumbuhan Pengguna:** Input = data pengguna historis. Output = jumlah pengguna aktif bulan depan.
*   **Penilaian Risiko Kredit:** Input = data profil pelanggan (pekerjaan, pendapatan, histori kredit). Output = skor kredit (angka kontinu).

:::info
**Contoh Kode Sederhana (Konseptual dengan PyTorch):** Bayangkan kita melakukan regresi linear sederhana untuk memprediksi harga rumah berdasarkan luasnya.
:::

```python
# Ini adalah ilustrasi konsep. Detail teknis PyTorch akan dibahas di tingkat berikutnya.
import torch

# 1. Data (Supervised: Kita punya INPUT (luas) dan OUTPUT/TARGET (harga))
luas_rumah = torch.tensor([50., 70., 90., 110.])  # dalam m² (Input/X)
harga_nyata = torch.tensor([300., 420., 500., 620.]) # dalam juta (Target/Y)

# 2. Model Sederhana: f(x) = w * x + b (kita ingin model belajar parameter w (bobot) dan b (bias))
w = torch.tensor(1.0, requires_grad=True) # Inisialisasi bobot
b = torch.tensor(1.0, requires_grad=True) # Inisialisasi bias

# 3. Proses pembelajaran (nanti akan dijelaskan): Model akan mencoba berbagai w dan b.
# Tujuannya: Mencari w dan b sehingga prediksi model (w*luas + b) sedekat mungkin dengan harga_nyata.
# Misal setelah belajar, model menemukan w ≈ 5.0 dan b ≈ 50.0.
# Maka untuk rumah 80 m² yang belum pernah dilihat: prediksi = 5.0*80 + 50.0 = 450 juta.
```

### **2.2 Unsupervised Learning (Pembelajaran Tidak Terawasi)**

Di sini, **tidak ada guru atau label**. Kita hanya memberikan **data input (`X`)** kepada model **tanpa jawaban yang benar**.

Tugas model adalah **menemukan struktur, pola, atau hubungan yang tersembunyi** di dalam data itu sendiri.

**Tujuan Model:** Mempelajari distribusi atau struktur menarik dari data. Ini seperti memberikan setumpuk dokumen campuran pada seseorang dan memintanya, "Kelompokkan yang serupa," tanpa memberitahu kategori apa yang harus dicari.

**Contoh Analogi:** Seorang manajer toko memiliki data pembelian semua pelanggan (item yang dibeli, waktu, jumlah). Tanpa label apa pun, algoritma *unsupervised* dapat mengelompokkan pelanggan ke dalam segmen alami berdasarkan perilaku belanja mereka (misal, "keluarga pembeli bulk", "penggemar makanan organik", "pembeli cepat sajin"). Pola ini tidak diberikan sebelumnya, tapi *ditemukan*.

**Dua Tugas Utama dalam Unsupervised Learning:**

#### **A. Clustering (Pengelompokan)**
*   **Tujuan:** Mengelompokkan data ke dalam **kluster** sehingga data dalam satu kluster sangat mirip, dan data dari kluster berbeda sangat tidak mirip.
*   **Pertanyaan Inti:** "Data saya naturally terbagi menjadi berapa kelompok?"

**Contoh Aplikasi Dunia Nyata:**
*   **Segmentasi Pasar/Pelanggan:** Seperti analogi toko di atas.
*   **Pengelompokan Berita/Dokumen:** Mengorganisir artikel berita berdasarkan topik tanpa tahu topiknya sebelumnya.
*   **Analisis Genetika:** Mengelompokkan pasien berdasarkan ekspresi gen untuk menemukan subtipe penyakit.
*   **Deteksi Anomali (Outlier):** Kluster utama berisi data normal. Titik data yang jauh dari semua kluster bisa jadi anomali (transaksi penipuan, kegagalan sensor).

#### **B. Dimensionality Reduction (Reduksi Dimensi)**
*   **Tujuan:** Mengurangi jumlah variabel (fitur) dalam data sambil **mempertahankan informasi sebanyak mungkin**. Seringkali untuk visualisasi atau pra-pemrosesan.
*   **Pertanyaan Inti:** "Bagaimana cara merepresentasikan data kompleks tinggi-dimensi ini dalam ruang yang lebih sederhana (2D/3D) agar bisa dipahami?"

**Contoh Aplikasi Dunia Nyata:**
*   **Visualisasi Data Kompleks:** Memetakan data pelanggan dengan 100 fitur (usia, pendapatan, 98 riwayat pembelian) ke dalam grafik 2D.
*   **Kompresi Fitur (Feature Compression):** Sebelum memasuki model supervised, mengurangi noise dan redundansi. Misal, pada pengenalan wajah, mengubah ribuan pixel menjadi beberapa puluh "komponen wajah" utama (*eigenfaces*).
*   **Denoising:** Menghilangkan noise dari gambar atau sinyal audio.

### **Perbandingan Singkat**

| Aspek | Supervised Learning | Unsupervised Learning |
| :--- | :--- | :--- |
| **Data Pelatihan** | Berlabel (`X`, `Y`) | Tanpa label (`X`) |
| **Tujuan** | Mempelajari pemetaan `X -> Y` untuk **prediksi** | Mempelajari **struktur/pola** dalam `X` |
| **Tugas Khas** | Klasifikasi, Regresi | Clustering, Reduksi Dimensi |
| **Analogi** | Belajar dengan guru & kunci jawaban | Menemukan pola dalam sebuah koleksi tanpa panduan |
| **Tantangan** | Membutuhkan data berlabel yang mahal & memakan waktu | Evaluasi hasil lebih subjektif, "tanpa jawaban pasti" |

---

## **Bab 3: Pendekatan Lain dan Ruang Lingkup yang Lebih Luas**

Selain dua raksasa di atas, ada paradigma penting lainnya:

*   **Semi-supervised Learning:** Campuran dari sedikit data berlabel dan banyak data tidak berlabel. Realistis di dunia nyata karena memberi label itu mahal.
*   **Reinforcement Learning (RL):** Paradigma berbeda di mana sebuah *agent* belajar dengan **berinteraksi dengan lingkungan** dan menerima *reward* atau *penalty* atas tindakannya. Tujuannya belajar kebijakan (*policy*) untuk memaksimalkan total reward. Contoh: AI bermain game (AlphaGo), robot belajar berjalan, sistem rekomendasi yang mengoptimalkan engagement pengguna.

**Ruang Lingkup ML** juga mencakup:
*   **Preprocessing Data & Feature Engineering:** Membersihkan dan menyiapkan data agar bisa "dicerna" model.
*   **Model Selection & Evaluation:** Memilih algoritma terbaik dan mengukur kinerjanya secara ketat.
*   **Optimization:** Proses inti "pembelajaran" itu sendiri—menyesuaikan parameter model untuk meminimalkan kesalahan (akan dibahas mendalam dengan Gradient Descent di tingkat berikutnya).
*   **Ethics & Bias:** Memahami bagaimana bias dalam data pelatihan dapat menyebabkan diskriminasi dalam model, serta implikasi sosial dari sistem ML.

---

## **Bab 4: Hubungan dengan Deep Learning dan PyTorch**

**Deep Learning (DL)** adalah sub-bidang ML yang menggunakan **jaringan saraf tiruan (Artificial Neural Networks/ANN)** dengan banyak lapisan ("dalam").

DL sangat kuat untuk menangani data tidak terstruktur dan secara otomatis mempelajari fitur tingkat tinggi dari data mentah (misal, dari pixel langsung ke objek).

**PyTorch** adalah salah satu *framework* utama untuk membangun dan melatih model DL dan ML. Keunggulannya terletak pada:

1.  **Dynamic Computational Graph:** Membuat proses prototyping dan debugging lebih intuitif.
2.  **Sintaks yang Pythonic:** Terasa alami bagi programmer Python.
3.  **Komunitas dan Ekosistem yang Kuat:** Banyak model state-of-the-art dirilis dengan kode PyTorch.

Dalam perjalanan belajar ini, Anda akan menggunakan PyTorch sebagai alat untuk mengimplementasikan konsep-konsep ML yang telah dipelajari—mulai dari regresi linear (supervised) hingga autoencoder (unsupervised)—sehingga teori dan praktik berjalan beriringan.

---

### **Rangkuman & Langkah Selanjutnya**

Pada tingkat ini, Anda telah membangun fondasi pemahaman yang kokoh:
*   Machine Learning adalah tentang **belajar dari data**, bukan pemrograman eksplisit.
*   **Supervised Learning** (Klasifikasi & Regresi) membutuhkan data berlabel untuk membuat prediksi.
*   **Unsupervised Learning** (Clustering & Reduksi Dimensi) menemukan pola tersembunyi dalam data tanpa label.
*   Setiap pendekatan memiliki aplikasi dunia nyata yang kuat dan transformative.

:::caction
**Ini baru permulaan.** Dengan konsep ini, Anda sekarang siap untuk masuk ke *workshop* sebenarnya: **memahami bagaimana sebuah model "belajar"**.
:::

Di tingkat berikutnya, kita akan membedah konsep sentral seperti **loss function, gradient descent, dan optimisasi**—proses yang membuat parameter model (seperti `w` dan `b` pada contoh regresi) menyesuaikan diri agar prediksinya semakin akurat.

Di sanalah PyTorch akan mulai bersinar, mengubah konsep matematika menjadi kode yang hidup dan dinamis.
