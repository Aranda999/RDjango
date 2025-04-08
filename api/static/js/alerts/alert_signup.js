document.addEventListener('DOMContentLoaded', function () {
    const messageDiv = document.getElementById('error-message');
    if (messageDiv && messageDiv.innerText.trim() !== '') {
        // Mensaje alert
        const messages = messageDiv.querySelectorAll('.alert');
        messages.forEach(message => {
            console.log('Mensaje:', message.innerText);
        });
        // Ocultar el mensaje después de 5 segundos
        setTimeout(() => {
            messageDiv.style.display = 'none';
        }, 5000);
    }
});

