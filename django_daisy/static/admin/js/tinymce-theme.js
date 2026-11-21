(() => {
    const tinyMCE = window.tinymce;
    if (!tinyMCE) return;

    const root = document.documentElement;

    function applyTheme(editor) {
        const body = editor.getBody();
        if (!body) return;

        // The editing iframe has its own document and cannot inherit Daisy's colors.
        const theme = getComputedStyle(root);
        const frameRoot = body.ownerDocument.documentElement;
        frameRoot.style.colorScheme = theme.colorScheme;
        frameRoot.style.backgroundColor = body.style.backgroundColor =
            theme.getPropertyValue('--color-base-100');
        body.style.color = theme.getPropertyValue('--color-base-content');
    }

    tinyMCE.on('AddEditor', ({ editor }) => editor.on('init', () => applyTheme(editor)));
    const updateEditors = () => tinyMCE.get().forEach(applyTheme);
    new MutationObserver(updateEditors).observe(root, {
        attributes: true,
        attributeFilter: ['data-theme'],
    });
    updateEditors();
})();
