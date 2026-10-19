import requests

SERVER_URL = "http://127.0.0.1:8000"

def register_and_login(player_name):
    try:
        requests.post(f"{SERVER_URL}/register", json={"name": player_name, "password": "123"})
        login_resp = requests.post(f"{SERVER_URL}/login", json={"name": player_name, "password": "123"})
        if login_resp.status_code == 200:
            return login_resp.json().get("token", "")
    except Exception:
        pass
    return ""

def send_score_to_server(player_token, final_score):
    try:
        if player_token:
            headers = {"token": player_token}
            requests.post(f"{SERVER_URL}/scores", json={"score": final_score}, headers=headers)
    except Exception as e:
        print(f"Kļūda saziņā ar serveri: {e}")