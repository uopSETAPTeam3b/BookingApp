async function onload() {
    const homeButton = document.getElementById("homebutton");
    const bookButton = document.getElementById("bookbutton");
    const bookingsButton = document.getElementById("bookings");
    const loginButton = document.getElementById("loginout");

    homeButton.addEventListener("click", () => {
        window.location.href = "/home";
    });
    bookButton.addEventListener("click", () => {
        window.location.href = "/book";
    });
    bookingsButton.addEventListener("click", () => {
        window.location.href = "/booking";
    });
    loginButton.addEventListener("click", async () => {
        if (loginButton.innerText === "Logout") {
            
            loginButton.innerText = "Login";
            document.getElementById("userImage").style.display = 'none';
            await fetch('/account/logout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token: localStorage.getItem("token") })
            });
            localStorage.removeItem("token");
            try {
                const bookingsList = document.getElementById('bookingList');
                console.log("Bookings:", bookings);  // Debug log
              
                bookingsList.innerHTML = ""; // Clear existing list
                const listItem = document.createElement('li');
                listItem.innerHTML = "You are not logged in. Please log in to view your bookings.";
                bookingsList.appendChild(listItem);
            } catch (error) {
                console.error("Error clearing booking list:", error);
            }
            
            
        } else {
            window.location.href = "/login";
        }
        
        
       
    });
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
            } else {
                loginButton.innerText = "login";
                document.getElementById("userImage").style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error fetching user data:', error);
            // Handle error
        });
        
        
    } else {
        loginButton.innerText = "Login";
    }
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
document.addEventListener('DOMContentLoaded', onload);
