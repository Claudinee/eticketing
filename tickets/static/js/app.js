// Add this navigation functionality at the top of your existing app.js
document.addEventListener('DOMContentLoaded', function() {
    // Navigation handling
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = {
        home: document.getElementById('ticketForm').closest('section'),
        events: document.getElementById('events-section'),
        contact: document.getElementById('contact-section')
    };

    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Update active state
            navLinks.forEach(navLink => navLink.classList.remove('active'));
            this.classList.add('active');
            
            // Show/hide sections
            const sectionToShow = this.dataset.section;
            Object.values(sections).forEach(section => {
                section.classList.add('d-none');
            });
            sections[sectionToShow].classList.remove('d-none');
        });
    });

    // Contact form handling
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Thank you for your message! We will contact you soon.');
            this.reset();
        });
    }
});

// Your existing ticket form JS remains below...
const AUTH_TOKEN = "c5458fe371215017510c55b1b88e0af28929d340"; // Get this from python manage.py shell
document.getElementById('ticketForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        organizer: document.getElementById('organizer').value,
        personal_id: document.getElementById('personal_id').value,
        amount: document.getElementById('amount').value
    };

    try {
        const response = await axios.post('/api/transactions/', formData, {
            headers: {
                'Authorization': 'c5458fe371215017510c55b1b88e0af28929d340', // Replace with your token
                'Content-Type': 'application/json'
            }
        });
        
        alert(`Ticket purchased successfully! Ticket Number: ${response.data.ticket.ticket_number}`);
        document.getElementById('ticketForm').reset();
    } catch (error) {
        alert(`Error: ${error.response?.data?.error || 'Failed to purchase ticket'}`);
        console.error(error);
    }
});