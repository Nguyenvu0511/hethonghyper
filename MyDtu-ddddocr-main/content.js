// --- FILE: content.js (Bản V3.8: Fix Lỗi Trùng Biến & Tọa độ Chuẩn) ---
console.log("🚀 MyDTU: Final Position Mode!");

// 1. fix thông báo màn đen
const style = document.createElement('style');
style.textContent = `
    .darkness, #popout, #adbox { display: none !important; }
    #my-native-btn { z-index: 9999 !important; }
`;
(document.head || document.documentElement).appendChild(style);

let CONFIG = {};
let isSolving = false; 
let isConfigLoaded = false;

// 2. TẢI CẤU HÌNH
chrome.storage.sync.get(['dtu_username', 'dtu_password', 'dtu_apiKey', 'dtu_auto'], (data) => {
    CONFIG = data;
    isConfigLoaded = true;
    if (document.getElementById('txtUser')) fillCredentials();
});

// 3. QUÉT GIAO DIỆN
const scanner = setInterval(() => {
    const boxCaptcha = document.getElementById('box-captcha');
    if (boxCaptcha && !document.getElementById('my-native-btn')) {
        injectNativeButton();
        if (isConfigLoaded) fillCredentials();
    }
    if (document.body && !window.zombieRunning) {
        startZombieObserver();
        window.zombieRunning = true;
    }
}, 50);

// --- HÀM TẠO NÚT ---
function injectNativeButton() {
    const boxCaptcha = document.getElementById('box-captcha'); 
    if (!boxCaptcha) return;

    const labelSpan = boxCaptcha.querySelector('span'); 
    if (!labelSpan) return;

    const labelStyle = window.getComputedStyle(labelSpan);
    const btn = document.createElement("div"); 
    btn.id = "my-native-btn";
    btn.innerHTML = "⚡ Auto Captcha"; 
    
    boxCaptcha.style.position = "relative";

    // --- TỌA ĐỘ CHUẨN CẬU YÊU CẦU ---
    // Dịch sang trái 27px, Dịch lên trên 12px
    const leftPos = labelSpan.offsetLeft - 27;
    const topPos = (labelSpan.offsetTop + labelSpan.offsetHeight) - 12; 

    btn.style.cssText = `
        position: absolute;
        left: ${leftPos}px;
        top: ${topPos}px;
        
        font-family: ${labelStyle.fontFamily};
        font-size: 11px;
        font-weight: normal;
        
        /* Màu Trắng */
        color: #ffffff; 
        
        cursor: pointer;
        user-select: none;
        opacity: 0.9;
        white-space: nowrap;
        padding-top: 2px;
        transition: all 0.2s;
        text-shadow: 0 1px 2px rgba(0,0,0,0.5); 
    `;

    // Hiệu ứng Hover
    btn.onmouseover = () => { 
        btn.style.opacity = "1";
        btn.style.textDecoration = "underline"; 
        btn.style.color = "#ffff00"; // Vàng
        fillCredentials();
    };
    btn.onmouseout = () => { 
        btn.style.opacity = "0.9";
        btn.style.textDecoration = "none";
        btn.style.color = "#ffffff"; // Trả về Trắng
    };
    
    btn.onclick = () => {
        fillCredentials();
        btn.innerHTML = "⏳...";
        btn.style.color = "#ffbd45"; 
        runSolver(btn); 
    };

    boxCaptcha.appendChild(btn);

    // Auto Run (Đợi 3 giây để trang tải hoàn tất theo yêu cầu)
    if (CONFIG.dtu_auto) {
        setTimeout(() => {
            btn.innerHTML = "⚡ Auto...";
            btn.click(); 
        }, 3000);
    }
}

// --- GIẢI MÃ BẰNG GEMINI API SIÊU TỐC ---
function handleAutoRun() {
    if (!CONFIG.dtu_auto || isAutoRunning) return;
    isAutoRunning = true;
    
    const btn = document.getElementById('my-native-btn');
    if (btn) btn.innerHTML = "⏳ AI OCR...";
    
    executeSolver(btn, true);
}

