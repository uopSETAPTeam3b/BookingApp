export function showCancelledOverlay(bookingId) {
  document.getElementById("cancelled-booking-id").textContent = `#${bookingId}`;
  const body = document.getElementById("cancelled-body");

  document.getElementById("cancelledOverlay").style.display = "flex";
}

document.getElementById("closeCancelledBtn").addEventListener("click", () => {
  document.getElementById("cancelledOverlay").style.display = "none";
});

document.getElementById("goToBookingsBtn").addEventListener("click", () => {
  window.location.href = "/booking";
});

document.getElementById("bookMoreBtn").addEventListener("click", () => {
  document.getElementById("cancelledOverlay").style.display = "none";
});
