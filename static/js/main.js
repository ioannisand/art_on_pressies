document.addEventListener('DOMContentLoaded', function () {
    const burgerBtn   = document.getElementById('burger-btn');
    const drawer      = document.getElementById('nav-drawer');
    const backdrop    = document.getElementById('nav-backdrop');
    const menuIcon    = document.getElementById('menu-icon');
    const closeIcon   = document.getElementById('close-icon');

    function openDrawer() {
        drawer.classList.add('open');
        backdrop.classList.add('open');
        menuIcon.classList.add('hidden');
        closeIcon.classList.remove('hidden');
    }

    function closeDrawer() {
        drawer.classList.remove('open');
        backdrop.classList.remove('open');
        menuIcon.classList.remove('hidden');
        closeIcon.classList.add('hidden');
    }

    if (burgerBtn) {
        burgerBtn.addEventListener('click', function () {
            drawer.classList.contains('open') ? closeDrawer() : openDrawer();
        });
    }

    // Close on backdrop click
    if (backdrop) {
        backdrop.addEventListener('click', closeDrawer);
    }

    // Close on Escape
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeDrawer();
    });

    // Mobile search toggle
    const searchBtn   = document.getElementById('search-toggle-btn');
    const mobileSearch = document.getElementById('mobile-search');

    if (searchBtn && mobileSearch) {
        searchBtn.addEventListener('click', function () {
            mobileSearch.classList.toggle('hidden');
            if (!mobileSearch.classList.contains('hidden')) {
                mobileSearch.querySelector('input').focus();
            }
        });
    }
});
