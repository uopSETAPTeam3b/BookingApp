let selectedSlots = [];
let selectedRoomId = null;
// Sample booking data, you should fetch this from the backend
// Format: { room: "Room A", hour: 9, userId: 1 }
let bookings = [];
let currentUserId = null;

async function fetchBookings() {
  try {
    const response = await fetch("/getBookings"); // Add token if needed
    const data = await response.json();
    bookings = data.bookings;
    currentUserId = data.currentUserId;
  } catch (err) {
    console.error("Failed to load bookings", err);
  }
}



function selectSlot(room, hour, cell) {
  // You could visually show selection or send booking request
  if (confirm(`Book ${room} at ${hour}:00?`)) {
    // Send request to book
    fetch("/bookRoom", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ room, hour })
    }).then(res => res.json()).then(data => {
      alert(data.message || "Booking successful");
      openOverlay(); // Rebuild the table
    });
  }
}
async function getDayBookings(bookingId) {
  try {
      // Make GET request to the API endpoint with the booking_id
      const response = await fetch(`/booking/get_day_bookings?booking_id=${bookingId}`);

      // Check if the response is okay (status code 200-299)
      if (!response.ok) {
          throw new Error("Failed to fetch bookings");
      }

      // Parse the JSON response
      const data = await response.json();
      
      // Check if the response contains bookings
      if (data.bookings && data.bookings.length > 0) {
          // Call function to display the bookings
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
  const header = document.getElementById("booking_id")
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
  const old_booking_id = parseInt(document.getElementById("booking_id").innerText);
  try {
    const response = await fetch("/booking/edit_booking", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        token,
        dayTime,
        room_id,
        duration,
        old_booking_id
      })
    });

    const result = await response.text(); // Assuming your backend returns a plain string
    if (!response.ok) {
      throw new Error(`Failed: ${result}`);
    }

    console.log("Edit booking success:", result);
    location.reload(true);
    closeOverlay();

  } catch (error) {
    console.error("Error editing booking:", error.message);
    alert("Could not edit booking: " + error.message);
  }
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


      return { rooms, buildings };
  } catch (error) {
      console.error("Error fetching rooms/buildings:", error);
  }
}
async function displayBookings(bookings, selectedBookingId) {
  const tbody = document.getElementById("booking-body");
  tbody.innerHTML = ""; // Clear previous rows
  console.log("Bookings HEREHEHHEHE:", bookings); // Debug log
  // Fetch rooms and buildings
  const { rooms, buildings } = await fetchRoomsAndBuildings();

  // Find the current booking
  const currentBooking = bookings.find(b => b.booking_id === selectedBookingId);
  if (!currentBooking) {
    console.error("Booking not found for ID:", selectedBookingId);
    return;
  }

  // Parse opening and closing times
  const openTime = parseInt(currentBooking.opening_time.split(":")[0]);
  const closeTime = parseInt(currentBooking.closing_time.split(":")[0]);

  // Get the date of the current booking (from start_time)
  const bookingDate = new Date(currentBooking.start_time * 1000);
  const year = bookingDate.getUTCFullYear();
  const month = bookingDate.getUTCMonth();
  const day = bookingDate.getUTCDate();

  // Create header row for time slots
  const headerRow = document.createElement("tr");
  const emptyCell = document.createElement("th"); // Empty cell for room column
  headerRow.appendChild(emptyCell);
  for (let i = openTime; i < closeTime; i++) {
    const th = document.createElement("th");
    th.textContent = `${i}:00`;
    headerRow.appendChild(th);
  }
  tbody.appendChild(headerRow);

  // Create a row for each room
  rooms.forEach(room => {
    if (room.building_id === currentBooking.building_id) {
      const row = document.createElement("tr");

      // Room name cell
      const roomCell = document.createElement("td");
      roomCell.textContent = room.name; // Assuming room has a 'name' property
      row.appendChild(roomCell);

      // Create a cell for each time slot
      for (let i = openTime; i < closeTime; i++) {
        const cell = document.createElement("td");

        // Construct Unix timestamp for the time slot (e.g., 8:00 on booking's date)
        const localDate = new Date(year, month, day, i, 0, 0); // This creates local time (BST-aware)
        const timeSlotStart = Math.floor(localDate.getTime() / 1000); // Convert to seconds
        

        // Find booking for this room and time slot
        let booking = bookings.find(booking => 
          booking.room_id === room.id && isTimeSlotBooked(booking, timeSlotStart)
        );
        

        if (booking) {
          // Booked slot
          cell.style.backgroundColor = booking.booking_id === selectedBookingId ? "red" : "lightblue";
          const bstTime = new Date(booking.start_time * 1000).toLocaleTimeString('en-GB', {
            timeZone: 'Europe/London',
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
          });
          cell.textContent = "   ";
        } else {
          // Available slot
          cell.style.backgroundColor = "green";
          cell.textContent = " Book ";
          
          cell.onclick = () => {
            if (selectedRoomId !== null && selectedRoomId !== room.id) {
              // Deselect all previous selections
              const allCells = document.querySelectorAll("td");
              allCells.forEach(c => {
                if (c.style.backgroundColor === "yellow") {
                  c.style.backgroundColor = "green";
                }
              });
              selectedSlots = [];
            }
          
            selectedRoomId = room.id;
          
            const slotKey = `${room.id}-${i}`;
            const alreadySelected = selectedSlots.find(slot => slot.room === room.id && slot.hour === i);
          
            if (!alreadySelected) {
              cell.style.backgroundColor = "yellow";
              selectedSlots.push({ room: room.id, hour: i });
          
              // Sort selectedSlots by hour
              selectedSlots.sort((a, b) => a.hour - b.hour);
          
              // Look for any 1+ hour gaps and trim earlier slots
              for (let j = 1; j < selectedSlots.length; j++) {
                if (selectedSlots[j].hour - selectedSlots[j - 1].hour > 1) {
                  // Gap found: remove slots before the gap
                  const invalidSlots = selectedSlots.slice(0, j);
                  invalidSlots.forEach(slot => {
                    const selector = `td`; // You can add class/id or data attributes to target more precisely
                    const cells = document.querySelectorAll(selector);
                    cells.forEach(c => {
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
              // Deselect slot
              cell.style.backgroundColor = "green";
              selectedSlots = selectedSlots.filter(slot => !(slot.room === room.id && slot.hour === i));
          
              // If no more selected, reset selectedRoomId
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

// Function to generate time slots (from 8 AM to 8 PM, in 1-hour intervals)
function generateTimeSlots() {
  const timeSlots = [];
  const startHour = 8;  // Start at 8 AM
  const endHour = 20;   // End at 8 PM

  for (let hour = startHour; hour < endHour; hour++) {
      timeSlots.push(hour);  // Add each hour as a time slot
  }

  return timeSlots;
}

// Check if the time slot for a booking matches the current time slot
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
function closeOverlay() {
  const overlay = document.getElementById("bookingOverlay");
  overlay.classList.remove("active");
}
