import {renderBookingTable} from "./book.js"

// Filtering Logic
export function applyFilters(rooms, bookings) {
    const lengthValue = parseInt(document.getElementById('lengthRange').value);
    const fromValue = parseInt(document.getElementById('fromToRange').value);
    if (fromValue === -1 || isNaN(fromValue)) return rooms;

    const toValue = fromValue + lengthValue;
    if (toValue > 24) return [];

    const bookedSet = new Set(bookings.map(b => `${b.room}-${b.time}`));
    return rooms.filter(room => {
        for (let t = fromValue; t < toValue; t++) {
            if (bookedSet.has(`${room}-${t}`)) return false;
        }
        return true;
    });
}

// Filter Toggle & Reset From Hour
let filterbutton = document.querySelector("button#expand-filter");
filterbutton.addEventListener("click", () => {
    const filterbox = document.querySelector("section#filter");
    const fromSlider = document.getElementById("fromToRange");

    const nowHidden = filterbox.classList.toggle("hidden");

    // Reset 'From' when filter opens
    if (!nowHidden) {
        fromSlider.value = -1;
        document.getElementById('fromToDisplay').innerText = "Select Time";
    }
});

export function updateLengthDisplay(value) {
    document.getElementById('lengthDisplay').innerText = value + " Hour" + (value > 1 ? "s" : "");
    renderBookingTable();
}

export function updateFromToDisplay(value) {
    const display = document.getElementById('fromToDisplay');
    if (parseInt(value) === -1) {
        display.innerText = "Select Time";
        return;
    }
    display.innerText = value + ":00";
    renderBookingTable();
}

export function initFilters() {
    updateLengthDisplay(document.getElementById('lengthRange').value);
    updateFromToDisplay(document.getElementById('fromToRange').value);
    
    document.querySelector("#fromToRange").addEventListener("input", (e) => {
        updateFromToDisplay(e.target.value);
    });
    document.querySelector("#lengthRange").addEventListener("input", (e) => {
        updateLengthDisplay(e.target.value);
    })
}
