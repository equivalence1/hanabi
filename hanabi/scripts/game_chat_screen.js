function submit() {
    sendMessage("/send_chat_message", "user_id=" + user_id + "&message=" + document.getElementById("message").value)
}