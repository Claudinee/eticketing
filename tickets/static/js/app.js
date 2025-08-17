document.addEventListener('DOMContentLoaded', function() {
    const ticketCategory = document.getElementById('ticket_category');
    const amountInput = document.getElementById('amount');

    // Prices per category
    const categoryPrices = {
        VVIP: 15000,
        VIP: 10000,
        REGULAR: 5000,
        ADULT: 5000,
        CHILD: 2500
    };

    // Update price when category is selected
    ticketCategory.addEventListener('change', function() {
        const selectedCategory = this.value;
        amountInput.value = categoryPrices[selectedCategory] || '';
    });

    // Ticket form submission
    const ticketForm = document.getElementById('ticketForm');
    ticketForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Validate fields
        const organizerValue = document.getElementById('organizer').value;
        const personalIdValue = document.getElementById('personal_id').value;
        if (!ticketCategory.value || !amountInput.value || !organizerValue || !personalIdValue) {
            alert('Please fill all required fields.');
            return;
        }

        const formData = {
            organizer: organizerValue,
            personal_id: personalIdValue,
            category: ticketCategory.value,
            amount: amountInput.value
        };

        try {
            const response = await axios.post('/api/transactions/', formData, {
                headers: { 'Content-Type': 'application/json' }
            });

            // Get ticket number and category from API response
            const ticketNumber = response.data.ticket_number || 'N/A';
            const category = response.data.category || 'N/A';

            alert(`🎉 Ticket purchased successfully!\nTicket Number: ${ticketNumber}\nCategory: ${category}\nPrice: RWF ${amountInput.value}`);

            // Reset form and set default price
            ticketForm.reset();
            amountInput.value = '';
        } catch (error) {
            console.error(error);
            const errorMessage = error.response?.data?.error || 'Failed to purchase ticket. Please try again!';
            alert(`❌ Error: ${errorMessage}`);
        }
    });

    // Navigation section toggle
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = {
        home: document.getElementById('ticket-section'),
        events: document.getElementById('events-section'),
        contact: document.getElementById('contact-section')
    };

    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            navLinks.forEach(nav => nav.classList.remove('active'));
            this.classList.add('active');

            const sectionToShow = this.dataset.section;
            Object.values(sections).forEach(section => section.classList.add('d-none'));
            sections[sectionToShow].classList.remove('d-none');

            // Scroll to top for better UX
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    });

    // Contact form handling
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Thank you for your message! We will contact you soon.');
            contactForm.reset();
        });
    }
});
