import os
import sys
from bs4 import BeautifulSoup
from curl_cffi import requests

# Ανάκτηση Secrets
EMPORIO_EMAIL = os.getenv("EMPORIO_EMAIL")
EMPORIO_PASSWORD = os.getenv("EMPORIO_PASSWORD")

def test_login():
    if not EMPORIO_EMAIL or not EMPORIO_PASSWORD:
        print("[!] ERROR: Δεν βρέθηκαν τα EMPORIO_EMAIL / EMPORIO_PASSWORD στα secrets.")
        sys.exit(1)

    print(f"[*] Εκκίνηση δοκιμής Login για το χρήστη: {EMPORIO_EMAIL}")
    
    # Δημιουργία session με εξαιρετικά πιστή προσομοίωση Chrome 120
    session = requests.Session(impersonate="chrome120")

    home_url = "https://www.emporiorologion.gr/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://www.emporiorologion.gr',
        'Referer': home_url,
    }

    try:
        # 1. Αρχική επίσκεψη για λήψη session cookies
        print("[*] 1. Αίτημα στην αρχική σελίδα για cookies...")
        res_get = session.get(home_url)
        print(f"    Status Code: {res_get.status_code}")
        print(f"    Initial Cookies: {session.cookies.get_dict()}")

        soup = BeautifulSoup(res_get.text, 'html.parser')

        # 2. Εντοπισμός της φόρμας στο login modal
        modal_form = soup.select_one('#login-modal form')
        
        post_url = "https://www.emporiorologion.gr/index.php?route=account/login/login"
        payload = {
            'login_username': EMPORIO_EMAIL,
            'login_password': EMPORIO_PASSWORD,
        }

        if modal_form:
            print("[*] 2. Βρέθηκε το φόρμα στο #login-modal.")
            action = modal_form.get('action')
            if action:
                post_url = action if action.startswith('http') else f"https://www.emporiorologion.gr/{action.lstrip('/')}"
            
            # Συλλογή τυχόν hidden πεδίων (π.χ. CSRF tokens)
            for hidden in modal_form.select('input[type="hidden"]'):
                name = hidden.get('name')
                val = hidden.get('value', '')
                if name:
                    payload[name] = val
                    print(f"    Hidden field found: {name} = {val}")

        print(f"[*] 3. Αποστολή POST στο: {post_url}")
        print(f"    Payload keys: {list(payload.keys())}")

        # 3. Εκτέλεση POST Request
        res_post = session.post(post_url, data=payload, headers=headers)
        print(f"    POST Response Status: {res_post.status_code}")
        print(f"    POST Response Text (πρώτοι 300 χαρακτήρες):\n    {res_post.text[:300]}")

        # 4. Έλεγχος αν είμαστε πλέον συνδεδεμένοι
        print("[*] 4. Έλεγχος κατάστασης σύνδεσης...")
        res_check = session.get(home_url)
        check_text = res_check.text.lower()

        if "route=account/logout" in check_text or "αποσύνδεση" in check_text or "my account" in check_text:
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
