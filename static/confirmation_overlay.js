export function showConfirmationOverlay(bookingId, bookingDetails) {
  document.getElementById("confirm-booking-id").textContent = `#${bookingId}`;
  const body = document.getElementById("confirmation-body");
  body.innerHTML = "";

  bookingDetails.forEach((detail) => {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.textContent = `${detail.room} | ${detail.time}`;
    tr.appendChild(td);
    body.appendChild(tr);
  });

  document.getElementById("confirmationOverlay").style.display = "flex";
}

document
  .getElementById("closeConfirmationBtn")
  .addEventListener("click", () => {
    document.getElementById("confirmationOverlay").style.display = "none";
  });

document.getElementById("goToBookingsBtn").addEventListener("click", () => {
  window.location.href = "/booking";
});

document.getElementById("bookMoreBtn").addEventListener("click", () => {
  document.getElementById("confirmationOverlay").style.display = "none";
});
