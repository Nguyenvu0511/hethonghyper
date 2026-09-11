chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "solve_captcha") {
        fetch('http://157.66.100.11:8080/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: request.image })
        })
        .then(res => res.json())
        .then(json => {
            if (json && json.text) {
                // Ensure exactly 4 chars uppercase
                let text = json.text.trim().replace(/[^A-Za-z0-9]/g, '');
                text = text.toUpperCase().substring(0, 4);
                sendResponse({ text: text });
            } else {
                sendResponse({ text: null });
            }
        })
        .catch(err => {
            console.error("Local OCR Server Error (Fetch failed):", err.message, err);
            chrome.notifications.create({
                type: 'basic',
                iconUrl: 'icon.png',
                title: 'Lỗi Kết Nối Server ddddocr',
                message: err.message || 'Không thể kết nối tới server VPS 157.66.100.11:8080. Hãy kiểm tra lại VPS.'
            });
            sendResponse({ text: null });
        });
        return true; // Keep the message channel open for async response
    }
});