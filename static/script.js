// alert("It's Working")
// if (typeof flashMessages !== 'undefined' && flashMessages.length > 0) {
//     flashMessages.forEach(function(message) {
//         alert(message); // or use your own custom alert logic
//     });
// }

// static/script.js

document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('themeToggle');
    const body = document.body;
    const navbar = document.querySelector('.navbar');
    const toastNotificationsContainer = document.getElementById('toastNotifications') || document.getElementById('toastNotificationsDash'); // For different pages
    const currentYearSpan = document.getElementById('currentYear') || document.getElementById('currentYearDash');

    // --- Theme Toggle ---
    const currentTheme = localStorage.getItem('theme') ? localStorage.getItem('theme') : 'dark'; // Default to dark
    body.classList.add(currentTheme + '-theme');
    updateThemeIcon(currentTheme);

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            let newTheme = 'dark';
            if (body.classList.contains('dark-theme')) {
                body.classList.remove('dark-theme');
                body.classList.add('light-theme');
                newTheme = 'light';
            } else {
                body.classList.remove('light-theme');
                body.classList.add('dark-theme');
                newTheme = 'dark';
            }
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }

    function updateThemeIcon(theme) {
        const icon = themeToggle ? themeToggle.querySelector('i') : null;
        if (icon) {
            if (theme === 'light') {
                icon.classList.remove('ri-sun-line');
                icon.classList.add('ri-moon-clear-line');
            } else {
                icon.classList.remove('ri-moon-clear-line');
                icon.classList.add('ri-sun-line');
            }
        }
    }

    // --- Navbar Scroll Behavior (only for home page with transparent hero) ---
    if (navbar && !navbar.classList.contains('scrolled')) { // Check if it's not the dashboard navbar
        const heroSection = document.querySelector('.hero-section');
        if (heroSection) { // Only apply scroll for pages with a hero section
            window.addEventListener('scroll', () => {
                if (window.scrollY > 50) {
                    navbar.classList.add('scrolled');
                } else {
                    navbar.classList.remove('scrolled');
                }
            });
        } else { // If no hero section (e.g. simple pages), make navbar solid from start
             navbar.classList.add('scrolled');
        }
    }


    // --- Profile Dropdown Toggle (if it exists) ---
    const navUsername = document.querySelector('.nav-username');
    if (navUsername) {
        const dropdown = navUsername.nextElementSibling;
        if (dropdown && dropdown.classList.contains('profile-dropdown')) {
            navUsername.addEventListener('click', (event) => {
                event.stopPropagation(); // Prevent window click from closing it immediately
                dropdown.style.opacity = dropdown.style.opacity === '1' ? '0' : '1';
                dropdown.style.visibility = dropdown.style.visibility === 'visible' ? 'hidden' : 'visible';
                dropdown.style.transform = dropdown.style.transform === 'translateY(0px)' ? 'translateY(10px)' : 'translateY(0px)';
            });
            // Close dropdown if clicked outside
            window.addEventListener('click', (event) => {
                if (!navUsername.contains(event.target) && !dropdown.contains(event.target)) {
                    dropdown.style.opacity = '0';
                    dropdown.style.visibility = 'hidden';
                    dropdown.style.transform = 'translateY(10px)';
                }
            });
        }
    }


    // --- Toast Notifications from Flask flash messages ---
    if (typeof flashMessages !== 'undefined' && flashMessages.length > 0 && toastNotificationsContainer) {
        flashMessages.forEach(flash => {
            showToast(flash.message, flash.category);
        });
    }

    function showToast(message, type = 'info') { // type can be 'success', 'danger', 'warning', 'info'
        if (!toastNotificationsContainer) return;

        const toast = document.createElement('div');
        toast.classList.add('toast', type);

        let iconClass = 'ri-information-line';
        if (type === 'success') iconClass = 'ri-checkbox-circle-line';
        else if (type === 'danger') iconClass = 'ri-error-warning-line';
        else if (type === 'warning') iconClass = 'ri-alert-line';

        toast.innerHTML = `
            <i class="${iconClass}"></i>
            <span>${message}</span>
        `;
        toastNotificationsContainer.appendChild(toast);

        // Auto dismiss
        setTimeout(() => {
            toast.style.animation = 'toastOutRight 0.5s forwards'; // Ensure animation name matches CSS
            if (document.body.offsetWidth <= 576) { // Check for small screens to use toastOutDown
                 toast.style.animation = 'toastOutDown 0.5s forwards';
            }
            toast.addEventListener('animationend', () => {
                toast.remove();
            });
        }, 5000); // Corresponds to animation delay in CSS
    }
    // Example: showToast("Profile updated successfully!", "success"); // For client-side toasts

    // --- Scroll-triggered Animations ---
    const animatedElements = document.querySelectorAll('.slide-up-fade-in');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                // Optional: unobserve after animation to save resources
                // observer.unobserve(entry.target);
            } else {
                // Optional: re-hide if scrolling up, or keep visible
                // entry.target.style.opacity = '0';
                // entry.target.style.transform = 'translateY(20px)';
            }
        });
    }, { threshold: 0.1 }); // Trigger when 10% of the element is visible

    animatedElements.forEach(el => {
        // Initialize hidden for JS control
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        observer.observe(el);
    });


    // --- Set Current Year in Footer ---
    if (currentYearSpan) {
        currentYearSpan.textContent = new Date().getFullYear();
    }

});