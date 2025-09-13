from flask import Flask, request
import sqlite3
import logging
import requests
from datetime import datetime

app = Flask(__name__)

# Configure logging
logging.basicConfig(filename="honeypot.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# Database setup
def init_db():
    conn = sqlite3.connect("honeypot.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            ip TEXT,
            location TEXT,
            isp TEXT,
            endpoint TEXT,
            user_agent TEXT,
            payload TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Get IP address (supporting ngrok / proxies)
def get_client_ip():
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # ngrok/proxies may send multiple IPs, take the first one
        ip = forwarded.split(",")[0].strip()
    else:
        ip = request.remote_addr
    return ip

# Get location from IP
def get_ip_info(ip):
    try:
        if ip.startswith("127.") or ip == "localhost":
            return "Localhost", "Local Network"
        response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
        data = response.json()
        location = f"{data.get('city', 'Unknown')}, {data.get('country', 'Unknown')}"
        isp = data.get('org', 'Unknown ISP')
        return location, isp
    except:
        return "Unknown", "Unknown ISP"

# Detect attack patterns
def is_attack(payload):
    payload = payload.lower()
    attack_signatures = ["'", "--", ";", "<script>", " or ", " and ", "="]
    return any(sig in payload for sig in attack_signatures)

# Log attack attempts
def log_attack(endpoint, user_agent, payload):
    ip = get_client_ip()
    if is_attack(payload):
        location, isp = get_ip_info(ip)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"Attack detected! {timestamp} | IP: {ip} ({location}, {isp}), Endpoint: {endpoint}, Payload: {payload}")
        conn = sqlite3.connect("honeypot.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO logs (timestamp, ip, location, isp, endpoint, user_agent, payload) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (timestamp, ip, location, isp, endpoint, user_agent, payload)
        )
        conn.commit()
        conn.close()

# Vulnerable-looking login page
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        user_agent = request.headers.get("User-Agent", "Unknown")
        payload = f"username={username}&password={password}"
        
        # Log suspicious attempts
        log_attack("/", user_agent, payload)

        # Fake vulnerable SQL output
        fake_sql = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}';"
        return f"""
        <h3>Login Failed</h3>
        <p>Error: invalid credentials</p>
        <p><b>Debug:</b> Executed query: {fake_sql}</p>
        """, 403

    return """
    <html>
    <head><title>Member Login</title></head>
    <body>
        <h2>Member Login</h2>
        <form method="POST">
            <label>Username:</label><br>
            <input type="text" name="username"><br><br>
            <label>Password:</label><br>
            <input type="password" name="password"><br><br>
            <input type="submit" value="Login">
        </form>
    </body>
    </html>
    """

# View logs
@app.route("/logs", methods=["GET"])
def view_logs():
    conn = sqlite3.connect("honeypot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logs ORDER BY id DESC")
    logs = cursor.fetchall()
    conn.close()

    output = "<pre>ID | Timestamp | IP | Location | ISP | Endpoint | User Agent | Payload\n"
    output += "-" * 120 + "\n"
    for log in logs:
        output += " | ".join(map(str, log)) + "\n"
    output += "</pre>"
    return output

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
