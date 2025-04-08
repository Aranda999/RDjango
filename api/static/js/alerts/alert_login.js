document.addEventListener('DOMContentLoaded', function () {
    const errorMessage = document.getElementById('error-message');
    if (errorMessage.innerText.trim() !== '') {
        // mensaje alert
        console.log('Error:', errorMessage.innerText);
        //ocultar el mensaje después de 5 segundos
        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 5000);
    }
});