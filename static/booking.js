import { checkLoggedInExpt } from "./nav.js";
import { showCancelledOverlay } from "./booking_cancelled_overlay.js";
import { showShareOverlay } from "./share_overlay.js";
async function onload() {
  const token = localStorage.getItem("token");
  console.log("Token:", token);
  const loginButton = document.getElementById("loginout");
  const loggedStatus = await checkLoggedInExpt(token);

  const addSharedBtn = document.getElementById("addSharedBtn");
  addSharedBtn.addEventListener("click", add_share_click);
  console.log("Bookings:", bookings); 

  if (!loggedStatus || token === undefined) {
    console.log("User is not logged in");
    const bookingsList = document.getElementById("bookingList");
   
    loginButton.innerText = "Login";
    document.getElementById("userImage").style.display = "none";
    bookingsList.innerHTML = ""; 
    const listItem = document.createElement("li");
    listItem.innerHTML =
      "You are not logged in. Please log in to view your bookings.";
    bookingsList.appendChild(listItem);
    return;
  }
  loginButton.innerText = "Logout";
  document.getElementById("userImage").style.display = "block";
  fetchBookings(token); 
}
async function addSharedBooking(shareCode){
  const token = localStorage.getItem("token");
  try {
    const response = await fetch(`/booking/share_booking_via_code?token=${token}&share_code=${shareCode}`)

    if (response.ok) {
      const data = await response.json();
      console.log("Booking added successfully:", data);
      fetchBookings(token); 
    } else {
      throw new Error("Failed to add shared booking");
    }
  } catch (error) {
    console.error("Error adding shared booking:", error);
    alert("Failed to add shared booking: " + error.message);
  }
}
async function add_share_click(){
  console.log("Add shared booking button clicked");
  const shareCodeInput = document.getElementById("shareCodeInput");
  const shareCode = shareCodeInput.value;
  console.log("Share code:", shareCode);
  if (shareCode) {
    await addSharedBooking(shareCode);
    shareCodeInput.value = ""; 
  } else {
    alert("Please enter a valid share code.");
  }
}
async function fetchBookings(token) {
  try {
    const response = await fetch("/booking/get_bookings", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ token: token }), 
    });

    if (response.ok) {
      const data = await response.json(); 

      
      displayBookings(data.bookings); 
    } else {
      const bookingsList = document.getElementById("bookingList");
      bookingsList.innerHTML = ""; 
      const listItem = document.createElement("li");
      listItem.innerHTML = "You have no upcoming bookings.";
      bookingsList.appendChild(listItem);
      return;
    }
  } catch (error) {
    console.error("Network error:", error);
    alert("Network error: " + error);
  }
}


function displayBookings(bookings) {
  const bookingsList = document.getElementById("bookingList");
  console.log("Bookings:", bookings); 
  

  bookingsList.innerHTML = ""; 

  bookings.forEach((booking) => {
    const listItem = document.createElement("li");
    listItem.classList.add("booking-item");
    
    
    const startTime = new Date(booking.time * 1000).toLocaleString();
    if (booking.time + (59 * 60) < Math.floor(Date.now() / 1000)) {
      console.log("Past booking:", booking);
      listItem.classList.add("past-booking");
      listItem.innerHTML = `
        <strong>Booking ID:</strong> ${booking.id} <br>
        <strong>Building:</strong> ${booking.building?.name || "N/A"} <br>
        <strong>Address:</strong> ${booking.building?.address_1 || ""}, ${booking.building?.address_2 || ""} <br>
        <strong>Access Code:</strong> ${booking.access_code} <br>
        <strong>Start Time:</strong> ${startTime} <br>
        <strong>Duration:</strong> ${booking.duration ?? "N/A"} hour(s)<br>
        <button class="btn btn-primary" onclick="cancelBtnClick(${
          booking.id
        })">cancel</button>
        <button class="btn btn-secondary" onclick="editBtnClick(${
          booking.id
        }, ${Math.floor(Date.now() / 1000) + 3600},1, ${
        booking.room_id
        })">Edit</button>
        <button class="btn btn-secondary" onclick="shareBtnClick(${booking.id}, '${booking.share_code}')">Share</button>

      `;
    } else if(booking.shared === true){
      listItem.classList.add("shared");
      listItem.innerHTML = `
        <strong>Booking ID:</strong> ${booking.id} <br>
        <strong>Building:</strong> ${booking.building?.name || "N/A"} <br>
        <strong>Address:</strong> ${booking.building?.address_1 || ""}, ${booking.building?.address_2 || ""} <br>
        <strong>Access Code:</strong> ${booking.access_code} <br>
        <strong>Start Time:</strong> ${startTime} <br>
        <strong>Duration:</strong> ${booking.duration ?? "N/A"} hour(s)<br>
      `;

    } else {
      listItem.innerHTML = `
        <strong>Booking ID:</strong> ${booking.id} <br>
        <strong>Building:</strong> ${booking.building?.name || "N/A"} <br>
        <strong>Address:</strong> ${booking.building?.address_1 || ""}, ${booking.building?.address_2 || ""} <br>
        <strong>Access Code:</strong> ${booking.access_code} <br>
        <strong>Start Time:</strong> ${startTime} <br>
        <strong>Duration:</strong> ${booking.duration ?? "N/A"} hour(s)<br>
        <button class="btn btn-primary" onclick="cancelBtnClick(${
          booking.id
        })">cancel</button>
        <button class="btn btn-secondary" onclick="editBtnClick(${
          booking.id
        }, ${Math.floor(Date.now() / 1000) + 3600},1, ${
        booking.room_id
        })">Edit</button>
        <button class="btn btn-secondary" onclick="shareBtnClick(${booking.id}, '${booking.share_code}')">Share</button>

      `;
    }
    console.log(booking.share_code)
    

    bookingsList.appendChild(listItem);
  });
}
function shareBtnClick(bookingId, shareCode) {
  showShareOverlay(bookingId, shareCode);
}
function editBtnClick(bookingId) {
  const token = localStorage.getItem("token");
  openOverlay(bookingId);
}

async function alterBooking(bookingId, newTime, newDuration, newRoomId) {
  const token = localStorage.getItem("token");

  try {
    const response = await fetch(`/booking/edit_booking`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        token: token,
        datetime: newTime,
        room_id: newRoomId,
        duration: newDuration,
        old_booking_id: bookingId,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to edit booking");
    }

    const result = await response.json();
    console.log("Booking edited successfully:", result);
    fetchBookings(token);
  } catch (error) {
    console.error("Error editing booking:", error);
    alert("Failed to edit booking: " + error.message);
  }
}

async function cancelBtnClick(bookingId) {
  console.log("Cancel button clicked for booking ID:", bookingId);
  const token = localStorage.getItem("token");
  try {
    const response = await fetch("/booking/cancel", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ token: token, booking_id: bookingId }),
    });

    if (!response.ok) {
      throw new Error("Failed to cancel booking");
    }

    const data = await response.json();
    showCancelledOverlay(bookingId);
    fetchBookings(token); 
  } catch (error) {
    console.error("Error cancelling booking:", error);
    
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
window.cancelBtnClick = cancelBtnClick;
window.editBtnClick = editBtnClick;
window.shareBtnClick = shareBtnClick;
document.addEventListener("DOMContentLoaded", onload);
