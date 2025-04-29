async function onload() {
    console.log("onload");
    const token = localStorage.getItem("token");
    //const response = await fetch("/api/booking/get_user_bookings");
    const list = document.getElementById("bookingList");
    list.innerHTML = ""; 
    bookings = [
        {
          id: 1,
          user: { username: "alice", email: "alice@example.com" },
          room: { id: 101 },
          time: 1714380000
        },
        {
          id: 2,
          user: { username: "bob", email: "bob@example.com" },
          room: { id: 102 },
          time: 1714466400
        }
      ];
    //if (!token) {
    //    list.innerHTML = "<li>You must be logged in to view bookings.</li>";
    //    return;
    //}
    //if (!response.ok) throw new Error("Failed to fetch bookings");
    //const bookings = await response.json();
    if (bookings.length === 0) {
        list.innerHTML = "<li>No bookings found.</li>";
        return;
    }
    console.log("here");
    displayBookings(bookings);

}
function displayBookings(bookings) {
    const list = document.getElementById("bookingList");
    list.innerHTML = ""; 

    bookings.forEach(booking => {
        const li = document.createElement("li");
        const date = new Date(booking.time * 1000); // assuming `time` is UNIX timestamp in seconds
        li.textContent = `Room ${booking.room.id} | ${date.toLocaleString()} | User: ${booking.user.username}`;
        list.appendChild(li);
    });
}
console.log("here2");
document.addEventListener('DOMContentLoaded', onload);