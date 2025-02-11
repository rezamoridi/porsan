
// Sidebar Toggle for Mobile
const menuToggle = document.getElementById('menu-toggle');
const sidebar = document.getElementById('sidebar');
menuToggle.addEventListener('click', () => {
    sidebar.classList.toggle('hidden');
});

// Date and Time Update
function updateDateTime() {
    const datetimeElement = document.getElementById('datetime');
    const now = new Date();
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' };
    datetimeElement.textContent = now.toLocaleDateString('en-US', options);
}




// Update every second
setInterval(updateDateTime, 1000);
updateDateTime(); // Initial call
