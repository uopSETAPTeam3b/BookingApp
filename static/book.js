 let bookings = [];

// Setup Date
let date = document.querySelector("#date");
date.valueAsDate = new Date();
date.min = new Date().toISOString().split("T")[0];

// Next & Previous Buttons
let next = document.querySelector("#next");
next.addEventListener("click", () => {
    date.stepUp();
    updateBookingTable();
});

let pre = document.querySelector("#pre");
pre.addEventListener("click", () => {
    if (new Date(date.value) < new Date().setHours(0, 0, 0, 0)) return;
    date.stepDown();
    updateBookingTable();
});

// Render Table
function renderBookingTable(rooms, bookings) {
    let table = document.getElementById("bookings-table");
    table.innerHTML = '';

    let header = document.createElement("tr");
    let room_header = document.createElement("th");
    room_header.textContent = "Room/Time";
    header.appendChild(room_header);

    for (let i = 0; i < 24; i++) {
        let time = document.createElement("th");
        time.textContent = `${i}:00`;
        header.appendChild(time);
    }
    table.appendChild(header);

    for (let room of rooms) {
        let row = document.createElement("tr");
        let room_name = document.createElement("th");
        room_name.textContent = room;
        row.appendChild(room_name);

        for (let i = 0; i < 24; i++) {
            let booking = document.createElement("td");
            let checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.checked = false;
            checkbox.disabled = false;
            checkbox.setAttribute("time", i);
            checkbox.setAttribute("room", room);
            booking.appendChild(checkbox);
            row.appendChild(booking);
        }
        table.appendChild(row);
    }

    for (let booking of bookings) {
        let checkbox = document.querySelector(`input[type="checkbox"][time="${booking.time}"][room="${booking.room}"]`);
        if (checkbox) {
            checkbox.disabled = true;
            checkbox.checked = true;
        }
    }
}

// Fetch and Update Bookings
async function updateBookingTable() {
    let response = await fetch("/booking/get_rooms", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ date: new Date(date.value).toString() })
    });

    const rooms = await response.json();

    response = await fetch("/booking/get_bookings_for_date", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ date: new Date(date.value).toString() })
    });

    bookings = await response.json();

    // Add fixed bookings (will persist before filtering)
    bookings = [
        ...bookings,
        { time: 11, room: "3.0" },
        { time: 12, room:"4.0" },
        { time: 9, room:"2.0" },
        {time: 14, room:"5.0" }
        
    ];

    // Render full unfiltered view initially
    renderBookingTable(["1.0", "2.0", "3.0", "4.0", "5.0", "6.0", "7.0", "8.0", "9.0"], bookings);
}






// Initialise
document.addEventListener('DOMContentLoaded', () => {
    updateBookingTable().then(() => {
        updateLengthDisplay(document.getElementById('lengthRange').value);
        updateFromToDisplay(document.getElementById('fromToRange').value);
    });
});
