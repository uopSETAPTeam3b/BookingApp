import { checkLoggedInExpt } from "./nav.js";

function addBookVectors() {
  const container = document.querySelector(".book-vectors");
  container.innerHTML = "";
  const numVectors = 15;
  const svg = `
      <svg width="50" height="50" viewBox="0 0 24 24" fill="none" stroke="var(--accent-color)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/>
      </svg>
    `;

  for (let i = 0; i < numVectors; i++) {
    const vector = document.createElement("div");
    vector.innerHTML = svg;
    vector.className = "book-vector";
    vector.style.position = "absolute";
    vector.style.zIndex = "1";
    vector.style.opacity = "0.3";
    vector.style.transform = `rotate(${Math.random() * 360}deg)`;
    vector.style.pointerEvents = "none";

    const maxX = window.innerWidth - 50;
    const maxY = window.innerHeight - 50;
    vector.style.left = `${Math.random() * maxX}px`;
    vector.style.top = `${Math.random() * maxY}px`;

    container.appendChild(vector);
  }
}

const themeSwitch = document.getElementById("theme-switch");
if (themeSwitch) {
  themeSwitch.addEventListener("click", (event) => {
    event.stopPropagation();
    document.documentElement.classList.toggle("darkmode");
    localStorage.setItem(
      "theme",
      document.documentElement.classList.contains("darkmode") ? "dark" : "light"
    );
  });
}

if (localStorage.getItem("theme") === "dark") {
  document.documentElement.classList.add("darkmode");
}

window.addEventListener("DOMContentLoaded", async () => {
  const loggedIn = await checkLoggedInExpt();
  console.log("Logged in status:", loggedIn);
  if (loggedIn) {
    document.getElementById("logged-out").style.display = "none";
    return;
  }
  document.getElementById("logged-out").style.display = "block";
  addBookVectors();
  window.addEventListener("resize", addBookVectors);
  document.querySelectorAll(".button").forEach((button) => {
    button.addEventListener("click", () =>
      console.log(`${button.textContent} button clicked`)
    );
  });
});
