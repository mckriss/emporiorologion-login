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
    home_url = f"{base_url}/"

    # Headless Browser Headers για παράκαμψη CDN/WAF
    common_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'el-GR,el;q=0.9,en-US;q=0.8,en;q=0.7',
        'Origin': base_url,
        'Referer': home_url,
    }

    try:
        # 1. Αρχικό GET για Session Cookies
        print("[*] 1. Αίτημα στην αρχική σελίδα για cookies...")
        res_get = session.get(home_url, headers=common_headers)
        print(f"    Status Code: {res_get.status_code}")
        print(f"    Initial Cookies: {session.cookies.get_dict()}")

        soup = BeautifulSoup(res_get.text, 'html.parser')

        # 2. AJAX Login Attempt (Modal Form)
        print("\n[*] 2. Δοκιμή AJAX Login (#login-modal)...")
        ajax_headers = common_headers.copy()
        ajax_headers.update({
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        })

        ajax_payload = {
            'login_username': EMPORIO_EMAIL,
            'login_password': EMPORIO_PASSWORD
        }

        ajax_url = f"{base_url}/index.php?route=account/login/login"
        res_ajax = session.post(ajax_url, data=ajax_payload, headers=ajax_headers)
        
        print(f"    AJAX Response Status: {res_ajax.status_code}")
        print(f"    AJAX Response Text: {res_ajax.text[:300]}")

        # 3. Standard Form Login Attempt (Fallback)
        print("\n[*] 3. Δοκιμή Standard Form Login...")
        std_headers = common_headers.copy()
        std_headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'

        std_payload = {
            'email': EMPORIO_EMAIL,
            'password': EMPORIO_PASSWORD
        }

        std_url = f"{base_url}/index.php?route=account/login"
        res_std = session.post(std_url, data=std_payload, headers=std_headers, allow_redirects=True)
        print(f"    Standard POST Response Status: {res_std.status_code}")

        # 4. Έλεγχος κατάστασης σύνδεσης
        print("\n[*] 4. Έλεγχος αν δημιουργήθηκε authenticated session...")
        res_check = session.get(home_url, headers=common_headers)
        check_text = res_check.text.lower()

        if any(keyword in check_text for keyword in ["route=account/logout", "αποσύνδεση", "εξόδος", "my account"]):
            print("\n[SUCCESS] Το Login πέτυχε απόλυτα!")
            return True
        else:
            print("\n[FAIL] Το Login απέτυχε. Ο server δεν διατήρησε το authenticated session.")
            return False

    except Exception as e:
        print(f"[!] Σφάλμα: {e}")
        return False

if __name__ == "__main__":
    test_login()
