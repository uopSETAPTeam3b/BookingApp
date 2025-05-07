import {applyFilters, initFilters} from "./filter.js";

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

async function fetchRoomsAndBuildings() {
    //Gets a list of all rooms and buildings from the server, 
    // then populates the buildings drop down
    try {
        const response = await fetch("/booking/get_rooms", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({})
        });

        if (!response.ok) throw new Error("Failed to fetch data");

        const data = await response.json();
        const { rooms, buildings } = data;

        populateBuildingDropdown(buildings);
    } catch (error) {
        console.error("Error fetching rooms/buildings:", error);
    }
}
function populateBuildingDropdown(buildings) {
    const buildingSelect = document.getElementById("buildingSelect");
    buildingSelect.innerHTML = '<option value="">Select a Building</option>';
    console.log(buildings)
    buildings.forEach(building => {
        const option = document.createElement("option");
        option.value = building;
        option.textContent = building.name;
        buildingSelect.appendChild(option);
    });
}

export function renderBookingTable(bookings, rooms, buildings, selectedDate) {
    let table = document.getElementById("bookings-table")
    let buildingSelector = document.getElementById("buildingSelect");
    let buildingName = buildingSelector.options[buildingSelector.selectedIndex].text;
    table.innerHTML = '';
    if (buildingName === "Select a Building") {
        let noBuilding = document.createElement("tr")
        let noBuildingText = document.createElement("td")
        noBuildingText.colSpan = 25
        noBuildingText.textContent = "Please select a building"
        noBuilding.appendChild(noBuildingText)
        table.appendChild(noBuilding)
        return
    }
    let building = buildings.find(b => b.name === buildingName)
    // Place the time headings onto the table
    let header = document.createElement("tr")
    let room_header = document.createElement("th")
    room_header.textContent = "Room/Time"
    header.appendChild(room_header)
    for (let i = parseInt(building.opening_time.split(",")[0]); i < parseInt(building.closing_time.split(",")[0]); i++) {
        let time = document.createElement("th")
        time.textContent = `${i.toString()}:00`
        header.appendChild(time)
    }
    table.appendChild(header)
    console.log("bookings filter", bookings)
    let _rooms = applyFilters(rooms, bookings.bookings, building.id)
    // Place the rooms and the checkboxes in the table
    for (let room of _rooms) {
        let row = document.createElement("tr")
        let room_name = document.createElement("th")
        room_name.textContent = room.name
        row.appendChild(room_name)
        for (let i = parseInt(building.opening_time.split(",")[0]); i < parseInt(building.closing_time.split(",")[0]); i++) {
            let booking = document.createElement("td")
            let checkbox = document.createElement("input")
            checkbox.type = "checkbox"
            checkbox.checked = false
            checkbox.disabled = false
            checkbox.setAttribute("time", i)
            checkbox.setAttribute("room", parseInt(room.id));
            let timeSlotStart = getTimestampForTimeOfDay(selectedDate, i);
            if (!bookings.details) {
                let findBooking = bookings.bookings.find(booking => 
                    booking.room_id === room.id && isTimeSlotBooked(booking, timeSlotStart)
                );
                if (findBooking) {
                    checkbox.checked = true;
                    checkbox.disabled = true;
                }
            }
            
            
            booking.appendChild(checkbox);
            row.appendChild(booking)
        }
        table.appendChild(row)
    }

}
function getTimestampForTimeOfDay(dateUnixTimestamp, hours) {
    // Convert the Unix timestamp to a Date object
    const date = new Date(dateUnixTimestamp * 1000);  // Convert to milliseconds

    // Set the time to the specified hour (e.g., 08:00)
    date.setHours(hours, 0, 0, 0); // Set hours, minutes, seconds, milliseconds

    // Convert the Date object back to a Unix timestamp (in seconds)
    return Math.floor(date.getTime() / 1000);
}
function isTimeSlotBooked(booking, timeSlot, slotDurationInSeconds = 3600) {
    // Convert booking start and end times to milliseconds
    
    const bookingStartTime = booking.start_time * 1000;
    const bookingEndTime = (booking.start_time + booking.duration * 3600) * 1000;
  
    // Round timeSlot down to the nearest slot interval
    const roundedTimeSlot = Math.floor(timeSlot / slotDurationInSeconds) * slotDurationInSeconds;
    const timeSlotStart = roundedTimeSlot * 1000;
    const timeSlotEnd = timeSlotStart + slotDurationInSeconds * 1000;
  
    // Check for overlap
    return timeSlotStart < bookingEndTime && timeSlotEnd > bookingStartTime;
  }

export async function updateBookingTable(){

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

    let data = await response.json()
    let rooms = data.rooms
    let buildings = data.buildings
    let dateSelector = document.getElementById("date"); 
    let selectedDateStr = dateSelector.value; // format: "YYYY-MM-DD"
    let useableDate = new Date(selectedDateStr);

    // Convert to Unix timestamp (in seconds)
    let selectedDate = parseInt(Math.floor(useableDate.getTime() / 1000));
    // Get bookings for current date
    response = await fetch("/booking/get_bookings_for_date", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            dateTime: selectedDate 
        })
    })

    let bookings = await response.json()
    console.log("Bookings:", bookings)

    renderBookingTable(bookings, rooms, buildings, selectedDate);
}

// Initialise
document.addEventListener('DOMContentLoaded', () => {
    const buildingSelector = document.getElementById("buildingSelect");
    buildingSelector.addEventListener("change", () => {
        let selectedBuilding = buildingSelector.value;
        console.log("Selected building:", selectedBuilding);
        updateBookingTable(selectedBuilding).then(() => {
            //initFilters()
        });
    });
    updateBookingTable().then(() => {
        //initFilters()
    });
    fetchRoomsAndBuildings()
});
