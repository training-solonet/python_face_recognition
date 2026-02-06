<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/c8eb097c-a5d6-4917-be88-6cafc0f10632" /># Sistem Absensi Wajah Berbasis Library Face Recognition

Proyek ini merupakan sebuah backend berbasis library face-recognition dengan FastAPI yang berfungsi untuk pengenalan wajah menggunakan data foto siswa yang disimpan pada API eksternal.
Aplikasi ini dirancang sebagai bagian dari Sistem Absensi Wajah, di mana pengguna mengirimkan foto melalui endpoint API, lalu sistem akan mencocokkan wajah tersebut dengan dataset wajah yang telah tersimpan di memori server.

Dataset wajah tidak disimpan secara statis, melainkan:

- Diambil dari database external melalui API
- Disinkronkan otomatis ke memori
- Diperbarui secara harian pada waktu tertentu

Dengan pendekatan ini, sistem menjadi dinamis, ringan, dan efisien, tanpa perlu database wajah lokal.

## Tujuan Utama

- Mengenali wajah siswa berdasarkan foto yang dikirim
- Mendukung sistem absensi otomatis berbasis wajah
- Mengelola dataset wajah secara terpusat melalui API eksternal

## Fitur Utama

### 🔄 Sinkronisasi Dataset Otomatis
- Mengambil data siswa aktif dari API eksternal
- Mengunduh foto siswa
- Mengonversi foto menjadi face encoding
- Menyimpan encoding dan nama siswa di memori server

Sinkronisasi dilakukan:
- Saat server pertama kali dijalankan
- Setiap hari pada jam tertentu (default: 01:00)

### 🕒 Scheduler Harian
- Menggunakan asyncio background task
- Mengecek waktu setiap beberapa waktu tertentu
- Menjalankan sinkronisasi tepat pada jam yang ditentukan

### 🧠 Pengenalan Wajah (Face Recognition)
- Endpoint /analyze-face
- Menerima file gambar
- Mendeteksi wajah dalam satu gambar
- Mencocokkan wajah dengan dataset di memori

### 🧩 Teknologi yang Digunakan
- Python 3
- FastAPI
- face_recognition
- NumPy
- Requests
- Uvicorn
- Asyncio

Seluruh dependency tercantum di dalam file **requirements.txt**

## Prasyarat Sistem

### 🖥️ Software
- Python >= 3.8
- pip
- Virtual environment

### 🧠 Library
Linux
```bash
sudo apt update
sudo apt install -y build-essential cmake \
libopenblas-dev liblapack-dev \
libx11-dev libgtk-3-dev \
python3-dev
```

Windows
- Visual Studio Build Tools dengan Desktop Development for C++
- CMake
- Python

## Instalasi Proyek

### 1️⃣ Clone Repository
```bash
git clone https://github.com/training-solonet/python_face_recognition.git
cd python_face_recognition
```

### 2️⃣ Buat Virtual Environment
```bash
python -m venv venv
```
Aktifkan virtual environment:

**Windows**
```bash
venv\Scripts\activate
```

**Linux**
```bash
source venv/bin/activate
```

### 3️⃣ Install Dependency
Pastikan versi pip sudah yang terbaru
```bash
python.exe -m pip install --upgrade pip
```
Lalu instal semua dependency
```bash
pip install -r requirements.txt
```

## Konfigurasi Environment

Aplikasi menggunakan environment variable yang tersimpan di dalam file **.env** untuk konfigurasi API siswa, seperti yang dicontohkan di dalam file **.env.example**.
|Variabel|Deskripsi|
|:---|:---|
|API_SISWA_URL|URL API data siswa|

Jika tidak diatur, sistem akan menggunakan nilai default di dalam kode.

## Menjalankan Server

```bash
python app.py
```
Atau menggunakan uvicorn langsung:
```bash
uvicorn app:app --host 0.0.0.0 --port 5000
```
Server akan berjalan di:
```bash
http://127.0.0.1:5000
```

## Alur Kerja Sistem

1. Server dijalankan
2. Dataset wajah diambil dari API siswa
3. Foto siswa diunduh dan di-encode
4. Encoding disimpan di memori
5. Client mengirim foto ke endpoint
6. Sistem mendeteksi wajah
7. Wajah dicocokkan dengan dataset
8. Nama dikembalikan sebagai response