function runSolver(btnElement) {
    if (isSolving) return; 
    isSolving = true;
    executeSolver(btnElement, false);
}

function executeSolver(btnElement, isAuto) {
    const img = document.querySelector('#UpdatePanel1 img') || document.querySelector('img[src*="CaptchaImage.axd"]');
    const input = document.getElementById('txtCaptcha');

    if (!img || !input) { 
        isSolving = false; 
        if(isAuto) isAutoRunning = false; 
        return; 
    }

    // Đảm bảo ảnh Captcha đã tải xong 100% trước khi đọc, tránh đọc ảnh rỗng khi vừa Đăng xuất
    if (!img.complete || img.naturalWidth === 0) {
        img.onload = () => {
            isSolving = false;
            executeSolver(btnElement, isAuto);
        };
        return;
    }

    const canvas = document.createElement("canvas");
    canvas.width = img.naturalWidth;
    canvas.height = img.naturalHeight;
    canvas.getContext("2d").drawImage(img, 0, 0);
    // Giữ nguyên chất lượng ảnh để ddddocr đọc được chính xác nhất
    const base64Str = canvas.toDataURL("image/png").replace(/^data:image\/(png|jpg|jpeg);base64,/, "");

    // Gửi ảnh Base64 cho background.js để nó gọi server nội bộ (Tránh lỗi Mixed Content HTTPS -> HTTP)
    chrome.runtime.sendMessage({ action: "solve_captcha", image: base64Str }, (response) => {
        isSolving = false; 
        if (isAuto) isAutoRunning = false;

        if (response && response.text) {
            input.value = response.text;
            if (btnElement) {
                btnElement.innerHTML = "✅ " + response.text;
                btnElement.style.color = "#76ff03"; // Xanh lá
            }

            if (CONFIG.dtu_auto) {
                setTimeout(() => {
                    fillCredentials();
                    document.getElementById('btnLogin1')?.click();
                }, 200);
            }
        } else {
            handleOcrError(btnElement, isAuto);
        }
    });
}

function handleOcrError(btnElement, isAuto) {
    if (btnElement) {
        btnElement.innerHTML = "❌ Lỗi v2";
        btnElement.style.color = "#ff4d4d"; // Đỏ
    }
    // Nếu Auto-login đang bật, tự động reset tải lại captcha mới để thử lại
    if (isAuto && CONFIG.dtu_auto) {
        setTimeout(() => {
            const refreshBtn = document.getElementById('btnRefresh');
            if (refreshBtn) refreshBtn.click();
        }, 1500);
    }
}

// --- HÀM HỖ TRỢ ---
function fillCredentials() {
    const userField = document.getElementById('txtUser');
    const passField = document.getElementById('txtPass');
    if (!userField || !passField) return;
    if (!CONFIG.dtu_username && !CONFIG.dtu_password) return;
    
    const forceFill = (el, val) => {
        if (!el || !val) return;
        el.focus(); el.value = val;
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
    };
    if (CONFIG.dtu_username) forceFill(userField, CONFIG.dtu_username);
    if (CONFIG.dtu_password) forceFill(passField, CONFIG.dtu_password);
}

function startZombieObserver() {
    const observer = new MutationObserver((mutations) => {
        if (!document.getElementById('my-native-btn')) injectNativeButton();
        for (const mutation of mutations) {
            if (mutation.type === 'childList' && mutation.target.id === 'UpdatePanel1') {
                console.log("♻️ Captcha mới...");
                if (CONFIG.dtu_auto && !isSolving) {
                    setTimeout(() => {
                        const btn = document.getElementById('my-native-btn');
                        if (btn) {
                            btn.innerHTML = "♻️ Thử lại...";
                            runSolver(btn);
                        }
                    }, 500);
                } else { setTimeout(fillCredentials, 500); }
            }
        }
    });
    observer.observe(document.body, { childList: true, subtree: true });
}

document.addEventListener('mouseover', (e) => {
    const t = e.target;
    if (t && (t.id === 'btnLogin1' || t.id === 'my-native-btn')) fillCredentials();
}, true);