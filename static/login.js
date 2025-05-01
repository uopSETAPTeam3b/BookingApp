function onload() {
    loginBtn = document.getElementById("loginBtn");
    //loginBtn.addEventListener("click", loginClick);
    document.getElementById("login_form").addEventListener("submit", function (e) {
        e.preventDefault();
        loginClick(); 
      });
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

        const text = await response.text();
        const data = JSON.parse(text); 
    
        if (response.ok && data.token) {
            localStorage.setItem("token", data.token);
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