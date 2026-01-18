const urlsField = document.getElementById('urls');
const typeDlField = document.querySelector('input[name="option"]:checked');
const alert = document.getElementById('urls-invalid');


document.getElementById('downloadForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const urlsText = urlsField.value.trim();
    const typeDl = typeDlField ? typeDlField.value : null

    if (!urlsText) {
        notification('Send one url at least', false)
        return;
    }

    const urls = urlsText.split('\n').filter(url => url.trim());
    const hasValidUrls = urls.every(url => isValidHttpUrl(url));
    if (!hasValidUrls) {
        alert.style.display = 'block';
        return;
    } else {
        alert.style.display = 'none';
    }

    try {
        const response = await fetch('/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                urls: urls,
                type_dl: typeDl
            })
        });

        if (!response.ok) {
            const data = await response.json();
            notification(`HTTP Error: ${response.status}. Message: ${data.message}`, false)
            return
        }

        const data = await response.json();

        notification(`${data["uuids"].length} download(s) started`);
        urlsField.value = '';
        if (typeDlField) typeDlField.checked = false

    } catch (error) {
        notification(`Error: ${error.message}`, false);
        console.error('Error:', error);
    }
});


function notification(text, success= true) {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");
    toast.className = `toast brutalist ${success ? 'success' : 'error'}`;

    const textElement = document.createElement("span");
    textElement.textContent = text;

    const glow = document.createElement("div");
    glow.className = "toast-glow";
    glow.style.background = "radial-gradient(circle, rgba(255,255,255,0.2), transparent 70%)";

    toast.appendChild(textElement);
    toast.appendChild(glow);
    container.appendChild(toast);

    const easing = "cubic-bezier(0.25, 1.5, 0.5, 1)";

    toast.style.animationName = 'bounce';
    toast.style.animationDuration = "0.6s";
    toast.style.animationTimingFunction = easing;
    toast.style.animationFillMode = "both";

    setTimeout(() => toast.remove(), 2000);
}

function isValidHttpUrl(string) {
    let url;

    try {
        url = new URL(string);
    } catch (_) {
        return false;
    }

    return url.protocol === "http:" || url.protocol === "https:";
}
