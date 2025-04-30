function onload() {
    loginBtn = document.getElementById("loginBtn");
    loginBtn.addEventListener("click", loginClick);
}

async function loginClick(){
    console.log("Login button clicked");
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    if (!confirmCredentials(username, password)){
        alert("Invalid username or password");
        return;
    }
    console.log("Username: " + username);
    let loginStatus = verifyUser(username, password);
    if (loginStatus) {
        console.log("Login successful");
    }

}
function verifyUser(username, password){
    console.log("Verifying user...");
    fetch('/account/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({username: username, password: password})
    })
    .then(response => response.json())
    .then(data => {
        if (data.token) {
            console.log("Login successful, token:", data.token);
            // Store the token securely (e.g., localStorage or cookies)
        } else {
            console.error("Login failed:", data.message);
            alert(data.message);  // Display the error message to the user
        }
    })
    const token = data.token;
    
    localStorage.setItem("token", token);
};

function confirmCredentials(username, password){
    return true;
}

document.addEventListener('DOMContentLoaded', onload);