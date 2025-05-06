
import { checkLoggedInExpt } from "./nav.js";
async function onload() {
    const token = localStorage.getItem("token");
    console.log("Token:", token);
    const loginButton = document.getElementById("loginout");
    const loggedStatus = await checkLoggedInExpt(token)
    if (!loggedStatus || token === undefined) {
        console.log("User is not logged in");
        const bookingsList = document.getElementById('bookingList');
        console.log("Bookings:", bookings);  // Debug log
        loginButton.innerText = "Login";
        document.getElementById("userImage").style.display = 'none';
        bookingsList.innerHTML = ""; // Clear existing list
        const listItem = document.createElement('li');
        listItem.innerHTML = "You are not logged in. Please log in to view your bookings.";
        bookingsList.appendChild(listItem);
        return;
    }
    loginButton.innerText = "Logout";
    document.getElementById("userImage").style.display = 'block';
    fetchBookings(token);  // Fetch bookings using the token

}

async function fetchBookings(token) {
  try {
      const response = await fetch('/booking/get_bookings', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({ token: token })  // Send token in the request body
      });

      if (response.ok) {
          const data = await response.json();  // Parse the JSON response

          // Call a function to display the bookings
          displayBookings(data.bookings);  // `data.bookings` contains the list of bookings
      } else {
        const bookingsList = document.getElementById('bookingList');
        bookingsList.innerHTML = ""; // Clear existing list
        const listItem = document.createElement('li');
        listItem.innerHTML = "You have no upcoming bookings.";
        bookingsList.appendChild(listItem);
        return;
      }
  } catch (error) {
      console.error("Network error:", error);
      alert("Network error: " + error);
  }
}

// Function to display the bookings on the webpage
function displayBookings(bookings) {
    const bookingsList = document.getElementById('bookingList');
    console.log("Bookings:", bookings);  // Debug log
  
    bookingsList.innerHTML = ""; // Clear existing list
  
    bookings.forEach(booking => {
      const listItem = document.createElement('li');
      listItem.classList.add('booking-item');
      // Debug log
      // Format UNIX timestamp to readable time
      const startTime = new Date(booking.time * 1000).toLocaleString();
  
      listItem.innerHTML = `
        <strong>Booking ID:</strong> ${booking.id} <br>
        <strong>Building:</strong> ${booking.building?.name || 'N/A'} <br>
        <strong>Address:</strong> ${booking.building?.address_1 || ''}, ${booking.building?.address_2 || ''} <br>
        <strong>Start Time:</strong> ${startTime} <br>
        <strong>Duration:</strong> ${booking.duration ?? 'N/A'} hour(s)<br>
        <button class="btn btn-primary" onclick="cancelBtnClick(${booking.id})">cancel</button>
        <button class="btn btn-secondary" onclick="alterBooking(${booking.id}, ${Math.floor(Date.now() / 1000) + 3600},1, ${booking.room_id})">Edit</button>
      `;
        
      bookingsList.appendChild(listItem);
    });
  }
function editBtnClick(bookingId) {
    const token = localStorage.getItem("token");

    
}

async function alterBooking(bookingId, newTime,newDuration, newRoomId) {
    const token = localStorage.getItem("token");
    openOverlay();
    try {
        const response = await fetch(`/booking/edit_booking`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                token: token,
                datetime: newTime,
                room_id: newRoomId,
                duration: newDuration,
                old_booking_id: bookingId
            })
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
        const response = await fetch('/booking/cancel', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ token: token, booking_id: bookingId })
        });

        if (!response.ok) {
            throw new Error('Failed to cancel booking');
        }

        const data = await response.json();
        fetchBookings(token);  // Refresh bookings after cancellation
    } catch (error) {
        console.error('Error cancelling booking:', error);
        // Optional: show an error message to user
    }
}
window.cancelBtnClick = cancelBtnClick;
window.alterBooking = alterBooking;
function shareBtnClick() {
    const token = localStorage.getItem("token");
    
}

document.addEventListener('DOMContentLoaded', onload);