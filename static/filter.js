// Filtering Logic
function applyFilters(rooms, bookings) {
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

function filterTable() {
    const fromValue = parseInt(document.getElementById('fromToRange').value);
    const allRooms = ["1.0", "2.0", "3.0", "4.0", "5.0", "6.0", "7.0", "8.0", "9.0"];

    if (fromValue === -1 || isNaN(fromValue)) {
        // Show all rooms with bookings (no filter applied yet)
        renderBookingTable(allRooms, bookings);
    } else {
        const filteredRooms = applyFilters(allRooms, bookings);
        renderBookingTable(filteredRooms, bookings);
    }
}
renderBookingTable(["1.0", "2.0", "3.0", "4.0", "5.0", "6.0", "7.0", "8.0", "9.0"], bookings);
filterTable(); // Apply filter after table is rendered

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

function updateLengthDisplay(value) {
    document.getElementById('lengthDisplay').innerText = value + " Hour" + (value > 1 ? "s" : "");
    filterTable();
}

function updateFromToDisplay(value) {
    const display = document.getElementById('fromToDisplay');
    if (parseInt(value) === -1) {
        display.innerText = "Select Time";
        return;
    }
    display.innerText = value + ":00";
    filterTable();
}