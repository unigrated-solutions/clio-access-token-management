function loadTokenFile(event) {
    const file = event.target.files[0];
    if (!file) {
        alert("No file selected.");
        return;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
        try {
            const tokenData = JSON.parse(e.target.result);
            const currentTime = Date.now();
            const remainingTime = Math.max(
                0,
                Math.floor((tokenData.created_at + tokenData.expires_in * 1000 - currentTime) / 1000)
            );
            const formattedTime = formatTime(remainingTime);

            // Populate token details
            document.getElementById('tokenType').value = tokenData.token_type || '';
            document.getElementById('accessToken').value = tokenData.access_token || '';
            document.getElementById('expiresIn').value = remainingTime > 0 ? formattedTime : 'Expired';
            document.getElementById('refreshToken').value = tokenData.refresh_token || '';

            // Enable action buttons
            document.getElementById('renewButton').disabled = !tokenData.refresh_token;
            document.getElementById('deauthorizeButton').disabled = !tokenData.access_token;

            // Show token details section
            document.getElementById('tokenDetails').style.display = 'block';

            alert("Token loaded successfully.");
        } catch (err) {
            alert("Error parsing token file: " + err.message);
        }
    };
    reader.readAsText(file);
}

function formatTime(seconds) {
    const days = Math.floor(seconds / (24 * 3600));
    seconds %= 24 * 3600;
    const hours = Math.floor(seconds / 3600);
    seconds %= 3600;
    const minutes = Math.floor(seconds / 60);
    seconds %= 60;
    return `${days}d ${hours}h ${minutes}m ${seconds}s`;
}

async function sendPostRequest(url, data) {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        if (response.ok) {
            alert("Success: " + JSON.stringify(result, null, 2));
        } else {
            alert("Error: " + JSON.stringify(result, null, 2));
        }
        return response; // Return the response object
    } catch (err) {
        alert("Error: " + err.message);
        throw err; // Rethrow the error to handle it in the calling function
    }
}

function renewToken() {
    const refreshToken = document.getElementById('refreshToken').value;
    if (!refreshToken) {
        alert("Please provide a refresh token.");
        return;
    }
    sendPostRequest('/refresh_token', { refresh_token: refreshToken });
}

async function deauthorizeToken() {
    const accessToken = document.getElementById('accessToken').value;
    if (!accessToken) {
        alert("Please provide an access token.");
        return;
    }

    try {
        const response = await sendPostRequest('/revoke_token', { token: accessToken });
        if (response.ok) {
            location.reload(); // Reload the page on success
        }
    } catch (err) {
        console.error("Error during deauthorization:", err);
    }
}

function toggleEdit() {
    const clientIdInput = document.getElementById('updateClientId');
    const clientSecretInput = document.getElementById('updateClientSecret');
    const appUriInput = document.getElementById('updateAppURI');
    const editButton = document.getElementById('editButton');
    const updateButton = document.getElementById('updateButton');

    if (editButton.innerText === 'Edit') {
        clientIdInput.disabled = false;
        clientSecretInput.disabled = false;
        appUriInput.disabled = false;
        updateButton.disabled = false;
        editButton.innerText = 'Cancel';
    } else {
        clientIdInput.disabled = true;
        clientSecretInput.disabled = true;
        appUriInput.disabled = true;
        updateButton.disabled = true;
        editButton.innerText = 'Edit';
    }
}
