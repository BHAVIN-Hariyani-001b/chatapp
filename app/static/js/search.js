let clearSearch = document.querySelector("#clear-search");
let searchInput = document.querySelector("#search");
let searchClearIcon = document.querySelector(".search-clear-icon svg");

let searchbox = document.querySelector(".user-search-list");
let userlist = document.querySelector(".user-list");
let BackBtn = document.querySelector(".Back");

clearSearch.addEventListener("click", () => {
  searchInput.value = "";
});

searchInput.addEventListener("click",(e)=>{
  e.focus();
})

searchInput.addEventListener("keyup", () => {
  if (searchbox.style.display === "none" || searchbox.style.display === "") {
    searchbox.style.display = "block";
    userlist.style.display = "none";
    BackBtn.style.display = "block";
    if (searchInput.value.length > 0 && searchInput.value.trim() !== "") {
      searchClearIcon.style.display = "flex";
    } else {
      searchClearIcon.style.display = "none";
    }
  } 

  const query = searchInput.value.trim();

  if(!query){
    searchbox.innerHTML = "";
    return;
  }

  timeout = setTimeout(async()=>{
    const response = await fetch("/search_chat",{
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query })
    });
    try {
      const data = await response.json();
      console.log(data);
      searchbox.innerHTML = "";  

      if(data.result.length > 0){
          data.result.forEach(user => {
              let a = document.createElement('div');
              a.className = "user";
              a.onclick = () => openChat(user._id, user.name);
              a.innerHTML = `
                  <div class="user-img">
                      <svg viewBox="0 0 48 48" height="212" width="212" preserveAspectRatio="xMidYMid meet" class="xh8yej3 x5yr21d x1c9tyrk xeusxvb x1pahc9y x1ertn4p x1od0jb8 x4u6w88 x1g40iwv" fill="none"><title>default-contact-refreshed</title><path d="M24 23q-1.857 0-3.178-1.322Q19.5 20.357 19.5 18.5t1.322-3.178T24 14t3.178 1.322Q28.5 16.643 28.5 18.5t-1.322 3.178T24 23m-6.75 10q-.928 0-1.59-.66-.66-.662-.66-1.59v-.9q0-.956.492-1.758A3.3 3.3 0 0 1 16.8 26.87a16.7 16.7 0 0 1 3.544-1.308q1.8-.435 3.656-.436 1.856 0 3.656.436T31.2 26.87q.816.422 1.308 1.223T33 29.85v.9q0 .928-.66 1.59-.662.66-1.59.66z" fill="#606263" class="xvt3oi1"></path></svg>
                      <span class="online-status" style="display: none;"></span>
                  </div>
                  <div class="user-name-label">
                      <p></p>
                      <p></p>
                  </div>
                  <div class='user-chat-logout follow'>
                      <button type="submit" class="${user.status}" id="btn-${user._id}" onclick="followUser('${user._id}')">${user.status}</button>
                  </div>
              `;

              const onlineStatus = a.querySelector('.online-status');
              onlineStatus.dataset.userId = user._id;
              
              const [namePara, aboutPara] = a.querySelectorAll('.user-name-label p');
              namePara.textContent = user.name || 'Unknown';
              aboutPara.textContent = user.online ? "online" : "offline" || '';
              
              searchbox.appendChild(a);
          });
          searchbox.style.display = "block";
      } else {
          searchbox.innerHTML = "<p class='no-results'>No results found</p>";
          searchbox.style.display = "block";
      }
    } catch (error) {
      console.log(error);
    }
  }, 300);
});

BackBtn.addEventListener("click", () => {
  if (userlist.style.display === "none" || userlist.style.display === "") {
    userlist.style.display = "block";
    searchbox.style.display = "none";
    BackBtn.style.display = "none";
    searchClearIcon.style.display = "none";
    searchInput.value = "";
  }
});

async function followUser(userId) {
  try{
    const response = await fetch('/follow_user',{
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body : JSON.stringify({user_id:userId})
    });
    // console.log(response);
    const result = await response.json();
    // console.log(result.message);
    // console.log(result);
    const btn = document.querySelector(`#btn-${userId}`)
    // console.log(btn);
    if (result.status === "followed") {
      btn.innerHTML = "Unfollow";
      btn.style.background = '#383b3b';
    } else if (result.status === "unfollowed") {
      btn.innerHTML = "Follow";
      btn.style.background = '#708DFF';
    }
  } catch(error){ 
    console.log(error);
  }
}


