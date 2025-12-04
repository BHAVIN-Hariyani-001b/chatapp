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
    userListContainer.style.color = "red";
    userChatContainer.style.display = "flex";
  } else{
    userListContainer.style.display = "block";
    userChatContainer.style.display = "none";
  }
});
  




/*
<a href="/chat/${user._id}" class="user" data-user-id="{{ user._id }}">
                  <div class="user-img">
                      <svg viewBox="0 0 48 48" height="212" width="212" preserveAspectRatio="xMidYMid meet" class="xh8yej3 x5yr21d x1c9tyrk xeusxvb x1pahc9y x1ertn4p x1od0jb8 x4u6w88 x1g40iwv" fill="none"><title>default-contact-refreshed</title><path d="M24 23q-1.857 0-3.178-1.322Q19.5 20.357 19.5 18.5t1.322-3.178T24 14t3.178 1.322Q28.5 16.643 28.5 18.5t-1.322 3.178T24 23m-6.75 10q-.928 0-1.59-.66-.66-.662-.66-1.59v-.9q0-.956.492-1.758A3.3 3.3 0 0 1 16.8 26.87a16.7 16.7 0 0 1 3.544-1.308q1.8-.435 3.656-.436 1.856 0 3.656.436T31.2 26.87q.816.422 1.308 1.223T33 29.85v.9q0 .928-.66 1.59-.662.66-1.59.66z" fill="#606263" class="xvt3oi1"></path></svg>
                      <span class="online-status" data-user-id="{{ user._id }}" style="display: none;"></span>
                  </div>
                  <div class="user-name-label">
                      <p>${ user.name }</p>
                      <p>${ user._id }</p>
                  </div>
              </a> 

*/

                  // <div class="user-img">
                  //   <svg viewBox="0 0 48 48" height="212" width="212" preserveAspectRatio="xMidYMid meet" class="xh8yej3 x5yr21d x1c9tyrk xeusxvb x1pahc9y x1ertn4p x1od0jb8 x4u6w88 x1g40iwv" fill="none"><title>default-contact-refreshed</title><path d="M24 23q-1.857 0-3.178-1.322Q19.5 20.357 19.5 18.5t1.322-3.178T24 14t3.178 1.322Q28.5 16.643 28.5 18.5t-1.322 3.178T24 23m-6.75 10q-.928 0-1.59-.66-.66-.662-.66-1.59v-.9q0-.956.492-1.758A3.3 3.3 0 0 1 16.8 26.87a16.7 16.7 0 0 1 3.544-1.308q1.8-.435 3.656-.436 1.856 0 3.656.436T31.2 26.87q.816.422 1.308 1.223T33 29.85v.9q0 .928-.66 1.59-.662.66-1.59.66z" fill="#606263" class="xvt3oi1"></path></svg>
                  // </div>
                  // <div class="user-name-label">
                  //   <p>${user.name}</p>
                  // </div>
                  // <div class='user-chat-logout follow'>
                  //     <button type="submit" class="${user.status}" id="btn-${user._id}" onclick="followUser('${user._id}')">${user.status}</button>
                  // </div>

              //      <a href="/chat/${user._id}" class="user" data-user-id="{{ user._id }}">
              //     <div class="user-img">
              //       <svg viewBox="0 0 48 48" height="212" width="212" preserveAspectRatio="xMidYMid meet" class="xh8yej3 x5yr21d x1c9tyrk xeusxvb x1pahc9y x1ertn4p x1od0jb8 x4u6w88 x1g40iwv" fill="none"><title>default-contact-refreshed</title><path d="M24 23q-1.857 0-3.178-1.322Q19.5 20.357 19.5 18.5t1.322-3.178T24 14t3.178 1.322Q28.5 16.643 28.5 18.5t-1.322 3.178T24 23m-6.75 10q-.928 0-1.59-.66-.66-.662-.66-1.59v-.9q0-.956.492-1.758A3.3 3.3 0 0 1 16.8 26.87a16.7 16.7 0 0 1 3.544-1.308q1.8-.435 3.656-.436 1.856 0 3.656.436T31.2 26.87q.816.422 1.308 1.223T33 29.85v.9q0 .928-.66 1.59-.662.66-1.59.66z" fill="#606263" class="xvt3oi1"></path></svg>
              //     </div>
              //     <div class="user-name-label">
              //       <p>${user.name}</p>
              //       <p>${user.online ? "Online" : "Offline"}</p>
              //     </div>
              //     <div class='user-chat-logout follow'>
              //         <button type="submit" class="${user.status}" id="btn-${user._id}" onclick="followUser('${user._id}')">${user.status}</button>
              //     </div>
              // </a>