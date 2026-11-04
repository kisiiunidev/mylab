// JavaScript for Coffee Corner website

// Mobile menu toggle
const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
const navLinks = document.querySelector('.nav-links');

if (mobileMenuToggle) {
    mobileMenuToggle.addEventListener('click', () => {
        navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
    });
}

// Flash message close buttons
const closeButtons = document.querySelectorAll('.flash-close');
closeButtons.forEach(button => {
    button.addEventListener('click', (e) => {
        e.target.closest('.flash-message').remove();
    });
});

// Thumbnail gallery functionality
const thumbnails = document.querySelectorAll('.thumbnail');
const mainImage = document.querySelector('.main-image img');

if (thumbnails.length > 0 && mainImage) {
    thumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', () => {
            const thumbnailSrc = thumbnail.src;
            mainImage.src = thumbnailSrc;

            // Remove active class from all thumbnails
            thumbnails.forEach(t => t.classList.remove('active'));
            // Add active class to clicked thumbnail
            thumbnail.classList.add('active');
        });
    });
}

// Form validation helpers
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('error');
        } else {
            field.classList.remove('error');
        }
    });

    return isValid;
}

// Cart quantity forms - prevent default and handle AJAX (if available)
const quantityForms = document.querySelectorAll('.quantity-form');
quantityForms.forEach(form => {
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        // In a real application, you would use AJAX to update the cart
        // For now, we'll just submit the form
        form.submit();
    });
});

// Add to cart button loading state
const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
addToCartButtons.forEach(button => {
    button.addEventListener('click', (e) => {
        if (button.hasAttribute('disabled')) {
            e.preventDefault();
            return;
        }

        // Add loading state
        button.classList.add('loading');
        button.disabled = true;

        // Submit the form after a short delay (simulating async request)
        const form = button.closest('form');
        if (form) {
            setTimeout(() => {
                button.classList.remove('loading');
                button.disabled = false;
                form.submit();
            }, 1000);
        }
    });
});

// Admin tab switching
const tabButtons = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

tabButtons.forEach(button => {
    button.addEventListener('click', () => {
        const targetTab = button.getAttribute('onclick').match(/showTab\('([^']+)'\)/)[1];

        // Remove active class from all buttons and contents
        tabButtons.forEach(btn => btn.classList.remove('active'));
        tabContents.forEach(content => content.classList.remove('active'));

        // Add active class to clicked button and target tab
        button.classList.add('active');
        const targetContent = document.getElementById(targetTab);
        if (targetContent) {
            targetContent.classList.add('active');
        }
    });
});

// Smooth scroll for anchor links
 document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Cookie consent banner (if present)
function showCookieConsent() {
    if (!localStorage.getItem('cookieConsent')) {
        const banner = document.createElement('div');
        banner.style.cssText = 'position: fixed; bottom: 0; left: 0; right: 0; background: var(--primary-color); color: white; padding: 1rem; text-align: center; z-index: 10000;';
        banner.innerHTML = `
            <p>We use cookies to improve your experience. By continuing to use this site, you agree to our <a href="#" style="color: var(--accent-color);">Privacy Policy</a>.</p>
            <button onclick="this.parentElement.remove(); localStorage.setItem('cookieConsent', 'true');" style="background: white; color: var(--primary-color); border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; font-weight: 600; margin-left: 1rem;">Accept</button>
        `;
        document.body.appendChild(banner);
    }
}

// Initialize cookie consent on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', showCookieConsent);
} else {
    showCookieConsent();
}

// Search functionality for coffee items
const coffeeSearch = document.querySelector('.coffee-search');
if (coffeeSearch) {
    coffeeSearch.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const coffeeCards = document.querySelectorAll('.coffee-card');

        coffeeCards.forEach(card => {
            const coffeeName = card.querySelector('h3').textContent.toLowerCase();
            const coffeeDescription = card.querySelector('.coffee-description').textContent.toLowerCase();

            if (coffeeName.includes(searchTerm) || coffeeDescription.includes(searchTerm)) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    });
}

// Cart total updater (if using AJAX)
function updateCartTotal() {
    // This function would be called via AJAX in a real application
    // For now, we'll just recalculate if needed
    console.log('Cart total updated');
}

// Error handling for forms
const forms = document.querySelectorAll('form');
forms.forEach(form => {
    form.addEventListener('submit', function(e) {
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.textContent = 'Processing...';
        }
    });
});

// Auto-hide flash messages after 5 seconds
const flashMessages = document.querySelectorAll('.flash-message');
flashMessages.forEach(message => {
    setTimeout(() => {
        if (message.parentElement) {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        }
    }, 5000);
});

console.log('Coffee Corner JavaScript loaded successfully!');