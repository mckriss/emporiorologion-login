import os
import sys
from curl_cffi import requests

EMPORIO_EMAIL = os.getenv("EMPORIO_EMAIL")
EMPORIO_PASSWORD = os.getenv("EMPORIO_PASSWORD")

def test_login():
    if not EMPORIO_EMAIL or not EMPORIO_PASSWORD:
        print("[!] ERROR: Δεν βρέθηκαν τα EMPORIO_EMAIL / EMPORIO_PASSWORD στα secrets.")
        sys.exit(1)

    print(f"[*] Εκκίνηση Login για τον χρήστη: {EMPORIO_EMAIL}")
    
    session = requests.Session(impersonate="chrome120")
    base_url = "https://www.emporiorologion.gr"
    login_url = f"{base_url}/gr/login"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'el-GR,el;q=0.9,en-US;q=0.8,en;q=0.7',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': base_url,
        'Referer': f"{base_url}/gr/login",
    }

    try:
        # 1. Αρχικό GET για cookies (PHPSESSID)
        session.get(f"{base_url}/", headers={'User-Agent': headers['User-Agent']})

        # 2. Αποστολή POST με τα σωστά πεδία (username & password)
        payload = {
            'username': EMPORIO_EMAIL,
            'password': EMPORIO_PASSWORD
        }

        res_post = session.post(login_url, data=payload, headers=headers)
        
        if res_post.status_code == 200 and "uid" in res_post.text:
            data = res_post.json()
            print(f"[SUCCESS] Επιτυχής σύνδεση! Χρήστης: {data.get('nome')} (UID: {data.get('uid')})")
            return session
        else:
            print(f"[FAIL] Αποτυχία σύνδεσης: {res_post.text}")
            return None

    except Exception as e:
        print(f"[!] Σφάλμα: {e}")
        return None

if __name__ == "__main__":
    test_login()
