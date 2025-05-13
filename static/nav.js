async function onload() {
    const homeButton = document.getElementById("homebutton");
    const bookButton = document.getElementById("bookbutton");
    const bookingsButton = document.getElementById("bookings");
    const loginButton = document.getElementById("loginout");
    const userImage = document.getElementById("userImage");
    userImage.addEventListener("click", () => {
        window.location.href = "/account";
    });
    homeButton.addEventListener("click", () => {
        window.location.href = "/welcome";
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
                console.log("Bookings:", bookings); 
              
                bookingsList.innerHTML = ""; 
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
    const loggedIn = await checkLoggedInExpt();
    if (loggedIn) {
        loginButton.innerText = "Logout";
        document.getElementById("userImage").style.display = 'block';
    }
    else {
        loginButton.innerText = "Login";
        document.getElementById("userImage").style.display = 'none';
    }
}
export async function checkLoggedInExpt() {
    const token = localStorage.getItem("token");

    if (token) {
        try {
            const response = await fetch(`/account/me?token=${token}`, {
                method: 'GET'
            });
            const user = await response.json();
            if (user.message !== "Invalid token") {
                return true;  // User is logged in
            } else {
                return false;  // User is not logged in
            }
        } catch (error) {
            console.error('Error fetching user data:', error);
            return false;  // Error occurred, treat as not logged in
        }
    } else {
        return false;  // No token found, treat as not logged in
    }
}

async function checkLoggedIn() {
    const token = localStorage.getItem("token");
    if (token) {
        await fetch('/account/me', {
            method: 'GET',
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
