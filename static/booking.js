
async function onload() {
    const token = localStorage.getItem("token");
    console.log("Token:", token);
    if (!checkLoggedIn(token) || token === null) {
        const bookingsList = document.getElementById('bookingList');
        console.log("Bookings:", bookings);  // Debug log
      
        bookingsList.innerHTML = ""; // Clear existing list
        const listItem = document.createElement('li');
        listItem.innerHTML = "You are not logged in. Please log in to view your bookings.";
        bookingsList.appendChild(listItem);
        return;
    }
    fetchBookings(token);  // Fetch bookings using the token

}
async function checkLoggedIn() {
    const token = localStorage.getItem("token");
    if (token) {
        await fetch('/account/me', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ token })
        })
        .then(response => response.json())
        .then(user => {
            if (user) {
                loginButton.innerText = "Logout";
                document.getElementById("userImage").style.display = 'block';
                return true;
            } else {
                loginButton.innerText = "Login";
                document.getElementById("userImage").style.display = 'none';
                return false;
            }
        })
        .catch(error => {
            console.error('Error fetching user data:', error);
            return false;
            // Handle error
        });
        
        
    } else {
        loginButton.innerText = "Login";
    }
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
    const bookingsList = document.getElementById('bookingList');
    console.log("Bookings:", bookings);  // Debug log
  
    bookingsList.innerHTML = ""; // Clear existing list
  
    bookings.forEach(booking => {
      const listItem = document.createElement('li');
      listItem.classList.add('booking-item');
  
      // Format UNIX timestamp to readable time
      const startTime = new Date(booking.time * 1000).toLocaleString();
  
      listItem.innerHTML = `
        <strong>Booking ID:</strong> ${booking.id} <br>
        <strong>Building:</strong> ${booking.building?.name || 'N/A'} <br>
        <strong>Address:</strong> ${booking.building?.address_1 || ''}, ${booking.building?.address_2 || ''} <br>
        <strong>Start Time:</strong> ${startTime} <br>
        <strong>Duration:</strong> ${booking.duration ?? 'N/A'} hour(s)<br>
      `;
  
      bookingsList.appendChild(listItem);
    });
  }

document.addEventListener('DOMContentLoaded', onload);