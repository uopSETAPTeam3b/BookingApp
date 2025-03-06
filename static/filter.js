let filterbutton = document.querySelector("button#expand-filter");

filterbutton.addEventListener("click", () => {
    let filterbox = document.querySelector("section#filter");
    filterbox.classList.toggle("hidden");
});