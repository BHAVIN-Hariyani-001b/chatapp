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

let userList = document.querySelector(".user");
let userChatContainer = document.querySelector(".user-chat-container");
let userListContainer = document.querySelector(".user-list-container");

userList.addEventListener("click", (e) => {
  if(e.target.className == "user"){
    userListContainer.style.display = "none";
    userChatContainer.style.display = "flex";
  } else{
    userListContainer.style.display = "block";
    userChatContainer.style.display = "none";
  }
});
  

