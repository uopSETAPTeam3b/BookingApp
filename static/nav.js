function onload() {
    const homeButton = document.getElementById("homebutton");
    const bookButton = document.getElementById("bookbutton");
    const bookingsButton = document.getElementById("bookings");
    const loginButton = document.getElementById("loginout");

    homeButton.addEventListener("click", () => {
        window.location.href = "/home";
    });
    bookButton.addEventListener("click", () => {
        window.location.href = "/book";
    });
    bookingsButton.addEventListener("click", () => {
        window.location.href = "/booking";
    });
    loginButton.addEventListener("click", () => {
        window.location.href = "/login";
    });
}
document.addEventListener('DOMContentLoaded', onload);
