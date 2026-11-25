(() => {
    const logo = document.querySelector('[data-logo-dark]');
    if (!logo) return;

    const lightLogo = logo.getAttribute('src');
    const darkLogo = logo.dataset.logoDark;
    const root = document.documentElement;
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)');
    const darkThemes = new Set([
        'abyss', 'aqua', 'black', 'business', 'coffee', 'dark', 'dim',
        'dracula', 'forest', 'halloween', 'luxury', 'night', 'sunset', 'synthwave',
    ]);

    function isDarkTheme() {
        const theme = root.dataset.theme;
        if (darkThemes.has(theme)) return true;
        if (theme === 'light') return false;

        const schemes = getComputedStyle(logo).colorScheme.split(' ');
        return schemes.includes('dark') &&
            (!schemes.includes('light') || systemTheme.matches);
    }

    function updateLogo() {
        const source = isDarkTheme() ? darkLogo : lightLogo;
        if (logo.getAttribute('src') !== source) logo.setAttribute('src', source);
    }

    new MutationObserver(updateLogo).observe(root, {
        attributes: true,
        attributeFilter: ['data-theme'],
    });
    systemTheme.addEventListener('change', updateLogo);
    updateLogo();
})();
