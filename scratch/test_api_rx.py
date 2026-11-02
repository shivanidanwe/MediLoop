import urllib.request
import json

# Login as pharmacist
login_data = json.dumps({'email': 'pharmacist.ramesh@mediloop.com', 'password': 'password123'}).encode()
login_req = urllib.request.Request('http://127.0.0.1:8000/api/v1/auth/pharmacist/login', data=login_data, headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(login_req) as res:
        token_data = json.loads(res.read())
        token = token_data['access_token']
        
        # Fetch prescription 90
        rx_req = urllib.request.Request('http://127.0.0.1:8000/api/v1/prescriptions/90', headers={'Authorization': f'Bearer {token}'})
        with urllib.request.urlopen(rx_req) as rx_res:
            rx = json.loads(rx_res.read())
            print(f"Prescription #{rx['id']} API Response:")
            print(f"Status: {rx.get('verification_status')}")
            for it in rx.get('items', []):
                print(f"  * Medicine: {it.get('medicine_name')} | Strength: {it.get('strength')} | Dosage: {it.get('dosage_pattern')}")
except Exception as e:
    print('Error:', e)
