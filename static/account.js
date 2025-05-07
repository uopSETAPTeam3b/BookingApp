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
      const universitySection = document.getElementById("university-section");

      if (data.university === null || data.university === undefined) {
          // Create dropdown
          // First name inpu
          const dropdown = document.createElement("select");
          dropdown.id = "university-select";
      
          // Sample university list (replace with your actual data)
          const universities = await fetch('/account/get_unis').then(res => res.json());
          console.log("Universities:", universities);
          universities.forEach(uni => {
              const option = document.createElement("option");
              option.value = uni.id;
              option.textContent = uni.name;
              dropdown.appendChild(option);
          });
      
          // Create request button
          const requestBtn = document.createElement("button");
          requestBtn.textContent = "Request";
  
          requestBtn.onclick = async () => {
            const universityId = parseInt(dropdown.value); // Assuming this is your university dropdown
            const token = localStorage.getItem("token");   // Adjust if stored differently
        
            if (isNaN(universityId)) {
                alert("Please select a university.");
                return;
            }
        
            try {
                const res = await fetch(`/account/add_uni_user?token=${token}&uni_id=${universityId}`, {
                    method: "POST"
                });
        
                const result = await res.json();
        
                if (res.ok) {
                    alert("Request submitted successfully!");
                    requestBtn.disabled = true;
                } else {
                    alert("Error: " + result.message);
                }
            } catch (err) {
                console.error(err);
                alert("Failed to submit request.");
            }
        };
          // Append all elements to sectio
          universitySection.appendChild(dropdown);
          universitySection.appendChild(requestBtn);
      } else {
          universitySection.textContent = data.university;
      }
      document.getElementById("user-university").textContent = data.university || "None";
      document.getElementById("user-strikes").textContent = data.strikes ?? "0";
  
      // If user is admin, show university access requests
      if (data.role === "admin") {
        document.getElementById("admin-section").style.display = "block";
        console.log("Admin section visible");
        const response = await fetch(`/account/get_uni_requests?token=${token}&uni_id=${data.university_id}`);
        const uniData = await response.json();
        if (!response.ok) {
          alert(uniData.message || "Failed to load university access requests.");
          return;
        }
        const list = document.getElementById("university-access-list");
        list.innerHTML = ""; // Clear any existing content
        console.log("University Data:", uniData);
        
        const pendingRequests = uniData.filter(request => request.status === 0);
        
        if (pendingRequests.length === 0) {
          const li = document.createElement("li");
          li.textContent = "No university access requests.";
          list.appendChild(li);
        } else {
          pendingRequests.forEach((request) => {
            const li = document.createElement("li");
            li.textContent = `${request.username} (${request.email})`;
            const acceptButton = document.createElement("button");
            acceptButton.textContent = "Accept";
            acceptButton.onclick = () => handleAcceptRequest(request.id, data.university_id); // Make sure request.id exists
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
  
  function handleAcceptRequest(user_id, university_id) {
    const token = localStorage.getItem("token");
    fetch(`/account/accept_uni_request?token=${token}&user_id=${user_id}&university_id=${university_id}`, {
        method: "POST"
    })
      .then(response => response.json())
      .then(data => {
        if (data.message === "Request accepted") {
          alert("Request accepted successfully!");
          // Optionally, refresh the list or remove the accepted request from the UI
        } else {
          alert("Error accepting request: " + data.message);
        }
      })
      .catch(error => {
        console.error("Error accepting request:", error);
        alert("Failed to accept request.");
      });
  }
  