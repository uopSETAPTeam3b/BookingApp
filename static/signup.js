function onload() {
    loginBtn = document.getElementById("loginBtn");
    
    document.getElementById("form").addEventListener("submit", function (e) {
        e.preventDefault();
        signup(); 
      });
}
async function signup(){ 
    const firstname = document.getElementById("firstname-input").value;
    const email = document.getElementById("email-input").value;
    const password = document.getElementById("password-input").value;
    const repeatPassword = document.getElementById("repeat-password-input").value;

    if (!confirmCredentials(firstname, email, password, repeatPassword)){
        alert("Invalid credentials");
        return;
    }
    if (password !== repeatPassword) {
        alert("Passwords do not match");
        return;
    }
    try {
        const response = await fetch('/account/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const text = await response.text();
        const data = JSON.parse(text); 
    
        if (response.ok && data.token) {
            localStorage.setItem("token", data.token);
            return;
        } else {
            alert("signup failed: " + (data.message || "No token received"));
            return;
        }
    
    } catch (err) {
        console.error("signup error:", err);
        alert("signup error: " + err.message);
        return;
    }

    
    console.log("Signup status:", signupStatus);
    alert("Signup status: " + signupStatus);
    if (signupStatus) {
        setTimeout(() => {
            window.location.href = "/login";
        }, 1500);
    }
}
document.addEventListener('DOMContentLoaded', onload);