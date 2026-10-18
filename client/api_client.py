import os
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

        response = requests.get(f"{SERVER_URL}/scores/top")
        if response.status_code == 200:
            top_data = response.json()
            
            rows_html = ""
            for i, entry in enumerate(top_data[:10], 1):
                row_class = ' class="first"' if i == 1 else ""
                rows_html += f'        <tr{row_class}><td>{i}</td><td>{entry["player"]}</td><td>{entry["score"]}</td></tr>\n'

            if os.path.exists("web/leaderboard.html"):
                with open("web/leaderboard.html", "r", encoding="utf-8") as html_file:
                    content = html_file.read()

                start_tag = "<table>\n        <tr><th>#</th><th>Spēlētājs</th><th>Punkti</th></tr>"
                end_tag = "    </table>"

                if start_tag in content and end_tag in content:
                    before_table = content.split(start_tag)[0]
                    after_table = content.split(end_tag)[1]

                    new_table = f"{start_tag}\n        <!-- TABLE_ROWS -->\n{rows_html}{end_tag}"
                    final_html = before_table + new_table + after_table

                    with open("web/leaderboard.html", "w", encoding="utf-8") as html_file:
                        html_file.write(final_html)
    except Exception as e:
        print(f"Kļūda saziņā ar serveri: {e}")