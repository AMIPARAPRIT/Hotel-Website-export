// Booking form validation and functionality

document.addEventListener('DOMContentLoaded', function () {
    const bookingForm = document.getElementById('booking-form');

    if (bookingForm) {
        const checkInDate = document.getElementById('check_in_date');
        const checkOutDate = document.getElementById('check_out_date');
        const numGuests = document.getElementById('num_guests');
        const roomId = bookingForm.dataset.roomId;
        const roomCapacity = parseInt(bookingForm.dataset.roomCapacity);
        const availabilityMessage = document.getElementById('availability-message');

        // Set minimum dates for check-in and check-out
        const today = new Date();
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);

        const formatDate = (date) => {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            return `${year}-${month}-${day}`;
        };

        checkInDate.min = formatDate(today);
        checkOutDate.min = formatDate(tomorrow);

        // Update checkout min date when check-in changes
        checkInDate.addEventListener('change', function () {
            const selectedDate = new Date(this.value);
            const nextDay = new Date(selectedDate);
            nextDay.setDate(selectedDate.getDate() + 1);

            checkOutDate.min = formatDate(nextDay);

            // If checkout date is now invalid, update it
            if (new Date(checkOutDate.value) <= selectedDate) {
                checkOutDate.value = formatDate(nextDay);
            }

            checkAvailability();
        });

        // Check availability when check-out date changes
        checkOutDate.addEventListener('change', checkAvailability);

        // Limit number of guests based on room capacity
        numGuests.max = roomCapacity;
        numGuests.addEventListener('change', function () {
            if (parseInt(this.value) > roomCapacity) {
                this.value = roomCapacity;
                showMessage(`This room has a maximum capacity of ${roomCapacity} guests.`, 'warning');
            }
        });

        // Form validation before submit
        bookingForm.addEventListener('submit', function (e) {
            if (!validateForm()) {
                e.preventDefault();
            }
        });

        // Check room availability function
        function checkAvailability() {
            const checkin = checkInDate.value;
            const checkout = checkOutDate.value;

            if (!checkin || !checkout || new Date(checkin) >= new Date(checkout)) {
                availabilityMessage.textContent = '';
                availabilityMessage.className = '';
                return;
            }

            fetch('/api/check_availability', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    room_id: roomId,
                    check_in: checkin,
                    check_out: checkout
                })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.available) {
                        availabilityMessage.textContent = 'Room is available for the selected dates!';
                        availabilityMessage.className = 'alert alert-success mt-2';
                    } else {
                        availabilityMessage.textContent = 'Sorry, the room is not available for the selected dates.';
                        availabilityMessage.className = 'alert alert-danger mt-2';
                    }
                })
                .catch(error => {
                    console.error('Error checking availability:', error);
                    availabilityMessage.textContent = 'Error checking availability. Please try again.';
                    availabilityMessage.className = 'alert alert-warning mt-2';
                });
        }

        // Form validation function
        function validateForm() {
            const guestName = document.getElementById('guest_name').value;
            const guestEmail = document.getElementById('guest_email').value;
            const guestPhone = document.getElementById('guest_phone').value;
            const checkin = checkInDate.value;
            const checkout = checkOutDate.value;
            const guests = numGuests.value;

            // Clear previous error messages
            document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));

            let isValid = true;

            // Check required fields
            if (!guestName) {
                document.getElementById('guest_name').classList.add('is-invalid');
                isValid = false;
            }

            // Validate email
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!guestEmail || !emailRegex.test(guestEmail)) {
                document.getElementById('guest_email').classList.add('is-invalid');
                isValid = false;
            }

            // Validate phone
            const phoneRegex = /^\+?[0-9\s\-()]{8,20}$/;
            if (!guestPhone || !phoneRegex.test(guestPhone)) {
                document.getElementById('guest_phone').classList.add('is-invalid');
                isValid = false;
            }

            // Validate dates
            if (!checkin || !checkout) {
                if (!checkin) checkInDate.classList.add('is-invalid');
                if (!checkout) checkOutDate.classList.add('is-invalid');
                isValid = false;
            } else if (new Date(checkin) >= new Date(checkout)) {
                checkInDate.classList.add('is-invalid');
                checkOutDate.classList.add('is-invalid');
                showMessage('Check-out date must be after check-in date', 'danger');
                isValid = false;
            }

            // Validate number of guests
            if (!guests || guests < 1 || guests > roomCapacity) {
                numGuests.classList.add('is-invalid');
                isValid = false;
            }

            return isValid;
        }

        // Helper function to show messages
        function showMessage(message, type) {
            const alertBox = document.createElement('div');
            alertBox.className = `alert alert-${type} alert-dismissible fade show mt-3`;
            alertBox.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;

            bookingForm.insertAdjacentElement('beforebegin', alertBox);

            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                alertBox.classList.remove('show');
                setTimeout(() => alertBox.remove(), 150);
            }, 5000);
        }
    }
});
