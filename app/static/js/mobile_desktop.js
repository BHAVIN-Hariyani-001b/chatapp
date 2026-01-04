let userListContainer = document.querySelector(".container .user-list-container")
let userChatContainer = document.querySelector(".container .user-chat-container")

let userItems = document.querySelector(".user-chat-list-container .user-list")
let BackUserChat = document.querySelector(".Back-user-chat");
let chatHide = document.querySelector(".user-child-chat-container")

userItems.addEventListener("click", (e) => {
  if(e.target.classList.contains("user") || e.target.closest(".user")){
        if(window.innerWidth <= 900){
            userListContainer.style.display = "none";
            userChatContainer.style.display = "block";
            userChatContainer.style.width = "100%";
            BackUserChat.style.display = "flex";
            document.querySelector(".user-message-container #messages").style.padding = "20px";
        } 

        if(chatHide.style.display !== "block"){
            chatHide.style.display = "block";
        }
    } 
});

let userList = document.querySelector(".user-chat-list-container .user-search-list");

userList.addEventListener("click", (e) => {
    if(e.target.closest(".user-chat-logout")){
        return;
    }

    if(e.target.classList.contains("user") || e.target.closest(".user")){
            if(window.innerWidth <= 900){
                userListContainer.style.display = "none";
                userChatContainer.style.display = "block";
                userChatContainer.style.width = "100%";
                BackUserChat.style.display = "flex";
                document.querySelector(".user-message-container #messages").style.padding = "20px";
            } 

            if(chatHide.style.display !== "block"){
                chatHide.style.display = "block";
            }
        } 
});

BackUserChat.addEventListener("click", () => {
    if(userListContainer.style.display === "none"){
        userListContainer.style.display = "block";
        userChatContainer.style.display = "none";
        BackUserChat.style.display = "none";
    } else{
        userListContainer.style.display = "none";
        userChatContainer.style.display = "block";
        BackUserChat.style.display = "flex";
    }
}); 



// popup open

let popupLogout =  document.querySelector(".user-chat-header-icon");
let popup = document.querySelector(".logout-container");

popupLogout.addEventListener("click",(e)=>{
    e.stopPropagation();
    if(popup.style.display !== "flex"){
        popup.style.display = "flex";
    } else{
        popup.style.display = "none";
    }
}); 

document.addEventListener("click",(e)=>{
    if(!popup.contains(e.target)){
        popup.style.display = "none";
    }
})


let profile = document.querySelector(".profile-edit-container");
let closeBtn = document.querySelector("#close-btn-profile")
let profileEditOpen = document.querySelector("#profile-edit-open")

closeBtn.addEventListener("click",()=>{
    if(profile.style.display === "none"){
        profile.style.display = "flex";
    } else{
        profile.style.display = "none";
    }
})


profileEditOpen.addEventListener("click",()=>{
    if(profile.style.display !== "flex"){
        profile.style.display = "flex";
    } else{
        profile.style.display = "none";
    }
})


