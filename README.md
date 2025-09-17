# Simple Flask Web Honeypot

A lightweight, simple-to-deploy web honeypot built with Python and Flask. This application mimics a vulnerable login page to attract, detect, and log common web attack attempts like SQL Injection (SQLi) and Cross-Site Scripting (XSS).

## 📝 Overview

The primary goal of this project is to serve as a decoy for attackers. It presents a basic login interface that, upon submission, analyzes the input for malicious patterns. If a potential attack is identified, it logs detailed information about the request without ever being truly vulnerable to the attack itself.

## ✨ Features

* **Decoy Login Page**: A minimal HTML form that acts as the lure for attackers.
* **Attack Detection**: Identifies basic attack signatures for SQL Injection and XSS (e.g., `'`, `--`, `<`, `>`) in submitted payloads.
* **Detailed Logging**: Captures and stores the following information for each detected attempt:
    * Timestamp
    * Attacker's IP Address
    * Geolocation (City, Country)
    * ISP Information
    * User-Agent String
    * The exact payload submitted.
* **IP Geolocation**: Uses the `ipinfo.io` API to enrich IP address data with location and ISP details.
* **Dual Storage**: Saves logs to both a structured **SQLite database** (`honeypot.db`) and a plain text file (`honeypot.log`) for easy access and analysis.
* **Log Viewer**: A simple web endpoint (`/logs`) to view all captured attack logs directly from the browser.

## ⚙️ How It Works

1.  The Flask application starts a web server, accessible on `0.0.0.0:5000`.
2.  An attacker visits the root URL (`/`) and is presented with a standard username/password login form.
3.  The attacker submits a malicious payload (e.g., username `admin'--`) to try and bypass the login.
4.  The application receives the POST request. Instead of processing the login, it checks the payload against a list of known attack signatures.
5.  If a signature is matched, the application retrieves the attacker's IP, gets location details from `ipinfo.io`, and logs everything to `honeypot.db` and `honeypot.log`.
6.  The attacker is shown a generic "Login Failed" message, keeping them unaware that their actions have been logged.

## 🚀 Getting Started

Follow these instructions to get the honeypot up and running on your local machine.

### Prerequisites

* Python 3.x
* pip (Python package installer)

### Installation & Setup

1.  **Clone the repository:**
    ```sh
    git clone <your-repository-url>
    cd <your-repository-name>
    ```

2.  **Create and activate a virtual environment:**
    * **Windows:**
        ```sh
        python -m venv venv
        .\venv\Scripts\activate
        ```
    * **macOS / Linux:**
        ```sh
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Install the required dependencies:**
    It's recommended to create a `requirements.txt` file with the following content:
    ```txt
    Flask
    requests
    ```
    Then, install the dependencies from the file:
    ```sh
    pip install -r requirements.txt
    ```

### Running the Application

1.  **Start the Flask server:**
    ```sh
    python honeypot.py
    ```

2.  The server will start and listen for connections. You will see output like this:
    ```
     * Running on all addresses (0.0.0.0)
     * Running on [http://127.0.0.1:5000](http://127.0.0.1:5000)
    ```

## Usage

1.  **Access the Honeypot**: Open your web browser and navigate to `http://127.0.0.1:5000`.
2.  **Simulate an Attack**: Enter a malicious string into the username field, such as `admin'--` or `<script>alert(1)</script>`, and any password.
3.  **View the Logs**: After submitting the form, navigate to `http://127.0.0.1:5000/logs` to see the log entry for your attempt. The new log will also appear in the `honeypot.db` and `honeypot.log` files in the project directory.

## ⚠️ Disclaimer

This is a simple, educational honeypot intended for learning and observation purposes. It is **NOT** a production-ready security tool and should not be exposed to the public internet without significant hardening and security considerations.
