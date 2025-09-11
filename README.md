# Django-MPESA

This project demonstrates how to integrate **Safaricom M-Pesa APIs** into a Django project. It provides ready-to-use examples for generating OAuth tokens and initiating STK push requests, while keeping credentials secure via environment variables.

---

## 🚀 Prerequisites

Before you start, make sure you have:

* **Python 3.9+**
* **Django** installed
* **Virtualenv** (recommended)
* **requests** library (`pip install requests`)
* A **Safaricom Developer Account** with API credentials:

  * `CONSUMER_KEY`
  * `CONSUMER_SECRET`
  * Shortcode, Passkey, and other required details

⚠️ **Note**: Your M-Pesa API product must be **fully activated** by Safaricom. If production access fails with errors like:

```
Error 404.001.03: Invalid Access Token
```

…it could be a configuration or activation issue. Contact **[apisupport@safaricom.co.ke](mailto:apisupport@safaricom.co.ke)** if this persists.

---

## 🔧 Setup

1. **Clone the repo**

   ```bash
   git clone <your-repo-url>
   cd Django-MPESA
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```
   or otherwise just install requests and decouple config for environment variables

   ```bash
   pip install requests decouple-config
   ```

4. **Configure environment variables**
   Create a `.env` file in the project root:

   ```ini
   CONSUMER_KEY=your_consumer_key
   CONSUMER_SECRET=your_consumer_secret
   SHORTCODE=your_shortcode
   PASSKEY=your_passkey
   CALLBACK_URL=https://yourdomain.com/callback
   ENV=sandbox   # or production
   ```

   * Use `sandbox` for testing
   * Switch to `production` when going live

5. **Run migrations and start the server**

   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

---

## ⚡ Usage

Once the server is running, you can:

* **Generate OAuth Tokens**
  Visit the relevant endpoint in the project to view how tokens are generated.

* **Initiate an STK Push**
  Trigger an STK push from the terminal or via API calls.

* **Explore the Docs**
  Check the included docs for detailed API workflows (C2B, B2C, Balance, Reversal, etc.).

---

## 🛡️ Sandbox vs Production

* **Sandbox**: Use the test credentials from the Safaricom Developer Portal. Transactions here are simulated.
* **Production**: Requires activation by Safaricom. Ensure all your credentials, callback URLs, and IPN setup are correct.

If you face persistent errors in production, especially with tokens or transactions, confirm that your product is activated. Contact **[apisupport@safaricom.co.ke](mailto:apisupport@safaricom.co.ke)** for unresolved issues.

---

## 🛠️ Development Notes

This project avoids external packages like `django-daraja` for simplicity. Instead, it uses the `requests` package to make direct API calls.

If you want to start a new Django project manually:

```bash
django-admin startproject PROJECT_NAME
django-admin startapp APP_NAME
```

Then, add your app to `INSTALLED_APPS` in `settings.py` and configure your URLs.

---

## Summary

* Clone → Setup venv → Configure `.env` → Run server
* Sandbox works immediately
* Production requires full activation
* Use docs to test tokens, STK push, and other APIs
* Contact Safaricom support if production setup fails
