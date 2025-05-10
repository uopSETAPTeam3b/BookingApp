document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("forgot-password-modal");
  const forgotPasswordLink = document.getElementById("forgot-password-link");
  const closeBtn = document.querySelector(".close");
  const backupCodeOption = document.getElementById("backup-code-option");
  const emailOption = document.getElementById("email-option");
  const backupCodeForm = document.getElementById("backup-code-form");
  const emailForm = document.getElementById("email-form");

  if (!forgotPasswordLink || !modal || !closeBtn) {
    console.error("Required elements not found");
    return;
  }

  forgotPasswordLink.addEventListener("click", (e) => {
    e.preventDefault();
    console.log("Forgot Password link clicked");
    modal.style.display = "flex";
  });

  closeBtn.addEventListener("click", () => {
    modal.style.display = "none";
  });

  window.addEventListener("click", (event) => {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  });

  backupCodeOption.addEventListener("click", () => {
    backupCodeOption.classList.add("active");
    emailOption.classList.remove("active");
    emailForm.classList.remove("active");
    setTimeout(() => {
      backupCodeForm.classList.add("active");
    }, 50);
  });

  emailOption.addEventListener("click", () => {
    emailOption.classList.add("active");
    backupCodeOption.classList.remove("active");
    backupCodeForm.classList.remove("active");
    setTimeout(() => {
      emailForm.classList.add("active");
    }, 50);
  });
});
