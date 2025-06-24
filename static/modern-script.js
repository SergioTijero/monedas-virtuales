// Modern Script for Material Design 3 Interface
document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS (Animate On Scroll)
    AOS.init({
        duration: 800,
        easing: 'ease-out-cubic',
        once: true,
        offset: 50
    });

    // Hide loader and show app
    setTimeout(() => {
        const loader = document.getElementById('loader');
        const app = document.getElementById('app');
        
        if (loader && app) {
            loader.style.opacity = '0';
            setTimeout(() => {
                loader.style.display = 'none';
                app.style.opacity = '1';
            }, 500);
        }
    }, 1000);

    // Navigation drawer functionality
    const menuToggle = document.getElementById('menu-toggle');
    const navDrawer = document.getElementById('nav-drawer');
    const overlay = document.getElementById('overlay');

    if (menuToggle && navDrawer && overlay) {
        menuToggle.addEventListener('click', toggleDrawer);
        overlay.addEventListener('click', closeDrawer);
        
        // Close drawer on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && navDrawer.classList.contains('open')) {
                closeDrawer();
            }
        });
    }

    function toggleDrawer() {
        navDrawer.classList.toggle('open');
        overlay.classList.toggle('active');
        document.body.style.overflow = navDrawer.classList.contains('open') ? 'hidden' : '';
    }

    function closeDrawer() {
        navDrawer.classList.remove('open');
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    // Auto-hide flash messages
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.animation = 'slideOutRight 0.3s ease-in forwards';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);
    });

    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.btn, .icon-button, .nav-item');
    buttons.forEach(button => {
        button.addEventListener('click', createRipple);
    });

    function createRipple(e) {
        const button = e.currentTarget;
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        const ripple = document.createElement('div');
        ripple.className = 'ripple';
        ripple.style.cssText = `
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: scale(0);
            animation: ripple-animation 0.6s linear;
            left: ${x}px;
            top: ${y}px;
            width: ${size}px;
            height: ${size}px;
            pointer-events: none;
        `;
        
        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        button.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    // Add CSS for ripple animation if not exists
    if (!document.querySelector('#ripple-styles')) {
        const style = document.createElement('style');
        style.id = 'ripple-styles';
        style.textContent = `
            @keyframes ripple-animation {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
            
            @keyframes slideOutRight {
                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }

    // Form validation and enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            // Add floating label effect
            input.addEventListener('focus', () => {
                input.parentElement.classList.add('focused');
            });
            
            input.addEventListener('blur', () => {
                if (!input.value) {
                    input.parentElement.classList.remove('focused');
                }
            });
            
            // Check if input has value on load
            if (input.value) {
                input.parentElement.classList.add('focused');
            }
        });
    });

    // Add smooth scrolling to navigation links
    const navLinks = document.querySelectorAll('.nav-item');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            // Add active state to clicked nav item
            navLinks.forEach(nl => nl.classList.remove('active'));
            link.classList.add('active');
            
            // Close drawer on mobile after navigation
            if (window.innerWidth <= 768) {
                setTimeout(closeDrawer, 300);
            }
        });
    });

    // Set active nav item based on current page
    const currentPath = window.location.pathname;
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Add loading states to forms
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="material-icons">hourglass_empty</span> Procesando...';
                submitBtn.classList.add('loading');
            }
        });
    });

    // Add intersection observer for animations
    const observeElements = document.querySelectorAll('.card, .stat-card');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 0.6s ease-out forwards';
            }
        });
    }, { threshold: 0.1 });

    observeElements.forEach(el => observer.observe(el));

    // Add CSS for fade in animation
    const fadeStyle = document.createElement('style');
    fadeStyle.textContent = `
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    `;
    document.head.appendChild(fadeStyle);

    // Dark mode toggle (future enhancement)
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
    
    function updateTheme(e) {
        if (e.matches) {
            document.documentElement.setAttribute('data-theme', 'dark');
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
        }
    }
    
    prefersDark.addEventListener('change', updateTheme);
    updateTheme(prefersDark);

    // Add performance optimizations
    // Debounce scroll events
    let scrollTimeout;
    window.addEventListener('scroll', () => {
        if (scrollTimeout) {
            clearTimeout(scrollTimeout);
        }
        scrollTimeout = setTimeout(() => {
            // Handle scroll events here if needed
        }, 10);
    });

    // Preload navigation pages
    const preloadLinks = document.querySelectorAll('.nav-item[href]');
    preloadLinks.forEach(link => {
        const linkUrl = link.getAttribute('href');
        if (linkUrl && linkUrl !== currentPath) {
            const linkElement = document.createElement('link');
            linkElement.rel = 'prefetch';
            linkElement.href = linkUrl;
            document.head.appendChild(linkElement);
        }
    });

    console.log('✨ Modern UI initialized successfully!');
});

// Utility functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `flash-message flash-${type} animate__animated animate__fadeInDown`;
    notification.innerHTML = `
        <span class="material-icons">
            ${type === 'success' ? 'check_circle' : 
              type === 'error' ? 'error' : 
              type === 'warning' ? 'warning' : 'info'}
        </span>
        <span>${message}</span>
        <button class="close-flash" onclick="this.parentElement.remove()">
            <span class="material-icons">close</span>
        </button>
    `;
    
    let container = document.querySelector('.flash-messages');
    if (!container) {
        container = document.createElement('div');
        container.className = 'flash-messages';
        document.body.appendChild(container);
    }
    
    container.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-in forwards';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Export for global use
window.showNotification = showNotification;
