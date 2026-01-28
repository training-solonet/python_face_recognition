import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import face_recognition
import numpy as np
import requests
import asyncio
from io import BytesIO

# --- KONFIGURASI ---
API_SISWA_URL = os.getenv('API_SISWA_URL', 'https://absensi.connectis.my.id/api/siswa')
WAKTU_SINKRONISASI = "01:00"  # Format 24 Jam

# --- DATABASE DI MEMORI ---
known_face_encodings = []
known_face_names = []

async def load_datasets_from_api():
    """Fungsi untuk sinkronisasi data wajah dari API"""
    global known_face_encodings, known_face_names
    
    print(f"\n--- [TASK] Memulai Sinkronisasi Dataset dari API pada {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: requests.get(API_SISWA_URL, timeout=30))
        response.raise_for_status()
        
        raw_data = response.json()
        data_siswa = raw_data.get('data', raw_data) if isinstance(raw_data, dict) else raw_data

        if not isinstance(data_siswa, list):
            print("❌ Error: Format data bukan list.")
            return

        temp_encodings = []
        temp_names = []

        for siswa in data_siswa:
            if isinstance(siswa, dict) and siswa.get('status') == 'aktif':
                nama = siswa.get('name')
                foto_url = siswa.get('foto')
                
                if not foto_url: continue

                try:
                    img_req = requests.get(foto_url, timeout=10)
                    image = face_recognition.load_image_file(BytesIO(img_req.content))
                    encodings = face_recognition.face_encodings(image)
                    
                    if encodings:
                        temp_encodings.append(encodings[0])
                        temp_names.append(nama)
                        print(f"✅ Ter-load: {nama}")
                    else:
                        print(f"⚠️ Wajah Tidak Terdeteksi: {nama}")
                except Exception as e:
                    print(f"❌ Gagal memproses {nama}: {e}")

        known_face_encodings = temp_encodings
        known_face_names = temp_names
        print(f"--- Selesai! {len(known_face_names)} wajah aktif di memori ---\n")
        
    except Exception as e:
        print(f"❌ Gagal sinkronisasi: {e}")

async def schedule_sync():
    """Looping untuk mengecek waktu setiap menit"""
    print(f"--- Scheduler Aktif: Sinkronisasi harian dijadwalkan pukul {WAKTU_SINKRONISASI} ---")
    while True:
        # Ambil waktu sekarang format Jam:Menit
        now = datetime.now().strftime("%H:%M")
        
        if now == WAKTU_SINKRONISASI:
            await load_datasets_from_api()
            # Tunggu 61 detik agar tidak trigger dua kali di menit yang sama
            await asyncio.sleep(61) 
        else:
            # Cek setiap 30 detik agar tidak membebani CPU namun tetap presisi
            await asyncio.sleep(30)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle FastAPI untuk startup dan shutdown"""
    # 1. Jalankan sekali saat startup agar memori terisi saat server baru nyala
    await load_datasets_from_api()
    # 2. Jalankan scheduler pengecekan jam di background
    asyncio.create_task(schedule_sync())
    yield

app = FastAPI(title="Sistem Absensi Wajah", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze-face")
async def analyze_face(image: UploadFile = File(...)):
    try:
        contents = await image.read()
        img_file = BytesIO(contents)
        
        image_data = face_recognition.load_image_file(img_file)
        face_locations = face_recognition.face_locations(image_data)
        face_encodings = face_recognition.face_encodings(image_data, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            name = "Unknown"
            if known_face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]
            
            face_names.append(name)

        return {
            "status": "success",
            "detected_faces": face_names,
            "count": len(face_names)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)