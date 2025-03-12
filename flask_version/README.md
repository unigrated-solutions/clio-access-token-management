
# OAuth Token Management Application

This application provides a web interface to manage OAuth tokens for an API. Users can create new tokens, renew existing tokens, and deauthorize them through a user-friendly interface.

---

## Features

- **Create Tokens**: Start the OAuth authorization process to obtain new access and refresh tokens.
- **Renew Tokens**: Use a refresh token to generate a new access token when the existing one expires.
- **Deauthorize Tokens**: Revoke an access token to disable its authorization.

---

## Prerequisites

Before running the application, ensure you have the following installed:

- **Python**: Version 3.7 or higher
- **pip**: Python package manager

---

## Setup and Usage

Follow these steps to set up, configure, and run the application:

### Step 1: Clone the Repository
Clone the repository to your local machine:
```bash
git clone <repository-url>
cd <repository-directory>
```

### Step 2: Set Up the Environment
1. **Create a Python Virtual Environment** (Optional but Recommended):
   ```bash
   python -m venv venv
   # Activate the environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Rename `.env.example` to `.env`**:

---

### Step 3: Run the Application
1. **Set Environment Variables**:
   ```bash
   export FLASK_APP=app.py  # On Windows: set FLASK_APP=main.py
   export FLASK_ENV=development  # On Windows: set FLASK_ENV=development
   ```

2. **Start the Flask Server**:
   ```bash
   flask run
   ```
   The application will start and be accessible at `http://127.0.0.1:5000`.

---

### Step 4: Using the Application

#### **1. Create a New Token**
- Visit the root route (`http://127.0.0.1:5000/`).
- If required variables (`CLIENT_ID` and `CLIENT_SECRET`) are missing, you will be prompted to set them via a form.
- Click the "Create New Token" button to start the OAuth authorization process.
- Follow the redirection to the authorization provider, authorize the application, and return to the callback page.

#### **2. Renew a Token**
- If a refresh token is available, you can use it to generate a new access token.
- Click the "Renew Token" button on the token management interface.

#### **3. Deauthorize a Token**
- To revoke an access token, click the "Deauthorize Token" button.
- The application will send a request to the deauthorization endpoint specified in the `.env` file.

---

### Troubleshooting

1. **Environment Variables Not Loading**:
   - Ensure the `.env` file is in the root directory.
   - Ensure the `python-dotenv` package is installed.

2. **Server Not Running**:
   - Verify Python and Flask are correctly installed.
   - Use `flask --debug run` to check for additional errors.

3. **Authorization Errors**:
   - Verify the `AUTH_BASE_URL`, `TOKEN_URL`, and `DEAUTHORIZE_URL` are correct.
   - Ensure the `CLIENT_ID` and `CLIENT_SECRET` are valid.

---

## Contributing

Feel free to submit issues and pull requests for improvements or new features.

---

## License

This project is licensed under the MIT License.
