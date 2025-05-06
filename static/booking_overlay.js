const rooms = ["Room A", "Room B", "Room C"];
const startHour = 8;
const endHour = 20;

function buildBookingTable() {
    const table = document.getElementById("booking-table");
    const headerRow = table.querySelector("thead tr");
    const tbody = document.getElementById("booking-body");
  
    // Clear previous content
    headerRow.innerHTML = "<th>Room / Time</th>";
    tbody.innerHTML = "";
  
    for (let hour = startHour; hour <= endHour; hour++) {
      const th = document.createElement("th");
      th.textContent = `${hour}:00`;
      headerRow.appendChild(th);
    }
  
    rooms.forEach((room) => {
      const row = document.createElement("tr");
      const roomCell = document.createElement("td");
      roomCell.textContent = room;
      row.appendChild(roomCell);
  
      for (let hour = startHour; hour <= endHour; hour++) {
        const cell = document.createElement("td");
        cell.textContent = "";
        cell.onclick = () => alert(`Clicked ${room} at ${hour}:00`);
        row.appendChild(cell);
      }
      tbody.appendChild(row);
    });
}
  

function openOverlay() {
    const overlay = document.getElementById("bookingOverlay");
    overlay.classList.add("active");
    buildBookingTable();
}


function closeOverlay() {
  document.getElementById("bookingOverlay").classList.remove("active");
}
  

// Build table on load
window.addEventListener("DOMContentLoaded", buildBookingTable);
