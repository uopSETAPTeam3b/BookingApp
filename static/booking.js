async function onload() {
    const token = localStorage.getItem("token");
    if (!token) {
        alert("No token found. Please log in.");
        window.location.href = "/Auth_Page";  // Redirect to login page
        return;
    }
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
          console.error("Error fetching bookings:", response.statusText);
          alert("Error fetching bookings: " + response.statusText);
      }
  } catch (error) {
      console.error("Network error:", error);
      alert("Network error: " + error);
  }
}

// Function to display the bookings on the webpage
function displayBookings(bookings) {
  const bookingsList = document.getElementById('bookings-list');
  
  // Clear the list before adding new bookings
  bookingsList.innerHTML = "";

  // Loop through each booking and display it
  bookings.forEach(booking => {
      const listItem = document.createElement('li');
      listItem.classList.add('booking-item');
      listItem.innerHTML = `
          <strong>Booking ID:</strong> ${booking.booking_id} <br>
          <strong>Building:</strong> ${booking.building_name} <br>
          <strong>Room Type:</strong> ${booking.room_type} <br>
          <strong>Start Time:</strong> ${booking.start_time} <br>
          <strong>Duration:</strong> ${booking.duration} <br>
          <strong>Access Code:</strong> ${booking.access_code} <br>
      `;
      bookingsList.appendChild(listItem);
  });
}

document.addEventListener('DOMContentLoaded', onload);