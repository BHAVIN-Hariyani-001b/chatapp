let loginPassword = document.querySelector("#password");
let loginEmail = document.querySelector("#login-email");
let eyeBtn = document.querySelector(".input-container button");
let loginBtn = document.querySelector(".login-btn .btn");

loginPassword.addEventListener("input", () => {
  if (loginPassword.value.length > 0) {
    eyeBtn.style.display = "flex";
    eyeBtn.innerHTML = '<i class="fa-regular fa-eye-slash"></i>';
  } else {
    eyeBtn.style.display = "none";
  }
  checkFromFild();
});

eyeBtn.addEventListener("click", () => {
  if (loginPassword.type === "password") {
    loginPassword.type = "text";
    eyeBtn.innerHTML = '<i class="fa-regular fa-eye"></i>';
  } else {
    loginPassword.type = "password";
    eyeBtn.innerHTML = '<i class="fa-regular fa-eye-slash"></i>';
  }
});

function checkFromFild() {
  if (loginPassword.value.trim() !== "" && loginEmail.value.trim() !== "") {
    loginBtn.disabled = false;
  } else {
    loginBtn.disabled = true;
  }
}
