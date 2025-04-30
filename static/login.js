function onload() {
    loginBtn = document.getElementById("loginBtn");
    loginBtn.addEventListener("click", loginClick);
}

async function loginClick(){
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    if (!confirmCredentials(username, password)){
        alert("Invalid username or password");
        return;
    }
    let loginStatus = verifyUser(username, password);
    if (loginStatus) {
        console.log("Login successful");
        setTimeout(() => {
            window.location.href = "/booking";
        }, 1500);
    }

}
function verifyUser(username, password) {
    return fetch('/account/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.token) {
            localStorage.setItem("token", data.token);
            console.log("Token saved:", data.token);
            document.getElementById("loading-spinner").style.display = "block";
            return true;
        } else {
            alert(data.message);
            return false;
        }
    })
    .catch(err => {
        console.error("Login error:", err);
        return false;
    });
}


function confirmCredentials(username, password){
    return true;
}

document.addEventListener('DOMContentLoaded', onload);