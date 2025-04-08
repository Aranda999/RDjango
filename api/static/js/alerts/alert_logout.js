document.getElementById('logout-btn').addEventListener('click', function (event) {
    event.preventDefault(); // Prevents the default action of the link

    Swal.fire({
        title: 'Are you sure?',
        text: "Do you want to log out?",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Yes, log out',
        cancelButtonText: 'Cancel'
    }).then((result) => {
        if (result.isConfirmed) {
            // Redirects to the logout URL
            window.location.href = "/logout/"; 
        }
    });
});
