import { checkLoggedInExpt } from "./nav.js";
import { showConfirmationOverlay } from "./confirmation_overlay.js";
let previousBuilding = null;
let selectedSlots = [];

let date = document.querySelector("#date");
date.valueAsDate = new Date();
date.min = new Date().toISOString().split("T")[0];

let next = document.querySelector("#next");
next.addEventListener("click", () => {
  date.stepUp();
  updateBookingTable();
});

let pre = document.querySelector("#pre");
pre.addEventListener("click", () => {
  let date = document.querySelector("#date");
  if (new Date(date.value) < new Date().setHours(0, 0, 0, 0)) return;
  date.stepDown();
  updateBookingTable();
});

function getSelectedBookings() {
  const table = document.getElementById("bookings-table");
  const selections = [];

  for (let row of table.rows) {
    for (let cell of row.cells) {
      if (cell.textContent === "✔️") {
        selections.push({
          time: cell.dataset.time,
          room: cell.dataset.roomId,
        });
      }
    }
  }

  return selections;
}

let book = document.querySelector("#book");

book.addEventListener("click", () => {
  let sel = getSelectedBookings();
  if (sel.length === 0) return;

  let room = null;
  for (let s of sel) {
    if (room !== null && room !== s.room) {
      alert("Please select only one room");
      return;
    }
    room = s.room;
  }

  const firstBooking = sel[0];
  let dateSelector = document.getElementById("date");
  let selectedDateStr = dateSelector.value;
  let useableDate = new Date(selectedDateStr);

  let selectedDate = parseInt(Math.floor(useableDate.getTime() / 1000));
  const offsetMinutes = new Date().getTimezoneOffset();
  console.log("Offset minutes", offsetMinutes);
  function getBookingTimestamp(dateStr, hourOfDay) {
    const selectedDate = new Date(dateStr);
    selectedDate.setHours(hourOfDay, 0, 0, 0);
    return Math.floor(selectedDate.getTime() / 1000);
  }
  
  let slotTime = getBookingTimestamp(selectedDateStr, Number(firstBooking.time));
  console.log("Slot time", slotTime);

  fetch("/booking/book", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      token: localStorage.getItem("token"),
      datetime: slotTime,
      duration: sel.length,
      room_id: firstBooking.room,
    }),
  })
    .then((response) => {
      if (!response.ok) {
        return response.text().then((err) => {
          throw new Error(err.detail || "Failed to book room");
        });
      }
      return response.json();
    })
    .then((data) => {
      console.log("Booking response:", data);

      updateBookingTable();
      showConfirmationOverlay(data.booking_id, [
        {
          room: `${data.building_name} - ${data.room_name}`,
          time: formatTime(data.start_time, data.duration),
        },
      ]);
    })
    .catch((error) => {
      console.error("Error booking room:", error);
      alert("Failed to book room: " + error.message);
    });
});
function formatTime(startTimestamp, durationHours) {
  const startDate = new Date(startTimestamp * 1000);
  const endDate = new Date(
    startDate.getTime() + durationHours * 60 * 60 * 1000
  );

  const format = (date) =>
    date.getHours().toString().padStart(2, "0") +
    ":" +
    date.getMinutes().toString().padStart(2, "0");

  return `${format(startDate)} - ${format(endDate)}`;
}
function getIdForRoom(room) {
  return Object.keys(roomids).find((key) => roomids[key] === room);
}

