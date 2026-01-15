# Django-MPESA (Daraja 3.0 Ready)

This project is a comprehensive reference implementation for integrating **Safaricom's M-Pesa (Daraja) APIs** into a Django application. 

It was built to solve common issues developers face when creating custom Daraja API integrations, providing a clean, working example of how to authenticate and process transactions correctly.

> **Note:** The included HTML templates and UI are primarily for demonstration purposes—to give you a clean visual interface for testing the API interactions. You can strip the backend logic (especially from `views.py` and `credentials.py`) and reuse the functions **exactly as they are** in your own projects, whether they are API-only backends or full-stack applications.

---

## 🌟 Key Features

*   **Daraja 3.0 Compatible**: Tested and working with the latest Safaricom Daraja API standards.
*   **Plug-and-Play Logic**: The core functions for Token Generation and STK Push are modular. You can copy-paste them directly into your own codebase.
*   **Secure**: Uses environment variables to manage sensitive credentials (Consumer Key, Secret, Passkey).
*   **Zero Bloat**: Avoids heavy third-party wrappers like `django-daraja` in favor of direct, transparent `requests` calls, giving you full control over the data flow.
*   **Real-world Error Handling**: Includes handling for common pitfalls like invalid tokens, timeouts, and connection errors.

---

## 🚀 Prerequisites

Before you start, make sure you have:

*   **Python 3.9+**
*   **Django** installed
*   **Virtualenv** (recommended)
*   **requests** library (`pip install requests`)
*   A **Safaricom Developer Account** with API credentials:
    *   `CONSUMER_KEY`
    *   `CONSUMER_SECRET`
    *   Shortcode (Paybill/Till Number)
    *   Passkey
    *   Fully activated API product (for Production)

---

## 🔧 Setup

1.  **Clone the repo**

    ```bash
    git clone <your-repo-url>
    cd Django-MPESA
    ```

2.  **Create and activate a virtual environment**

    ```bash
    python -m venv venv
    source venv/bin/activate   # Linux/Mac
    venv\Scripts\activate      # Windows
    ```

3.  **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```
    *Alternatively, just install the essentials:*
    ```bash
    pip install django requests python-decouple
    ```

4.  **Configure environment variables**
    Create a `.env` file in the project root:

    ```ini
    CONSUMER_KEY=your_consumer_key
    CONSUMER_SECRET=your_consumer_secret
    MPESA_SHORT_CODE=your_shortcode
    MPESA_PASSKEY=your_passkey
    MPESA_CALLBACK_URL=https://yourdomain.com/callback
    ENV=sandbox   # or production
    ```

5.  **Run migrations and start the server**

    ```bash
    python manage.py migrate
    python manage.py runserver
    ```

---

## ⚡ Usage

Once the server is running (usually at `http://127.0.0.1:8000`):

1.  **Generate Token**: Navigate to the Token page to see how OAuth tokens are generated and retrieved.
2.  **STK Push**: Go to the Pay page, enter a phone number and amount, and trigger a real-time STK Push to your phone.
3.  **Code Reuse**: Open `stkpush/views.py`. You will find the `pay` and `token` functions. The logic inside these views (headers, payload construction, request handling) is what you need for your own project.

---

## 🛡️ Sandbox vs Production

*   **Sandbox**: Use the test credentials from the Safaricom Developer Portal. Transactions here are simulated.
*   **Production**: Requires activation by Safaricom. Ensure all your credentials, callback URLs, and IPN setup are correct.

> **Tip**: If you encounter `Error 404.001.03: Invalid Access Token` in production, it often means your app isn't fully live on Safaricom's side, or you are using Sandbox credentials on the Production URL.

---

## 🤝 Contributing

Feel free to fork this project and submit pull requests if you find ways to improve the implementation or add support for more M-Pesa APIs (like C2B or B2C).