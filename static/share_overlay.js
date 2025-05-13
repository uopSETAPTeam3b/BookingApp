export function showShareOverlay(bookingId, shareCode) {
    document.getElementById("booking_id").textContent = `#${bookingId}`;
    document.getElementById("shareCode").textContent = ("Booking Share Code: " + shareCode );
    document.getElementById("shareOverlay").style.display = "flex";
  }
  
  document.getElementById("closeOverlayBtn").addEventListener("click", () => {
    console.log("Close button clicked");
    document.getElementById("shareOverlay").style.display = "none";
  });
  
  document.getElementById("goToBookingsBtn").addEventListener("click", () => {
    window.location.href = "/booking";
  });
  
  document.getElementById("confirmShareBtn").addEventListener("click", () => {
    document.getElementById("shareOverlay").style.display = "none";
  });
  