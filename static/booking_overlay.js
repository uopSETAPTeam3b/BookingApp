let selectedSlots = [];
let selectedRoomId = null;

let bookings = [];
let currentUserId = null;

async function fetchBookings() {
  try {
    const response = await fetch("/getBookings");
    const data = await response.json();
    bookings = data.bookings;
    currentUserId = data.currentUserId;
  } catch (err) {
    console.error("Failed to load bookings", err);
  }
}
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

function selectSlot(room, hour, cell) {
  if (confirm(`Book ${room} at ${hour}:00?`)) {
    fetch("/bookRoom", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ room, hour }),
    })
      .then((res) => res.json())
      .then((data) => {
        alert(data.message || "Booking successful");
        openOverlay();
      });
  }
}
async function getDayBookings(bookingId) {
  try {
    const response = await fetch(
      `/booking/get_day_bookings?booking_id=${bookingId}`
    );

    if (!response.ok) {
      throw new Error("Failed to fetch bookings");
    }

    const data = await response.json();

    if (data.bookings && data.bookings.length > 0) {
      console.log("Bookings for the day:", data.bookings);
      displayBookings(data.bookings, bookingId);
    } else {
      alert("No bookings found for that day.");
    }
  } catch (error) {
    console.error("Error:", error);
    alert("Error fetching bookings.");
  }
}
async function openOverlay(bookingId) {
  const closeBtn = document.getElementById("closeOverlayBtn");
  closeBtn.addEventListener("click", closeOverlay);
  const header = document.getElementById("booking_id");
  header.innerText = bookingId;
  const confirmButton = document.getElementById("confirmEditBtn");
  confirmButton.addEventListener("click", alterCurrentBooking);
  const overlay = document.getElementById("bookingOverlay");
  overlay.classList.add("active");
  await getDayBookings(bookingId);
}

async function alterCurrentBooking() {
  const token = localStorage.getItem("token");
  const room_id = selectedRoomId;
  const duration = selectedSlots.length;
  const dayTime = selectedSlots[0].hour;
  const old_booking_id = parseInt(
    document.getElementById("booking_id").innerText
  );
  try {
    const response = await fetch("/booking/edit_booking", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        token,
        dayTime,
        room_id,
        duration,
        old_booking_id,
      }),
    });

    const result = await response.text();
    if (!response.ok) {
      throw new Error(`Failed: ${result}`);
    }

    location.reload(true);
    closeOverlay();
  } catch (error) {
    console.error("Error editing booking:", error.message);
    alert("Could not edit booking: " + error.message);
  }
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

    return { rooms, buildings };
  } catch (error) {
    console.error("Error fetching rooms/buildings:", error);
  }
}
async function displayBookings(bookings, selectedBookingId) {
  const tbody = document.getElementById("booking-body");
  tbody.innerHTML = "";
  console.log("Bookings HEREHEHHEHE:", bookings);

  const { rooms, buildings } = await fetchRoomsAndBuildings();

  const currentBooking = bookings.find(
    (b) => b.booking_id === selectedBookingId
  );
  if (!currentBooking) {
    console.error("Booking not found for ID:", selectedBookingId);
    return;
  }

  const openTime = parseInt(currentBooking.opening_time.split(":")[0]);
  const closeTime = parseInt(currentBooking.closing_time.split(":")[0]);

  const bookingDate = new Date(currentBooking.start_time * 1000);
  const year = bookingDate.getUTCFullYear();
  const month = bookingDate.getUTCMonth();
  const day = bookingDate.getUTCDate();

  const headerRow = document.createElement("tr");
  const emptyCell = document.createElement("th");
  headerRow.appendChild(emptyCell);
  for (let i = openTime; i < closeTime; i++) {
    const th = document.createElement("th");
    th.textContent = `${i}:00`;
    headerRow.appendChild(th);
  }
  tbody.appendChild(headerRow);

  rooms.forEach((room) => {
    if (room.building_id === currentBooking.building_id) {
      const row = document.createElement("tr");

      const roomCell = document.createElement("td");
      roomCell.textContent = room.name;
      row.appendChild(roomCell);

      for (let i = openTime; i < closeTime; i++) {
        const cell = document.createElement("td");

        const localDate = new Date(year, month, day, i, 0, 0);
        const timeSlotStart = Math.floor(localDate.getTime() / 1000);

        let booking = bookings.find(
          (booking) =>
            booking.room_id === room.id &&
            isTimeSlotBooked(booking, timeSlotStart)
        );

        if (booking) {
          cell.style.backgroundColor =
            booking.booking_id === selectedBookingId ? "red" : "lightblue";
          const bstTime = new Date(
            booking.start_time * 1000
          ).toLocaleTimeString("en-GB", {
            timeZone: "Europe/London",
            hour: "2-digit",
            minute: "2-digit",
            hour12: false,
          });
          cell.textContent = "   ";
        } else {
          cell.style.backgroundColor = "green";
          cell.textContent = " Book ";

          cell.onclick = () => {
            if (selectedRoomId !== null && selectedRoomId !== room.id) {
              const allCells = document.querySelectorAll("td");
              allCells.forEach((c) => {
                if (c.style.backgroundColor === "yellow") {
                  c.style.backgroundColor = "green";
                }
              });
              selectedSlots = [];
            }

            selectedRoomId = room.id;

            const slotKey = `${room.id}-${i}`;
            const alreadySelected = selectedSlots.find(
              (slot) => slot.room === room.id && slot.hour === i
            );

            if (!alreadySelected) {
              cell.style.backgroundColor = "yellow";
              selectedSlots.push({ room: room.id, hour: i });

              selectedSlots.sort((a, b) => a.hour - b.hour);

              for (let j = 1; j < selectedSlots.length; j++) {
                if (selectedSlots[j].hour - selectedSlots[j - 1].hour > 1) {
                  const invalidSlots = selectedSlots.slice(0, j);
                  invalidSlots.forEach((slot) => {
                    const selector = `td`;
                    const cells = document.querySelectorAll(selector);
                    cells.forEach((c) => {
                      if (
                        c.style.backgroundColor === "yellow" &&
                        c.parentElement.firstChild.textContent === room.name &&
                        c.cellIndex - 1 === slot.hour - openTime
                      ) {
                        c.style.backgroundColor = "green";
                      }
                    });
                  });
                  selectedSlots = selectedSlots.slice(j);
                  break;
                }
              }
            } else {
              cell.style.backgroundColor = "green";
              selectedSlots = selectedSlots.filter(
                (slot) => !(slot.room === room.id && slot.hour === i)
              );

              if (selectedSlots.length === 0) {
                selectedRoomId = null;
              }
            }
          };
        }
        row.appendChild(cell);
      }

      tbody.appendChild(row);
    }
  });
}

function generateTimeSlots() {
  const timeSlots = [];
  const startHour = 8;
  const endHour = 20;

  for (let hour = startHour; hour < endHour; hour++) {
    timeSlots.push(hour);
  }

  return timeSlots;
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
function closeOverlay() {
  const overlay = document.getElementById("bookingOverlay");
  overlay.classList.remove("active");
}
