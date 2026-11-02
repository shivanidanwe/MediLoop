import urllib.request
import json
import sys
sys.path.insert(0, 'backend')
from app.core.database import SessionLocal
from app.models import Medicine, Prescription

services = [
    ('Backend API', 'http://127.0.0.1:8000/docs'),
    ('Pharmacy Dashboard', 'http://localhost:5173/'),
    ('Flutter Mobile App', 'http://localhost:3000/'),
    ('Ollama AI', 'http://127.0.0.1:11434/api/tags'),
]

for name, url in services:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as res:
            print(f'[ONLINE] {name:20} -> HTTP {res.status} ({url})')
    except Exception as e:
        print(f'[OFFLINE] {name:20} -> {e}')

try:
    db = SessionLocal()
    m_cnt = db.query(Medicine).count()
    p_cnt = db.query(Prescription).count()
    print(f'[ONLINE] {"PostgreSQL Database":20} -> Connected ({m_cnt} medicines, {p_cnt} prescriptions)')
    db.close()
except Exception as e:
    print(f'[OFFLINE] {"PostgreSQL Database":20} -> {e}')

