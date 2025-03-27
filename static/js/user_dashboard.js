document.addEventListener('DOMContentLoaded', function() {
    function addNotification(message, type = 'info') {
        const wrapper = document.querySelector('.notifications-wrapper');
        const notification = document.createElement('div');
        notification.className = 'notification-item';
        notification.innerHTML = `
            <i class="fas fa-${type === 'info' ? 'bell' : 'certificate'}"></i>
            <p>${message}</p>
            <span class="notification-time">Just now</span>
        `;
        wrapper.prepend(notification);
        
        // Remove notification after 5 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.5s ease-in forwards';
            setTimeout(() => notification.remove(), 500);
        }, 5000);
    }
    
    // Example usage
    setInterval(() => {
        addNotification('New notification message');
    }, 10000);
});
