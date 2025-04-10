function mostrarDetallesSala() {
    const salaSeleccionada = document.getElementById("salaJuntas").value;
    const detallesSala = document.getElementById("detallesSala");
    const detallesContenido = document.getElementById("detallesSalaContenido");

    if (salaSeleccionada) {
        detallesSala.style.display = "block";  // Mostrar modal secundario
        if (salaSeleccionada == "1") {
            detallesContenido.innerHTML = "<strong>Nombre:</strong> Sala 1 (Laboratorio)<br><strong>Material:</strong> Proyector, Pantalla, Sillas, Pizarra";
        } else if (salaSeleccionada == "2") {
            detallesContenido.innerHTML = "<strong>Nombre:</strong> Sala 2 (Reuniones)<br><strong>Material:</strong> Televisión, Pizarra, Mesas, Sillas";
        } else if (salaSeleccionada == "3") {
            detallesContenido.innerHTML = "<strong>Nombre:</strong> Sala 3 (Conferencia)<br><strong>Material:</strong> Micrófono, Proyector, Sillas, Mesas";
        }
    }
}

// Evento para ocultar el modal secundario cuando se cierra el modal principal
var modal = document.getElementById('reservacionModal');
modal.addEventListener('hidden.bs.modal', function () {
    // Ocultar detalles de la sala cuando se cierra el modal de reservación
    document.getElementById('detallesSala').style.display = 'none';
});

