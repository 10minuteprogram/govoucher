<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>


document.addEventListener('DOMContentLoaded', function () {
    var deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            // Show SweetAlert confirmation dialog
            Swal.fire({
                title: 'Are you sure?',
                text: "You won't be able to revert this!",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Yes, delete it!',
                cancelButtonText: 'Cancel'
            }).then((result) => {
                if (result.isConfirmed) {
                    // If user confirms, submit the form
                    button.closest('.delete-form').submit();
                }
            });
        });
    });
});