async function fetchRoomsAndBuildings() {
  try {
    const response = await fetch("/booking/get_rooms", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
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
  console.log(buildings);
  buildings.forEach((building) => {
    const option = document.createElement("option");
    option.value = building;
    option.textContent = building.name;
    buildingSelect.appendChild(option);
  });
}

export function renderBookingTable(bookings, rooms, buildings, selectedDate) {
  let table = document.getElementById("bookings-table");
  let buildingSelector = document.getElementById("buildingSelect");
  let buildingName =
    buildingSelector.options[buildingSelector.selectedIndex].text;
  table.innerHTML = "";

  let building;
  if (buildingName === "Any") {
    building = {
      name: "Any",
      opening_time: "00,00",
      closing_time: "24,00",
      id: "any",
    };
  } else {
    building = buildings.find((b) => b.name === buildingName);
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
  console.log("building name", building.name, "previous", previousBuilding);
  if (previousBuilding !== building.name) {
    console.log("Setting from and to values");
    from.value = parseInt(building.opening_time.split(",")[0]);
    to.value = parseInt(building.closing_time.split(",")[0]);
  }
  previousBuilding = building.name;
  const maxCapacity = Math.max(...rooms.map((room) => room.capacity));
  const capacity = document.getElementById("capacityRange");
  capacity.max = maxCapacity;
  updateFilterDisplay();

  let header = document.createElement("tr");
  let room_header = document.createElement("th");
  room_header.textContent = "Room/Time";
  header.appendChild(room_header);
  for (
    let i = parseInt(building.opening_time.split(",")[0]);
    i < parseInt(building.closing_time.split(",")[0]);
    i++
  ) {
    if (applyFiltersCol(i)) continue;
    let time = document.createElement("th");
    time.textContent = `${i.toString().padStart(2, "0")}:00`;
    header.appendChild(time);
  }
  table.appendChild(header);

  for (let room of rooms) {
    if (
      (room.building_id !== building.id && building.name !== "Any") ||
      applyFilters(room)
    )
      continue;
    const currentBuilding = buildings.find((b) => b.id === room.building_id);
    let row = document.createElement("tr");
    let room_name = document.createElement("th");
    room_name.innerHTML = `
          <div style="font-size: 0.85em; line-height: 1.2;">
            <strong>${room.name}</strong><br>
            <span style="color: #555;">${room.type.split(" ")[0]}</span><br>
            <span style="font-size: 0.9em; color: #555;">${
              currentBuilding.name
            }</span>
            <span style="font-size: 0.9em; color: #777;">(${
              room.capacity
            })</span>
          </div>
        `;
    room_name.addEventListener("click", () => {
      showRoomDetails(room, currentBuilding)
    })

    row.appendChild(room_name);

    const availabilityMap = [];
    const cellMap = [];

    for (
      let i = parseInt(building.opening_time.split(",")[0]);
      i < parseInt(building.closing_time.split(",")[0]);
      i++
    ) {
      if (applyFiltersCol(i, room)) continue;

      const cell = document.createElement("td");
      let timeSlotStart = getTimestampForTimeOfDay(selectedDate, i);
      let slotBuilding = buildings.find((b) => b.id === room.building_id);

      if (
        i < parseInt(slotBuilding.opening_time.split(",")[0]) ||
        i >= parseInt(slotBuilding.closing_time.split(",")[0])
      ) {
        cell.classList.add("closed");
        cell.style.backgroundColor = "grey";
        cell.style.pointerEvents = "none";
        cell.dataset.booked = "false";
        availabilityMap.push(false);
      } else {
        let isBooked = false;
        if (!bookings.details) {
          let booking = bookings.bookings.find(
            (booking) =>
              booking.room_id === room.id &&
              isTimeSlotBooked(booking, timeSlotStart)
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

    const validIndexes = new Set();
    let streakStart = null;

    for (let i = 0; i <= availabilityMap.length; i++) {
      if (availabilityMap[i]) {
        if (streakStart === null) streakStart = i;
      } else {
        if (streakStart !== null && i - streakStart >= length) {
          for (let j = streakStart; j < i; j++) validIndexes.add(j);
        }
        streakStart = null;
      }
    }

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
            const index = selectedSlots.findIndex(
              (slot) => slot.roomId === roomId && slot.time === time
            );

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
function closeRoomModal() {
  document.getElementById("room-modal").style.display = "none";
  document.getElementById("modal-backdrop").style.display = "none";
}
function showRoomDetails(room, currentBuilding) {

  const modal = document.getElementById("room-modal");
  const content = document.getElementById("room-modal-content")
  content.innerHTML = `
  <h3>${room.name}</h3>
  <p><strong>Type:</strong> ${room.type || "N/A"}</p>
  <p><strong>Capacity:</strong> ${room.capacity || "N/A"}</p>
  <p><strong>Building:</strong> ${currentBuilding?.name || "N/A"}</p>
  <p><strong>Address:</strong> ${currentBuilding?.address_1 || ""}, ${
    currentBuilding?.address_2 || ""
  }</p>
  <p><strong>Facilities:</strong></p>
  <ul>
    ${
      Array.isArray(room.facilities) && room.facilities.length > 0
        ? room.facilities.map(f => `<li>${f.name || "N/A"}</li>`).join("")
        : "<li>No facilities listed</li>"
    }
  </ul>
`;
  modal.style.display = "block";
  
}
function getSelectedFacilityIds() {
  const checkboxes = document.querySelectorAll("#facility-list input[type='checkbox']");
  return Array.from(checkboxes)
    .filter(cb => cb.checked)
    .map(cb => cb.value);
}
function updateFilterDisplay() {
  const { fromValue, toValue, lengthValue, capacityValue } = getFilterValues();
  const fromDisplay = document.getElementById("fromDisplay");
  fromDisplay.innerText = fromValue + ":00";
  const toDisplay = document.getElementById("toDisplay");
  toDisplay.innerText = toValue + ":00";
  const lengthDisplay = document.getElementById("lengthDisplay");
  lengthDisplay.innerText =
    lengthValue + " Hour" + (lengthValue > 1 ? "s" : "");
  const capacityDisplay = document.getElementById("capacityDisplay");
  capacityDisplay.innerText =
    capacityValue + " People" + (capacityValue > 1 ? "s" : "");
}

function getFilterValues() {
  const fromValue = document.getElementById("fromRange").value;
  const toValue = document.getElementById("toRange").value;
  const lengthValue = document.getElementById("lengthRange").value;
  const capacityValue = document.getElementById("capacityRange").value;
  const roomTypeValue = document.getElementById("roomTypeSelect").value;

  const facilities = Array.from(document.querySelectorAll("#facility-list input[type='checkbox']"))
    .filter(cb => cb.checked)
    .map(cb => cb.value);

  return {
    fromValue,
    toValue,
    lengthValue,
    capacityValue,
    roomTypeValue,
    facilities
  };
}
function applyFiltersCol(slot) {
  const { fromValue, toValue } = getFilterValues();
  const now = new Date();
  const currentDay = now.getDate();
  const currentMonth = now.getMonth();
  const currentYear = now.getFullYear();
  const currentHour = now.getHours();
  const currentMinute = now.getMinutes();

  const dateInput = document.querySelector("#date").value;
  const selectedDate = new Date(dateInput);
  const selectedDay = selectedDate.getDate();
  const selectedMonth = selectedDate.getMonth();
  const selectedYear = selectedDate.getFullYear();

  const isToday =
    currentDay === selectedDay &&
    currentMonth === selectedMonth &&
    currentYear === selectedYear;

  const isTooEarly =
    isToday &&
    (slot < currentHour || (slot === currentHour && currentMinute > 45));

  if (slot < fromValue || slot > toValue || isTooEarly) {
    return true;
  }

  return false;
}
function applyFilters(room) {
  const {
    fromValue,
    toValue,
    lengthValue,
    capacityValue,
    roomTypeValue,
    facilities: selectedFacilities
  } = getFilterValues();
  
  // Filter by type and capacity
  if (
    (roomTypeValue !== "any" && room.type !== roomTypeValue) ||
    room.capacity < capacityValue
  ) {
    return true;
  }
  
  // Filter by facilities
  if (selectedFacilities.length > 0) {
    const roomFacilityIds = room.facilities.map(f => f.id.toString());
    const hasAllSelectedFacilities = selectedFacilities.every(id => roomFacilityIds.includes(id));
    
    if (!hasAllSelectedFacilities) {
      return true;
    }
  }
  
  return false;
}

function getTimestampForTimeOfDay(dateUnixTimestamp, hours) {
  const date = new Date(dateUnixTimestamp * 1000);

  date.setHours(hours, 0, 0, 0);

  return Math.floor(date.getTime() / 1000);
}
function isTimeSlotBooked(booking, timeSlot, slotDurationInSeconds = 3600) {
  const bookingStartTime = booking.start_time * 1000;
  const bookingEndTime = (booking.start_time + booking.duration * 3600) * 1000;

  const roundedTimeSlot =
    Math.floor(timeSlot / slotDurationInSeconds) * slotDurationInSeconds;
  const timeSlotStart = roundedTimeSlot * 1000;
  const timeSlotEnd = timeSlotStart + slotDurationInSeconds * 1000;

  return timeSlotStart < bookingEndTime && timeSlotEnd > bookingStartTime;
}

export async function updateBookingTable() {
  if ((await checkLoggedInExpt()) === false) {
    const table = document.getElementById("bookings-table");
    table.innerHTML = "";
    const listItem = document.createElement("li");
    listItem.innerHTML =
      "You are not logged in. Please log in to view your bookings.";
    table.appendChild(listItem);
    return;
  }
  let date = document.querySelector("#date");

  let response = await fetch("/booking/get_rooms", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      date: new Date(date.value).toString(),
    }),
  });

  let data = await response.json();
  let rooms = data.rooms;
  let buildings = data.buildings;
  let dateSelector = document.getElementById("date");
  let selectedDateStr = dateSelector.value;
  let useableDate = new Date(selectedDateStr);
  let facilities = {};
  for (let room of rooms) {
    for (let facility of room.facilities) {
      facilities[facility.id] = {
        id: facility.id,
        name: facility.name,
      };
    }
  }
  
  const selectedIds = getSelectedFacilityIds();
  const facilityList = document.getElementById("facility-list");
  facilityList.innerHTML = "";

  for (let facility of Object.values(facilities)) {
    const li = document.createElement("li");
    li.style.listStyleType = "none"; 

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = facility.id;
    checkbox.style.marginRight = "8px";

    // Restore previous checked state
    if (selectedIds.includes(facility.id.toString())) {
      checkbox.checked = true;
    }

    checkbox.onclick = () => updateBookingTable();

    const label = document.createElement("strong");
    label.textContent = facility.name;

    const container = document.createElement("div");
    container.style.cssText = "font-size: 0.85em; line-height: 1.2; display: flex; align-items: center;";
    container.appendChild(checkbox);
    container.appendChild(label);

    li.appendChild(container);
    facilityList.appendChild(li);
  }

  let selectedDate = parseInt(Math.floor(useableDate.getTime() / 1000));

  response = await fetch(
    `/booking/get_bookings_for_date?dateTime=${selectedDate}`
  );

  let bookings = await response.json();
  console.log("Bookings:", bookings);

  renderBookingTable(bookings, rooms, buildings, selectedDate);
}

document.addEventListener("DOMContentLoaded", () => {

  const buildingSelector = document.getElementById("buildingSelect");
  buildingSelector.addEventListener("change", () => {
    let selectedBuilding = buildingSelector.value;
    console.log("Selected building:", selectedBuilding);
    updateBookingTable().then(() => {});
  });
  updateBookingTable().then(() => {});
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
    document.getElementById("lengthDisplay").innerText =
      lengthValue + " Hour" + (lengthValue > 1 ? "s" : "");
    updateBookingTable();
  });
  capacitySlider.addEventListener("input", () => {
    const capacityValue = capacitySlider.value;
    document.getElementById("capacityDisplay").innerText =
      capacityValue + " People" + (capacityValue > 1 ? "s" : "");
    updateBookingTable();
  });
  const closeRoomDetsBtn = document.getElementById("closeRoomDetails");
  closeRoomDetsBtn.addEventListener("click", closeRoomModal);
  roomTypeSelect.addEventListener("change", () => {
    const roomTypeValue = roomTypeSelect.value;
    updateBookingTable();
  });
  fetchRoomsAndBuildings();
});
