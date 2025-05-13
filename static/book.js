let previousBuilding = null;
let selectedSlots = []
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
    buildingSelect.innerHTML = '<option value="Any">Any</option>';
    console.log(buildings)
    buildings.forEach(building => {
        const option = document.createElement("option");
        option.value = building;
        option.textContent = building.name;
        buildingSelect.appendChild(option);
    });
}

export function renderBookingTable(bookings, rooms, buildings, selectedDate) {
    let table = document.getElementById("bookings-table");
    let buildingSelector = document.getElementById("buildingSelect");
    let buildingName = buildingSelector.options[buildingSelector.selectedIndex].text;
    table.innerHTML = '';

    let building;
    if (buildingName === "Any") {
        building = {
            name: "Any",
            opening_time: "00,00",
            closing_time: "24,00",
            id: "any"
        };
        
    } else {
        building = buildings.find(b => b.name === buildingName);
    }

    if (!building) {
        console.error("Building not found");
        return;
    }

    const from = document.getElementById("fromRange");
    const to = document.getElementById("toRange");
    const length = parseInt(document.getElementById("lengthRange").value);
    from.min = parseInt(building.opening_time.split(",")[0]);
    from.max = parseInt(building.closing_time.split(",")[0]);
    to.min = parseInt(building.opening_time.split(",")[0]);
    to.max = parseInt(building.closing_time.split(",")[0]);
    console.log("building name", building.name, "previous", previousBuilding)
    if (previousBuilding !== building.name) {
        console.log("Setting from and to values");
        from.value = parseInt(building.opening_time.split(",")[0]);
        to.value = parseInt(building.closing_time.split(",")[0]);
    }
    previousBuilding = building.name;
    const maxCapacity = Math.max(...rooms.map(room => room.capacity));
    const capacity = document.getElementById("capacityRange");
    capacity.max = maxCapacity;
    updateFilterDisplay();
    // Table header
    let header = document.createElement("tr");
    let room_header = document.createElement("th");
    room_header.textContent = "Room/Time";
    header.appendChild(room_header);
    for (let i = parseInt(building.opening_time.split(",")[0]); i < parseInt(building.closing_time.split(",")[0]); i++) {
        if (applyFiltersCol(i)) continue;
        let time = document.createElement("th");
        time.textContent = `${i.toString().padStart(2, '0')}:00`;
        header.appendChild(time);
    }
    table.appendChild(header);

    for (let room of rooms) {
        if ((room.building_id !== building.id && building.name !== "Any") || applyFilters(room)) continue;
        const currentBuilding = buildings.find(b => b.id === room.building_id);
        let row = document.createElement("tr");
        let room_name = document.createElement("th");
        room_name.innerHTML = `
          <div style="font-size: 0.85em; line-height: 1.2;">
            <strong>${room.name}</strong><br>
            <span style="color: #555;">${room.type.split(" ")[0]}</span><br>
            <span style="font-size: 0.9em; color: #555;">${currentBuilding.name}</span>
            <span style="font-size: 0.9em; color: #777;">(${room.capacity})</span>
          </div>
        `;
        row.appendChild(room_name);

        const availabilityMap = [];
        const cellMap = [];

        // First Pass – build availability map
        for (let i = parseInt(building.opening_time.split(",")[0]); i < parseInt(building.closing_time.split(",")[0]); i++) {
            if (applyFiltersCol(i, room)) continue;

            const cell = document.createElement("td");
            let timeSlotStart = getTimestampForTimeOfDay(selectedDate, i);
            let slotBuilding = buildings.find(b => b.id === room.building_id);

            if (i < parseInt(slotBuilding.opening_time.split(",")[0]) || i >= parseInt(slotBuilding.closing_time.split(",")[0])) {
                // Closed
                cell.classList.add("closed");
                cell.style.backgroundColor = "grey";
                cell.style.pointerEvents = "none";
                cell.dataset.booked = "false";
                availabilityMap.push(false);
            } else {
                // Check if booked
                let isBooked = false;
                if (!bookings.details) {
                    let booking = bookings.bookings.find(booking =>
                        booking.room_id === room.id && isTimeSlotBooked(booking, timeSlotStart)
                    );
                    if (booking) {
                        isBooked = true;
                    }
                }
                availabilityMap.push(!isBooked);
            }

            cell.dataset.time = i;
            cell.dataset.roomId = room.id;
            cellMap.push(cell);
        }

        // Second Pass – mark available groups
        const validIndexes = new Set();
        let streakStart = null;

        for (let i = 0; i <= availabilityMap.length; i++) {
            if (availabilityMap[i]) {
                if (streakStart === null) streakStart = i;
            } else {
                if (streakStart !== null && (i - streakStart) >= length) {
                    for (let j = streakStart; j < i; j++) validIndexes.add(j);
                }
                streakStart = null;
            }
        }

        // Final Pass – fill cell content
        for (let i = 0; i < cellMap.length; i++) {
            const cell = cellMap[i];
            if (availabilityMap[i]) {
                if (validIndexes.has(i)) {
                    cell.style.backgroundColor = "lightblue";
                    cell.textContent = "Book";
                    cell.classList.add("available");
                    cell.dataset.booked = "false";
                    cell.addEventListener("click", () => {
                        if (cell.dataset.booked === "true") return;

                        const roomId = cell.dataset.roomId;
                        const time = cell.dataset.time;
                        const index = selectedSlots.findIndex(slot => slot.roomId === roomId && slot.time === time);

                        if (index === -1) {
                            cell.classList.remove("available");
                            cell.classList.add("selected");
                            cell.textContent = "✔️";
                            selectedSlots.push({ roomId, time });
                        } else {
                            cell.classList.remove("selected");
                            cell.classList.add("available");
                            cell.textContent = "Book";
                            selectedSlots.splice(index, 1);
                        }
                    });
                } else {
                    // Not part of a valid streak
                    cell.classList.add("unusable");
                    cell.style.backgroundColor = "#ddd";
                    cell.style.pointerEvents = "none";
                    cell.textContent = "Filtered";
                    cell.dataset.booked = "false";
                }
            }
            row.appendChild(cell);
        }

        table.appendChild(row);
    }
}

