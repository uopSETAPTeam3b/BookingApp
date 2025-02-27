document.querySelector("#date").valueAsDate = new Date();

let next = document.querySelector("#next");
next.addEventListener("click", () => {
    let date = document.querySelector("#date")
    let currentDate = new Date(date.value);
    currentDate.setDate(currentDate.getDate() + 1);
    date.valueAsDate = currentDate;
    updateBookingTable()
})

let pre = document.querySelector("#pre");
pre.addEventListener("click", () => {
    let date = document.querySelector("#date")
    let currentDate = new Date(date.value);
    currentDate.setDate(currentDate.getDate() - 1);
    date.valueAsDate = currentDate;
    updateBookingTable()
})

function updateBookingTable() {
    let table = document.getElementById("bookings-table")
    table.innerHTML = '';
    // fetch all the bookings for current date
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
            booking.appendChild(checkbox);
            row.appendChild(booking)
        }
        table.appendChild(row)
    }
}

updateBookingTable()