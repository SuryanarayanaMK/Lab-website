// Maddu Lab - Main JavaScript

// ================= MOBILE MENU =================
window.toggleMobileMenu = function () {
    const mobileNav = document.getElementById('mobileNav');
    if (!mobileNav) return;

    mobileNav.style.display =
        mobileNav.style.display === 'block' ? 'none' : 'block';
};

// ================= SIDEBAR =================
window.toggleSidebar = function () {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');

    if (!sidebar || !overlay) return;

    sidebar.classList.toggle('active');
    overlay.classList.toggle('active');

    document.body.style.overflow =
        sidebar.classList.contains('active') ? 'hidden' : '';
};

// ================= LOAD HEADER =================
function loadHeader() {
    const headerContainer = document.getElementById('header-container');

    if (!headerContainer) return;

    fetch('header.html?t=' + Date.now())
        .then(res => res.text())
        .then(data => {
            headerContainer.innerHTML = data;

            // 🔥 IMPORTANT: Initialize header AFTER loading
            initHeader();
        })
        .catch(err => console.error('Error loading header:', err));
}

// ================= LOAD FOOTER =================
function loadFooter() {
    const footerContainer = document.getElementById('footer-container');

    if (!footerContainer) return;

    fetch('footer.html?t=' + Date.now())
        .then(res => res.text())
        .then(data => {
            footerContainer.innerHTML = data;
        })
        .catch(err => console.error('Error loading footer:', err));
}

// ================= HEADER INIT =================
function initHeader() {
    // Highlight active page
    const currentPage =
        window.location.pathname.split('/').pop() || 'index.html';

    const links = document.querySelectorAll('.nav-link, .mobile-nav-link');

    links.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPage) {
            link.classList.add('active');
        }
    });
    
    // Force highlighting for current page
    setTimeout(() => {
        const allLinks = document.querySelectorAll('.nav-link, .mobile-nav-link');
        allLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href === currentPage) {
                link.classList.add('active');
                link.style.color = 'black !important';
            } else {
                link.classList.remove('active');
                link.style.color = '';
            }
        });
    }, 100);

    // Close menu on outside click (SAFE)
    document.addEventListener('click', function (e) {
        const mobileNav = document.getElementById('mobileNav');
        const mobileBtn = document.querySelector('.mobile-menu-btn');

        if (!mobileNav || !mobileBtn) return;

        if (
            !mobileNav.contains(e.target) &&
            !mobileBtn.contains(e.target)
        ) {
            mobileNav.style.display = 'none';
        }
    });
}

// ================= EMAIL COPY =================
window.copyEmailToClipboard = function (btn) {
    const email = btn.getAttribute('data-email');
    if (!email || !navigator.clipboard) return;

    navigator.clipboard.writeText(email).then(function () {
        btn.classList.add('copied');
        clearTimeout(btn._copyTimeout);
        btn._copyTimeout = setTimeout(function () {
            btn.classList.remove('copied');
        }, 1600);
    });
};

// ================= GLOBAL EVENTS =================
document.addEventListener('DOMContentLoaded', function () {
    // Load reusable components
    loadHeader();
    loadFooter();

    // Smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();

            const target = document.querySelector(
                this.getAttribute('href')
            );

            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }

            // Close sidebar if open
            const sidebar = document.getElementById('sidebar');
            if (sidebar && sidebar.classList.contains('active')) {
                toggleSidebar();
            }
        });
    });

    // Escape key closes sidebar
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            const sidebar = document.getElementById('sidebar');
            if (sidebar && sidebar.classList.contains('active')) {
                toggleSidebar();
            }
        }
    });
});