function updateFilterDisplay() {
    const { fromValue, toValue, lengthValue, capacityValue } = getFilterValues();
    const fromDisplay = document.getElementById("fromDisplay");
    fromDisplay.innerText = fromValue + ":00";
    const toDisplay = document.getElementById("toDisplay");
    toDisplay.innerText = toValue + ":00";
    const lengthDisplay = document.getElementById("lengthDisplay");
    lengthDisplay.innerText = lengthValue + " Hour" + (lengthValue > 1 ? "s" : "");
    const capacityDisplay = document.getElementById("capacityDisplay");
    capacityDisplay.innerText = capacityValue + " People" + (capacityValue > 1 ? "s" : "");
    
}

function getFilterValues() {
    const fromValue = document.getElementById("fromRange").value;
    const toValue = document.getElementById("toRange").value;
    const lengthValue = document.getElementById("lengthRange").value;
    const capacityValue = document.getElementById("capacityRange").value;
    const roomTypeValue = document.getElementById("roomTypeSelect").value;
    return { fromValue, toValue, lengthValue , capacityValue, roomTypeValue};
}
function applyFiltersCol(slot){
    const { fromValue, toValue, lengthValue, capacityValue, roomTypeValue} = getFilterValues();
    if (slot < fromValue || slot > toValue ) {
        return true;
    }
    return false;
}
function applyFilters(room){
    const { fromValue, toValue, lengthValue, capacityValue, roomTypeValue} = getFilterValues();
    if ((roomTypeValue !== "any" && room.type !== roomTypeValue) || room.capacity < capacityValue) {
        
        return true; // Should be filtered
    }
    return false;

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
    response = await fetch(`/booking/get_bookings_for_date?dateTime=${selectedDate}`)

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
        updateBookingTable().then(() => {
            //initFilters()
        });
    });
    updateBookingTable().then(() => {
        //initFilters()
    });
    const fromSlider = document.getElementById("fromRange");
    const toSlider = document.getElementById("toRange");
    const lengthSlider = document.getElementById("lengthRange");
    const capacitySlider = document.getElementById("capacityRange");
    const roomTypeSelect = document.getElementById("roomTypeSelect");
    fromSlider.addEventListener("input", () => {
        const fromValue = fromSlider.value;
        document.getElementById("fromDisplay").innerText = fromValue + ":00";
        updateBookingTable();
    });
    toSlider.addEventListener("input", () => {
        const toValue = toSlider.value;
        document.getElementById("toDisplay").innerText = toValue + ":00";
        updateBookingTable();
    });
    lengthSlider.addEventListener("input", () => {
        const lengthValue = lengthSlider.value;
        document.getElementById("lengthDisplay").innerText = lengthValue + " Hour" + (lengthValue > 1 ? "s" : "");
        updateBookingTable();
    });
    capacitySlider.addEventListener("input", () => {
        const capacityValue = capacitySlider.value;
        document.getElementById("capacityDisplay").innerText = capacityValue + " People" + (capacityValue > 1 ? "s" : "");
        updateBookingTable();
    });
    
    roomTypeSelect.addEventListener("change", () => {
        const roomTypeValue = roomTypeSelect.value;
        updateBookingTable();
    });
    fetchRoomsAndBuildings()
});
