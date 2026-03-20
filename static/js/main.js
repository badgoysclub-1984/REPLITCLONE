// REPLITCLONE Main Script
function runCode() {
    const code = document.getElementById('code').value;
    console.log('Running code:', code);
    // Send to backend
    fetch('/run', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({code: code})
    });
}