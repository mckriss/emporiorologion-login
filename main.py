import os
import sys
from bs4 import BeautifulSoup
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
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'el-GR,el;q=0.9,en-US;q=0.8,en;q=0.7',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': base_url,
        'Referer': f"{base_url}/",
    }

    try:
        # 1. Αρχικό GET στην αρχική σελίδα για ανάκτηση Cookies
        print("[*] 1. Αίτημα στην αρχική σελίδα...")
        res_get = session.get(f"{base_url}/", headers=headers)
        print(f"    Status: {res_get.status_code}")
        print(f"    Cookies: {session.cookies.get_dict()}")

        # 2. Αποστολή POST στο σωστό endpoint (/gr/login)
        payload = {
            'login_username': EMPORIO_EMAIL,
            'login_password': EMPORIO_PASSWORD,
        }

        print(f"\n[*] 2. Αποστολή POST στο {login_url}...")
        res_post = session.post(login_url, data=payload, headers=headers, allow_redirects=True)
        print(f"    Status Code: {res_post.status_code}")
        print(f"    Final URL: {res_post.url}")

        # 3. Έλεγχος αν δημιουργήθηκε authenticated session
        print("\n[*] 3. Επαλήθευση Session...")
        res_check = session.get(f"{base_url}/index.php?route=account/account", headers={'Referer': f"{base_url}/"})
        
        account_keywords = ["route=account/logout", "αποσύνδεση", "έξοδος", "my account", "ο λογαριασμός μου"]
        if any(kw in res_check.text.lower() for kw in account_keywords):
            print("\n[SUCCESS] Το Login πέτυχε απόλυτα!")
            return True
        else:
            print("\n[FAIL] Το Login απέτυχε. Ελέγξτε αν τα πεδία χρειάζονται διαφορετικά keys (π.χ. email/password).")
            print(f"    Preview σελίδας μετά το login: {res_post.text[:200].strip()}")
            return False

    except Exception as e:
        print(f"[!] Σφάλμα: {e}")
        return False

if __name__ == "__main__":
    test_login()
