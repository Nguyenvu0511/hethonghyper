// --- FILE: options.js ---

// Load cài đặt cũ
document.addEventListener('DOMContentLoaded', () => {
    chrome.storage.sync.get(['dtu_username', 'dtu_password', 'dtu_auto'], (items) => {
        if (items.dtu_username) document.getElementById('username').value = items.dtu_username;
        if (items.dtu_password) document.getElementById('password').value = items.dtu_password;
        document.getElementById('autoLogin').checked = items.dtu_auto === true;
    });
});

// Lưu khi gạt nút Auto
const autoSwitch = document.getElementById('autoLogin');
autoSwitch.addEventListener('change', () => {
    const isAuto = autoSwitch.checked;
    chrome.storage.sync.set({ dtu_auto: isAuto }, () => {
        showStatus(isAuto ? "▶ Đã bật ฅ^•ﻌ•^" : "⏸ Đã tắt ^•ﻌ•^ฅ", isAuto ? "green" : "#666");
    });
});

// Lưu khi bấm nút Save
document.getElementById('saveBtn').addEventListener('click', () => {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;

    chrome.storage.sync.set({
        dtu_username: username,
        dtu_password: password
    }, () => {
        showStatus("✔  Đã lưu thành công! 𝑴𝒆𝒐𝒘. ฅ(•- •マ", "green");
    });
});

function showStatus(text, color) {
    const status = document.getElementById('status');
    status.textContent = text;
    status.style.color = color;
    status.style.opacity = '1';
    setTimeout(() => { 
        status.style.transition = "opacity 0.5s";
        status.style.opacity = '0'; 
    }, 2000);
}