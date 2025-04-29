import {applyFilters, initFilters} from "./filter.js";

let bookings = []
let rooms = ["1.0", "2.0", "3.0", "4.0", "5.0", "6.0", "7.0", "8.0", "9.0"]
let roomids = {
    1: "1.0",
    2: "2.0",
    3: "3.0",
    4: "4.0",
    5: "5.0",
    6: "6.0",
    7: "7.0",
    8: "8.0",
    9: "9.0"
}

// Setup Date
let date = document.querySelector("#date");
date.valueAsDate = new Date();
date.min = new Date().toISOString().split("T")[0];

// Next & Previous Buttons
let next = document.querySelector("#next");
next.addEventListener("click", () => {
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

function getSelectedBookings() {
    let table = document.getElementById("bookings-table");

    let selections = [];
    for (let row of table.children) {
        for (let data of row.children) {
            if (data.children[0] != undefined) {
                let box = data.children[0];
                if (box.checked && !box.disabled) {
                    selections.push({ time: box.getAttribute("time"), room: box.getAttribute("room") })
                }
            }
        }
    }

    return selections;
}

let book = document.querySelector("#book");
book.addEventListener("click", () => {
    let sel = getSelectedBookings();
    for (let booking of sel) {
        let time = new Date(date.value);
        const offsetMinutes = new Date().getTimezoneOffset();
        time.setHours(time.getHours() + Number(booking.time) + offsetMinutes / 60);
        fetch("/booking/book", {
            method: "POST",
            body: JSON.stringify({
                token: localStorage.getItem("token"),
                time: time.getTime()
            })
        })
    }
    console.log(sel);
})

function getIdForRoom(room) {
    return Object.keys(roomids).find(key => roomids[key] === room)
}

export function renderBookingTable() {
    let table = document.getElementById("bookings-table")

    table.innerHTML = '';

    // Place the time headings onto the table
    let header = document.createElement("tr")
    let room_header = document.createElement("th")
    room_header.textContent = "Room/Time"
    header.appendChild(room_header)
    for (let i = 0; i < 24; i++) {
        let time = document.createElement("th")
        time.textContent = `${i.toString()}:00`
        header.appendChild(time)
    }
    table.appendChild(header)

    let _rooms = applyFilters(rooms, bookings)

    // Place the rooms and the checkboxes in the table
    for (let room of _rooms) {
        let row = document.createElement("tr")
        let room_name = document.createElement("th")
        room_name.textContent = room
        row.appendChild(room_name)
        for (let i = 0; i < 24; i++) {
            let booking = document.createElement("td")
            let checkbox = document.createElement("input")
            checkbox.type = "checkbox"
            checkbox.checked = false
            checkbox.disabled = false
            checkbox.setAttribute("time", i)
            checkbox.setAttribute("room", getIdForRoom(room));
            booking.appendChild(checkbox);
            row.appendChild(booking)
        }
        table.appendChild(row)
    }

    // mark booked rooms
    for (let booking of bookings) {
        console.log(booking)
        let checkbox = document.querySelector(`input[type="checkbox"][time="${booking.time}"][room="${getIdForRoom(booking.room)}"]`)
        if (checkbox === null) continue;
        checkbox.disabled = true
        checkbox.checked = true
    }

}

async function updateBookingTable() {

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
        ...bookings,
        { time: 11, room: "3.0" },
        { time: 12, room: "3.0" },
        { time: 13, room: "3.0" },
        { time: 14, room: "3.0" }
    ]

    renderBookingTable();
}

// Initialise
document.addEventListener('DOMContentLoaded', () => {
    updateBookingTable().then(() => {
        initFilters()
    });
});
