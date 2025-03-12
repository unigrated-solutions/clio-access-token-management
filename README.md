# Clio Access Token Manager

This is a **web-based application** built with [NiceGUI](https://github.com/zauberzeug/nicegui) to manage API gateways and **generate, store, copy, and deauthorize access tokens**.

## 3/12/25 

- **New Version Released**: Previous version moved to flask_version/
- **Cleaner Interface**: Single page application that can be easily added to
- **Simple Execution**: All the core functionality is contained in app.py

## 🚀 Features

- **Manage API Gateways**: Add, edit, and remove API gateway credentials.
- **OAuth2 Authentication**: Securely obtain access tokens via Clio’s authorization flow.
- **Access Token Management**:
  - View and manage stored tokens.
  - **Copy tokens to clipboard** for quick usage.
  - **Deauthorize tokens before deletion** to maintain security.
- **Persistent Storage**: Uses NiceGUI's built-in storage to keep API keys and tokens.

## 📦 Installation

### **1️⃣ Clone the Repository**
```sh
git clone https://github.com/yourusername/clio-access-token-manager.git
cd clio-access-token-manager
```

### **2️⃣ Create a Virtual Environment (Optional)**
```sh
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### **3️⃣ Install Dependencies**
```sh
pip install nicegui httpx
```

### **4️⃣ Run the Application**
```sh
python app.py
```

The app should be accessible at **[http://127.0.0.1:8080](http://127.0.0.1:8080)**.

## Security Notice

- **Access Tokens**
   - Tokens are not encrypted and are stored in .nicegui/storage-general.json
   - Refresh tokens are NOT stored for this reason
   - Tokens are valid for 30 days so deauthorize them when you're done 
   
## 🔑 OAuth2 Setup
1. Register your application with **Clio** to obtain:
   - `client_id`
   - `client_secret`
   - `redirect_uri` (must match **http://127.0.0.1:8080/callback**)
   
2. Once set up, use the **"Create Access Token"** button to initiate the authorization process.

## 🔄 How to Use
1. **Add API Gateways**: Input `Name`, `Client ID`, and `Client Secret`.
2. **Generate Tokens**:
   - Select a gateway and click **"Create Access Token"**.
   - The app will redirect to Clio’s authentication page.
   - Upon successful authorization, the token is stored in the **Access Tokens** page.
3. **Manage Tokens**:
   - **Copy Token**: Click **"Copy Token"** to copy it to the clipboard.
   - **Export Token**: Click **"Export Token"** to download it as a JSON file.
   - **Deauthorize Token**: Click **"Deauthorize Token"** to remove it from Clio before deleting.

## 🛠️ Built With
- **[NiceGUI](https://github.com/zauberzeug/nicegui)** - The UI framework for building modern web apps in Python.
- **FastAPI** - Provides backend API routes for OAuth2 handling.
- **httpx** - Used for making async HTTP requests.

## 📜 License
This project is licensed under the **MIT License**.

## 🙌 Credits
This app is built using **[NiceGUI](https://nicegui.io/)**.  
Special thanks to the [NiceGUI developers](https://github.com/zauberzeug/nicegui) for creating an amazing Python-based UI framework.
