function onload() {
    loginBtn = document.getElementById("loginBtn");
    loginBtn.addEventListener("click", loginClick);
}

async function loginClick(){
    
    const username = document.getElementById("email_input").value;
    const password = document.getElementById("password_input").value;
    if (!confirmCredentials(username, password)){
        alert("Invalid username or password");
        return;
    }

    let loginStatus = await verifyUser(username, password);
    console.log("Login status:", loginStatus);
    alert("Login status: " + loginStatus);
    if (loginStatus) {
        console.log("Login successful");
        alert("Login successful");
        setTimeout(() => {
            
            window.location.href = "/booking";
        }, 1500);
    }

}
async function verifyUser(username, password) {
    try {
        const response = await fetch('/account/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        console.log("Response status:", response.status);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log("Data received:", data);

        // Check if data is empty or token is missing
        if (data && data.token) {
            localStorage.setItem("token", data.token);
            console.log("Token saved:", data.token);
            return true;
        } else {
            alert("Login failed: " + (data.message || "No token received"));
            return false;
        }
    } catch (err) {
        console.error("Login error:", err);
        alert("Login error: " + err.message);
        return false;
    }
}


function confirmCredentials(username, password){
    return true;
}

document.addEventListener('DOMContentLoaded', onload);