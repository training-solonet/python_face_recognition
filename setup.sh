sudo apt-get update
sudo apt-get install -y cmake build-essential libopenblas-dev liblapack-dev libx11-dev libgtk-3-dev
python3 -m venv env_wajah
source env_wajah/bin/activate
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 5000 --workers 2