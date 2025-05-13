document.getElementById("enterRoomBtn").addEventListener("click", async () => {
  const roomCode = document.getElementById("roomCodeInput").value;
  const room = document.getElementById("roomSelect").value
  const datetime = document.getElementById("dateSelect").value


  if (roomCode || room || datetime) {
    await enterRoom(roomCode, room, datetime);
    document.getElementById("roomCodeInput").value = ""; 
  } else {
    alert("Please enter a valid room code, room and date time");
  }
});
document.getElementById("dateSelect").addEventListener("change", async () => {
    let date = document.getElementById("dateSelect").value
    let response = await fetch("/booking/get_rooms", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        }
    });
    console.log(date)
    let data = await response.json();
    console.log(data)
    let rooms = data.rooms;
    let buildings = data.buildings;
    let roomList = document.getElementById("roomSelect");
    rooms.forEach(room => {
        let option = document.createElement("option");
        option.innerHTML = room.name;
        option.value = room.name;
        roomList.appendChild(option);
    });
});

async function enterRoom(room_code, room_id, datetime) {
    const date = new Date(datetime);
    const timestamp = Math.floor(date.getTime() / 1000);
    try {
        const response = await fetch(`/booking/enter_room?room_code=${room_code}&room_id=${room_id}&datetime=${timestamp}`)

        if (!response.ok) {
            const error = await response.json();
            alert("Error: " + error.detail);
            return;
        }

        const data = await response.json();
        alert("Success: " + data.message);
    } catch (err) {
        console.error("Failed to enter room:", err);
        alert("Network error while entering room.");
    }
}