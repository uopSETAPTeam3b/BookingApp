bookings = []

// Setup Date
let date = document.querySelector("#date")
date.valueAsDate = new Date();
date.min = new Date().toISOString().split("T")[0];

// Next Button
let next = document.querySelector("#next");
next.addEventListener("click", () => {
    let date = document.querySelector("#date")
    date.stepUp();
    updateBookingTable()
})

// Pre Button
let pre = document.querySelector("#pre");
pre.addEventListener("click", () => {
    let date = document.querySelector("#date")
    if (new Date(date.value) < new Date().setHours(0, 0, 0, 0)) return;
    date.stepDown();
    updateBookingTable()
})

async function updateBookingTable() {
    let table = document.getElementById("bookings-table")

    let date = document.querySelector("#date");
    
    let response = await fetch("/booking/get_rooms", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            date: new Date(date.value).toString()
        })
    })

    bookings = await response.json()
    // wait till after request to clear table to prevent flicker
    table.innerHTML = '';

    // Place the time headings onto the table
    let header = document.createElement("tr")
    let room_header = document.createElement("th")
    room_header.textContent = "Room/Time"
    header.appendChild(room_header)
    for (let i = 0; i < 24; i++) {
        let time = document.createElement("th")
        time.textContent = i.toString()
        header.appendChild(time)
    }
    table.appendChild(header)

    // Place the rooms and the checkboxes in the table
    for (let room of ["1.0", "2.0", "3.0", "4.0", "5.0", "6.0", "7.0", "8.0", "9.0"]) {
        let row = document.createElement("tr")
        room_name = document.createElement("th")
        room_name.textContent = room
        row.appendChild(room_name)
        for (let i = 0; i < 24; i++) {
            let booking = document.createElement("td")
            let checkbox = document.createElement("input")
            checkbox.type = "checkbox"
            checkbox.checked = false
            checkbox.disabled = false
            checkbox.setAttribute("time", i)
            checkbox.setAttribute("room", room)
            booking.appendChild(checkbox);
            row.appendChild(booking)
        }
        table.appendChild(row)
    }

    // Get bookings for current date
    response = await fetch("/booking/get_bookings_for_date", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            date: new Date(date.value).toString()
        })
    })

    bookings = await response.json()
    bookings = [
        {time: 11, room:"3.0"},
        {time: 12, room: "3.0"},
        {time: 13, room: "3.0"},
        {time: 14, room: "3.0"}
    ]


    // mark booked rooms
    for (let booking of bookings) {
        checkbox = document.querySelector(`input[type="checkbox"][time="${booking.time}"][room="${booking.room}"]`)
        checkbox.disabled = true
        checkbox.checked = true
    }
}

// Draw the table for the initial date
updateBookingTable()

let filterbutton = document.querySelector("button#expand-filter");

filterbutton.addEventListener("click", () => {
    let filterbox = document.querySelector("section#filter");
    filterbox.classList.toggle("hidden");
});


// Function to update the display of the length slider and filter rows
function updateLengthDisplay(value) {
    document.getElementById('lengthDisplay').innerText = value + " Hour" + (value > 1 ? "s" : "");
    filterTable();
}

// Function to update the display of the from-to slider and filter rows
function updateFromToDisplay(value) {
    document.getElementById('fromToDisplay').innerText = value + ":00";
    filterTable();
}

// Function to filter the rows of the booking table based on the slider values
function filterTable() {
    let lengthValue = parseInt(document.getElementById('lengthRange').value);
    let fromValue = parseInt(document.getElementById('fromToRange').value);
    let toValue = fromValue + lengthValue;

    // Ensure 'to' value does not exceed the limit of 24 hours
    if (toValue > 24) toValue = 24;

    let rows = document.querySelectorAll('#bookings-table tr');

    // Skip the header row and start from index 1
    for (let i = 1; i < rows.length; i++) {
        let row = rows[i];
        let visible = false;

        // Check each checkbox in the row
        row.querySelectorAll('input[type="checkbox"]').forEach((checkbox, index) => {
            let time = parseInt(checkbox.getAttribute('time'));
            // If the time is within the selected range, show this row
            if (time >= fromValue && time < toValue) {
                visible = true;
            }
        });

        // Toggle row visibility
        row.style.display = visible ? '' : 'none';
    }
}

// Initial table update and filtering when page loads
document.addEventListener('DOMContentLoaded', () => {
    updateBookingTable().then(() => {
        updateLengthDisplay(document.getElementById('lengthRange').value);
        updateFromToDisplay(document.getElementById('fromToRange').value);
    });
});
