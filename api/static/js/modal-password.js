// modal_cambio_contrasena.js
document.querySelector('form').addEventListener('submit', function(e) {
    var nuevaContrasena = document.getElementById('nuevaContrasena').value;
    var confirmarContrasena = document.getElementById('confirmarContrasena').value;

    if (nuevaContrasena !== confirmarContrasena) {
        e.preventDefault();
        alert('Las contraseñas no coinciden.');
    }
});

document.getElementById('toggleNuevaContrasena').addEventListener('click', function() {
    var input = document.getElementById('nuevaContrasena');
    var icon = this.querySelector('i');
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('bi-eye');
        icon.classList.add('bi-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('bi-eye-slash');
        icon.classList.add('bi-eye');
    }
});

document.getElementById('toggleConfirmarContrasena').addEventListener('click', function() {
    var input = document.getElementById('confirmarContrasena');
    var icon = this.querySelector('i');
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('bi-eye');
        icon.classList.add('bi-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('bi-eye-slash');
        icon.classList.add('bi-eye');
    }
});
