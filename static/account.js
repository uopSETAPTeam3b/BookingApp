document.addEventListener("DOMContentLoaded", async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        alert("User not logged in");
        return;
      }
  
      const response = await fetch(`/account/accountDetails?token=${token}`);
      const data = await response.json();
  
      if (!response.ok) {
        alert(data.message || "Failed to load account details.");
        return;
      }
  
      // Fill general account info
      document.getElementById("user-email").textContent = data.email || "";
      document.getElementById("user-username").textContent = data.username || "";
      document.getElementById("user-phone").textContent = data.phone_number || "";
      document.getElementById("user-university").textContent = data.university || "None";
      document.getElementById("user-strikes").textContent = data.strikes ?? "0";
  
      // If user is admin, show university access requests
      if (data.role === "admin") {
        document.getElementById("admin-section").style.display = "block";
        console.log("Admin section visible");
  
        const list = document.getElementById("university-access-list");
        list.innerHTML = ""; // Clear any existing content
        if (!data.university_requests) {
          const li = document.createElement("li");
          li.textContent = "No university access requests.";
          list.appendChild(li);
        } else {
          data.university_requests.forEach((request) => {
            const li = document.createElement("li");
            li.textContent = `${request.username} (${request.email})`;
            const acceptButton = document.createElement("button");
            acceptButton.textContent = "Accept";
            acceptButton.onclick = () => handleAcceptRequest(request.id);
            li.appendChild(acceptButton);
            list.appendChild(li);
          });
        }
        
      }
    } catch (error) {
      console.error("Error loading account details:", error);
      alert("An error occurred loading your account.");
    }
  });
  
  function handleAcceptRequest(requestId) {
    // Add logic to send POST or PATCH to backend to accept the user
    console.log("Accept clicked for request ID:", requestId);
    // Example:
    // fetch('/acceptUser', { method: 'POST', body: JSON.stringify({ requestId }) })
  }
  