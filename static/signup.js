function onload() {
  loginBtn = document.getElementById("loginBtn");

  document.getElementById("form").addEventListener("submit", function (e) {
    e.preventDefault();
    signup();
  });
}
async function signup() {
  const firstname = document.getElementById("firstname-input").value.trim();
  const email = document.getElementById("email-input").value.trim();
  const password = document.getElementById("password-input").value.trim();
  const repeatPassword = document
    .getElementById("repeat-password-input")
    .value.trim();

  if (!confirmCredentials(firstname, email, password, repeatPassword)) {
    return;
  }
  try {
    const response = await fetch("/account/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: email, password }),
    });

    const text = await response.text();
    const data = JSON.parse(text);
    const errorMessage = document.getElementById("error-message");
    if (response.ok && data.token) {
      localStorage.setItem("token", data.token);
      errorMessage.innerHTML =
        "Signup successful! Redirecting to login page...";
      setTimeout(() => {
        window.location.href = "/login";
      }, 1500);

      return;
    } else {
      errorMessage.innerHTML = "Email already exists!";

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
function confirmCredentials(firstname, email, password, repeatPassword) {
  const errorMessage = document.getElementById("error-message");
  if (firstname.length < 2) {
    errorMessage.innerHTML = "First name must be at least 2 characters long!";
    return false;
  }
  if (email.length < 3 || !email.includes("@")) {
    errorMessage.innerHTML =
      "Email must be at least 3 characters long and contain '@'";
    return false;
  }
  if (password.length < 8) {
    errorMessage.innerHTML = "Password must be at least 8 characters long";
    return false;
  }
  if (repeatPassword !== password) {
    errorMessage.innerHTML = "Passwords do not match";
    return false;
  }
  const values = [firstname, email, password, repeatPassword];
  const anyHasWhitespace = values.some((val) => /\s/.test(val));
  if (anyHasWhitespace) {
    errorMessage.innerHTML = "No whitespace allowed in any field";
    return false;
  }
  return true;
}
document.addEventListener("DOMContentLoaded", onload);
