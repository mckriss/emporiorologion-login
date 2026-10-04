import os
import sys
import json
from bs4 import BeautifulSoup
from curl_cffi import requests

EMPORIO_EMAIL = os.getenv("EMPORIO_EMAIL")
EMPORIO_PASSWORD = os.getenv("EMPORIO_PASSWORD")

def test_login():
    if not EMPORIO_EMAIL or not EMPORIO_PASSWORD:
        print("[!] ERROR: Δεν βρέθηκαν τα EMPORIO_EMAIL / EMPORIO_PASSWORD στα secrets.")
        sys.exit(1)

    print(f"[*] Εκκίνηση δοκιμής Login για τον χρήστη: {EMPORIO_EMAIL}")
    
    session = requests.Session(impersonate="chrome120")
    base_url = "https://www.emporiorologion.gr"

    # Strict Browser Headers για να εξομοιώσουμε το πάτημα του κουμπιού #form_login
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
        # 1. Αρχικό GET για να πάρουμε το PHPSESSID cookie
        print("[*] 1. Αίτημα στην αρχική σελίδα για cookies...")
        res_get = session.get(f"{base_url}/")
        print(f"    Initial Cookies: {session.cookies.get_dict()}")

        # Payload με τα ακριβή IDs/Names της φόρμας σου
        payload = {
            'login_username': EMPORIO_EMAIL,
            'login_password': EMPORIO_PASSWORD,
            'username': EMPORIO_EMAIL,
            'password': EMPORIO_PASSWORD,
            'email': EMPORIO_EMAIL
        }

        # 2. Δοκιμή στο 1ο πιθανό AJAX endpoint
        endpoint_1 = f"{base_url}/index.php?route=account/login/login"
        print(f"\n[*] 2. Αποστολή AJAX POST στο {endpoint_1}...")
        res_post1 = session.post(endpoint_1, data=payload, headers=headers)
        print(f"    Status: {res_post1.status_code}")
        print(f"    Response: {res_post1.text[:200]}")

        # 3. Επαλήθευση αν άνοιξε το Session
        check_headers = {
            'User-Agent': headers['User-Agent'],
            'Referer': f"{base_url}/"
        }
        res_check = session.get(f"{base_url}/index.php?route=account/account", headers=check_headers)
        
        if any(term in res_check.text.lower() for term in ["route=account/logout", "αποσύνδεση", "εξόδος", "my account"]):
            print("\n[SUCCESS] Το Login πέτυχε απόλυτα!")
            return True

        # 4. Αν απέτυχε, δοκιμή στο 2ο πιθανό endpoint (Module Login)
        endpoint_2 = f"{base_url}/index.php?route=module/account/login"
        print(f"\n[*] 3. Δοκιμή στο εναλλακτικό endpoint: {endpoint_2}...")
        res_post2 = session.post(endpoint_2, data=payload, headers=headers)
        print(f"    Status: {res_post2.status_code}")
        print(f"    Response: {res_post2.text[:200]}")

        # Τελικός έλεγχος
        res_check_final = session.get(f"{base_url}/index.php?route=account/account", headers=check_headers)
        if any(term in res_check_final.text.lower() for term in ["route=account/logout", "αποσύνδεση", "εξόδος", "my account"]):
            print("\n[SUCCESS] Το Login πέτυχε απόλυτα στο 2ο endpoint!")
            return True
        else:
            print("\n[FAIL] Απέτυχε η σύνδεση. Ο server δεν κράτησε το Session.")
            return False

    except Exception as e:
        print(f"[!] Σφάλμα: {e}")
        return False

if __name__ == "__main__":
    test_login()
