// async function openChat(otherId, otherName) {
//     currentOther = otherId;

//     // Update global variables
//     window.receiverId = otherId;
//     window.receiverName = otherName;

//     // 1. JOIN SOCKET ROOM
//     socket.emit("join", {
//         user_id: currentUserId,
//         other_id: otherId
//     });

//     // 2. Update header
//     const headerName = document.querySelector('.user-message-header .user-name-label p:first-child');
//     if (headerName) {
//         headerName.textContent = otherName;
//     }

//     // 3. LOAD CHAT MESSAGES
//     try {
//         const res = await fetch(`/api/chat/${otherId}`);
//         const data = await res.json();
        
//         // Clear and populate messages
//         const messagesSection = document.querySelector('.user-message-container .message');
//         if (messagesSection) {
//             messagesSection.innerHTML = ''; // Clear old messages
            
//             let chatBox = document.createElement('div');
//             chatBox.className = 'chat-box';  // ✅ Use class, not id
            
//             // Add all messages
//             data.messages.forEach(m => {
//                 const msgDiv = document.createElement('div');
//                 msgDiv.className = `msg ${m.sender_id.$oid === currentUserId ? 'sent' : 'received'}`;
//                 msgDiv.innerHTML = `
//                     <p>${escapeHtml(m.message)}</p>     
//                     <p class="time">${new Date(m.timestamp.$date).toLocaleString("en-IN", { timeZone: "Asia/Kolkata",hour: "2-digit",minute: "2-digit",hour12: true })}</p>
//                 `;

//                 chatBox.appendChild(msgDiv);
//             });
            
//             messagesSection.appendChild(chatBox);
            
//             // Scroll to bottom
//             messagesSection.scrollTop = messagesSection.scrollHeight;
//         }
        
//         // Check user status
//         if (typeof checkUserStatus === 'function') {
//             checkUserStatus(otherId);
//         }
        
//         console.log('Chat opened for:', otherName, otherId);
        
//     } catch (error) {
//         console.error('Error loading chat:', error);
//     }
// }

// function escapeHtml(text) {
//     const div = document.createElement('div');
//     div.textContent = text;
//     return div.innerHTML;
// }

// function dateTimeSet(utcDate){
//     if(utcDate){
//         const dateObj = new Date(utcDate);

//         return dateObj.toLocaleDateString("en-IN",{
//             timeZone : "Asia/Kolkata",
//             day : "2-digit",
//             month : 'short',
//             year : "numeric"
//         });
//     }
//     return "";
// }

// // alert(dateTimeSet("2025-12-20T09:37:21.502392Z") === dateTimeSet("2024-12-20T09:37:21.502392Z"))