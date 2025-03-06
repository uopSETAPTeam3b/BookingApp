rooms = []

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

    rooms = await response.json()
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
        {time: 20, room: "1.0"},
        {time: 21, room: "1.0"},
        {time: 22, room: "1.0"}
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