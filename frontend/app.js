const API_BASE = 'http://localhost:5000/api';
let currentSlotId = null;

async function fetchSensorData() {
    try {
        const response = await fetch(`${API_BASE}/data`);
        const data = await response.json();

        document.getElementById('temp-val').textContent = `${data.temp.toFixed(1)} °C`;
        document.getElementById('hum-val').textContent = `${data.hum.toFixed(0)} %`;
        document.getElementById('gas-val').textContent = data.gas;

        const statusEl = document.getElementById('env-status');
        statusEl.textContent = data.status;
        statusEl.className = data.status === 'FRESH' ? 'value status-good' : 'value status-bad';

    } catch (error) {
        console.error('Error fetching sensor data:', error);
    }
}

async function fetchSlots() {
    try {
        const response = await fetch(`${API_BASE}/slots`);
        const slots = await response.json();
        renderSlots(slots);
    } catch (error) {
        console.error('Error fetching slots:', error);
    }
}

function renderSlots(slots) {
    const container = document.getElementById('slots-container');
    container.innerHTML = '';

    slots.forEach(slot => {
        const card = document.createElement('div');
        card.className = 'slot-card';

        const imagePath = slot.image_path ? slot.image_path : 'https://placehold.co/400x300?text=No+Image';
        const statusText = slot.last_checked ? (slot.is_spoiled ? 'Spoiled' : 'Fresh') : 'Unchecked';
        const statusClass = slot.last_checked ? (slot.is_spoiled ? 'status-bad' : 'status-good') : '';

        card.innerHTML = `
            <div class="slot-image-container">
                <img src="${imagePath}" alt="${slot.name}">
            </div>
            <div class="slot-info">
                <div class="slot-name">${slot.name}</div>
                <div class="slot-type">${slot.type}</div>
                <div class="slot-status ${statusClass}">${statusText}</div>
            </div>
            <button class="check-btn" onclick="triggerCamera(${slot.id})">
                Check Item
            </button>
        `;
        container.appendChild(card);
    });
}

function triggerCamera(slotId) {
    currentSlotId = slotId;
    document.getElementById('camera-input').click();
}

async function handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file || !currentSlotId) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE.replace('/api', '')}/api/upload/${currentSlotId}`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            // Ideally re-fetch slots to show new image
            fetchSlots();
            alert('Image uploaded successfully! Checking for spoilage...');
            // In a real app, this is where we'd call an AI service to check the image
        } else {
            alert('Upload failed');
        }
    } catch (error) {
        console.error('Error uploading:', error);
        alert('Error uploading image');
    }
}

// Event Listeners
document.getElementById('camera-input').addEventListener('change', handleImageUpload);

// Initial Load & Polling
fetchSlots();
fetchSensorData();
setInterval(fetchSensorData, 2000); // Update sensors every 2s
