// static/js/telematics.js
const deviceId = "USER_DEVICE_ID"; 
const socket = new WebSocket(
    `ws://${window.location.host}/ws/telematics/${deviceId}/`
);

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    updateDashboard(data);
};

function updateDashboard(data) {
    // Update your real-time dashboard
    document.getElementById('speed').innerText = data.speed;
    document.getElementById('acceleration').innerText = data.acceleration;
    // ... other updates
}