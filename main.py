import os
import sys
import json
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
        'Referer': f"{base_url}/",
    }

    try:
        # 1. Αρχικό GET στην αρχική σελίδα για ανάκτηση Cookies
        print("[*] 1. Αίτημα στην αρχική σελίδα...")
        res_get = session.get(f"{base_url}/", headers={'User-Agent': headers['User-Agent']})
        print(f"    Cookies: {session.cookies.get_dict()}")

        # 2. Δοκιμή Payloads με διαφορετικούς συνδυασμούς keys
        payloads = [
            # Συνδυασμός 1: Όλα τα πιθανά keys μαζί
            {
                'email': EMPORIO_EMAIL,
                'password': EMPORIO_PASSWORD,
                'username': EMPORIO_EMAIL,
                'login_username': EMPORIO_EMAIL,
                'login_password': EMPORIO_PASSWORD
            },
            # Συνδυασμός 2: Καθαρό email & password
            {
                'email': EMPORIO_EMAIL,
                'password': EMPORIO_PASSWORD
            },
            # Συνδυασμός 3: Καθαρό username & password
            {
                'username': EMPORIO_EMAIL,
                'password': EMPORIO_PASSWORD
            }
        ]

        for i, payload in enumerate(payloads, 1):
            print(f"\n[*] 2.{i} Δοκιμή POST στο {login_url} (Payload {i})...")
            res_post = session.post(login_url, data=payload, headers=headers)
            print(f"    Status Code: {res_post.status_code}")
            print(f"    Response: {res_post.text.strip()}")

            # Αν η απάντηση περιέχει success ή redirection
            if "success" in res_post.text.lower() or "ok" in res_post.text.lower() or res_post.status_code == 302:
                print(f"    [+] ΕπιΤο πρόβλημα βρίσκεται στην απόκριση που λαμβάνεις από τον server:

```json
{"msg":"accesso_negato"}
