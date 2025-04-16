// Admin panel functionality

document.addEventListener('DOMContentLoaded', function () {
    // Handle room form modal
    const addRoomModal = document.getElementById('addRoomModal');
    if (addRoomModal) {
        addRoomModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const isEdit = button.getAttribute('data-action') === 'edit';
            const modal = this;

            const modalTitle = modal.querySelector('.modal-title');
            const form = modal.querySelector('form');
            const submitBtn = modal.querySelector('.modal-footer button[type="submit"]');

            if (isEdit) {
                const roomId = button.getAttribute('data-room-id');
                const roomName = button.getAttribute('data-room-name');
                const roomDesc = button.getAttribute('data-room-description');
                const roomImg = button.getAttribute('data-room-image');
                const roomPrice = button.getAttribute('data-room-price');
                const roomCapacity = button.getAttribute('data-room-capacity');
                const roomAmenities = button.getAttribute('data-room-amenities');
                const roomAvailable = button.getAttribute('data-room-available') === 'true';

                modalTitle.textContent = 'Edit Room';
                submitBtn.textContent = 'Update Room';

                form.action = `/admin/rooms/${roomId}/edit`;

                form.querySelector('#name').value = roomName;
                form.querySelector('#description').value = roomDesc;
                form.querySelector('#image_url').value = roomImg;
                form.querySelector('#price').value = roomPrice;
                form.querySelector('#capacity').value = roomCapacity;
                form.querySelector('#amenities').value = roomAmenities;
                form.querySelector('#is_available').checked = roomAvailable;

                // Show delete button for edit mode
                const deleteBtn = modal.querySelector('.btn-danger');
                if (deleteBtn) {
                    deleteBtn.classList.remove('d-none');
                    deleteBtn.setAttribute('data-room-id', roomId);
                }
            } else {
                // Reset form for add mode
                modalTitle.textContent = 'Add New Room';
                submitBtn.textContent = 'Add Room';

                form.action = '/admin/rooms/add';
                form.reset();

                // Hide delete button for add mode
                const deleteBtn = modal.querySelector('.btn-danger');
                if (deleteBtn) {
                    deleteBtn.classList.add('d-none');
                }
            }
        });
    }

    // Handle room deletion
    const deleteRoomModal = document.getElementById('deleteRoomModal');
    if (deleteRoomModal) {
        deleteRoomModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const roomId = button.getAttribute('data-room-id');
            const form = this.querySelector('form');

            form.action = `/admin/rooms/${roomId}/delete`;
        });
    }

    // Handle booking status updates
    const bookingStatusForm = document.querySelectorAll('.booking-status-form');
    bookingStatusForm.forEach(form => {
        const statusSelect = form.querySelector('select');
        statusSelect.addEventListener('change', function () {
            form.submit();
        });
    });

    // Search functionality for bookings
    const bookingSearchInput = document.getElementById('booking-search');
    if (bookingSearchInput) {
        bookingSearchInput.addEventListener('input', function () {
            const searchTerm = this.value.toLowerCase();
            const bookingRows = document.querySelectorAll('.booking-row');

            bookingRows.forEach(row => {
                const guestName = row.querySelector('.guest-name').textContent.toLowerCase();
                const guestEmail = row.querySelector('.guest-email').textContent.toLowerCase();
                const userName = row.querySelector('.user-name') ? row.querySelector('.user-name').textContent.toLowerCase() : '';
                const roomName = row.querySelector('.room-name').textContent.toLowerCase();

                const isMatch = guestName.includes(searchTerm) ||
                    guestEmail.includes(searchTerm) ||
                    userName.includes(searchTerm) ||
                    roomName.includes(searchTerm);

                row.style.display = isMatch ? '' : 'none';
            });
        });
    }

    // Date filtering for bookings
    const dateFilterForm = document.getElementById('date-filter-form');
    if (dateFilterForm) {
        dateFilterForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const startDate = new Date(document.getElementById('filter-start-date').value);
            const endDate = new Date(document.getElementById('filter-end-date').value);

            if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
                alert('Please select valid dates');
                return;
            }

            if (startDate > endDate) {
                alert('Start date must be before end date');
                return;
            }

            const bookingRows = document.querySelectorAll('.booking-row');

            bookingRows.forEach(row => {
                const checkInStr = row.querySelector('.check-in-date').textContent;
                const checkIn = new Date(checkInStr);

                const isInRange = checkIn >= startDate && checkIn <= endDate;
                row.style.display = isInRange ? '' : 'none';
            });
        });

        // Reset filter
        document.getElementById('reset-filter').addEventListener('click', function () {
            dateFilterForm.reset();
            document.querySelectorAll('.booking-row').forEach(row => {
                row.style.display = '';
            });
        });
    }

    // Dashboard charts
    const bookingsChart = document.getElementById('bookingsChart');
    if (bookingsChart) {
        // Get booking data from data attributes
        const chartData = JSON.parse(bookingsChart.dataset.bookings);

        new Chart(bookingsChart, {
            type: 'bar',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Booking Status Distribution',
                    data: chartData.data,
                    backgroundColor: [
                        'rgba(255, 193, 7, 0.8)',  // Warning - Pending
                        'rgba(40, 167, 69, 0.8)',  // Success - Confirmed
                        'rgba(220, 53, 69, 0.8)'   // Danger - Cancelled
                    ],
                    borderColor: [
                        'rgb(255, 193, 7)',
                        'rgb(40, 167, 69)',
                        'rgb(220, 53, 69)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Booking Status Distribution'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }
});
