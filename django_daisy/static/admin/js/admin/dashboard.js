function close_modal() {
    $('.modal-backdrop').click()
}

(() => {
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const mobileSidebarMedia = window.matchMedia('(max-width: 63.999rem)');

    if (!menuToggle || !sidebar || !sidebarOverlay) {
        return;
    }

    function setSidebarOpen(isOpen) {
        if (mobileSidebarMedia.matches) {
            sidebar.classList.toggle('is-open', isOpen);
            sidebarOverlay.classList.toggle('is-open', isOpen);
            sidebarOverlay.setAttribute('aria-hidden', String(!isOpen));
            document.body.classList.toggle('sidebar-open', isOpen);
        } else {
            sidebar.classList.toggle('desktop-hidden', !isOpen);
        }

        menuToggle.setAttribute('aria-expanded', String(isOpen));
    }

    menuToggle.setAttribute('aria-expanded', String(!mobileSidebarMedia.matches));

    menuToggle.addEventListener('click', () => {
        const isOpen = mobileSidebarMedia.matches
            ? sidebar.classList.contains('is-open')
            : !sidebar.classList.contains('desktop-hidden');
        setSidebarOpen(!isOpen);
    });

    sidebarOverlay.addEventListener('click', () => setSidebarOpen(false));

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && mobileSidebarMedia.matches && sidebar.classList.contains('is-open')) {
            setSidebarOpen(false);
            menuToggle.focus();
        }
    });

    mobileSidebarMedia.addEventListener('change', () => {
        sidebar.classList.remove('is-open', 'desktop-hidden');
        sidebarOverlay.classList.remove('is-open');
        sidebarOverlay.setAttribute('aria-hidden', 'true');
        document.body.classList.remove('sidebar-open');
        menuToggle.setAttribute('aria-expanded', String(!mobileSidebarMedia.matches));
    });

    const resizeHandle = document.getElementById('sidebar-resize-handle');
    if (!resizeHandle) {
        return;
    }

    const widthStorageKey = 'django-daisy-sidebar-width';
    let savedWidth = parseFloat(document.documentElement.style.getPropertyValue('--sidebar-width'));
    let minWidth;
    let maxWidth;
    let drag;

    function setSidebarWidth(width) {
        const clampedWidth = Math.round(Math.max(minWidth, Math.min(maxWidth, width)));
        sidebar.style.setProperty('--sidebar-width', `${clampedWidth}px`);
        resizeHandle.setAttribute('aria-valuenow', clampedWidth);
    }

    function saveSidebarWidth() {
        savedWidth = Number(resizeHandle.getAttribute('aria-valuenow'));
        try {
            localStorage.setItem(widthStorageKey, savedWidth);
        } catch {
            // Keep the current width for this page.
        }
    }

    function syncSidebarWidth() {
        if (mobileSidebarMedia.matches) {
            if (drag && resizeHandle.hasPointerCapture(drag.pointerId)) {
                resizeHandle.releasePointerCapture(drag.pointerId);
            }
            return;
        }

        const styles = getComputedStyle(sidebar);
        minWidth = parseFloat(styles.minWidth);
        maxWidth = parseFloat(styles.maxWidth);
        resizeHandle.setAttribute('aria-valuemin', Math.round(minWidth));
        resizeHandle.setAttribute('aria-valuemax', Math.round(maxWidth));
        if (drag) {
            resizeHandle.setAttribute('aria-valuenow', Math.round(parseFloat(styles.width)));
        } else if (Number.isFinite(savedWidth) && savedWidth > 0) {
            setSidebarWidth(savedWidth);
        } else {
            resizeHandle.setAttribute('aria-valuenow', Math.round(parseFloat(styles.width)));
        }
    }

    syncSidebarWidth();
    window.addEventListener('resize', syncSidebarWidth);

    function inlineDirection() {
        return getComputedStyle(sidebar).direction === 'rtl' ? -1 : 1;
    }

    resizeHandle.addEventListener('pointerdown', (event) => {
        if (event.button !== 0 || drag) {
            return;
        }

        event.preventDefault();
        resizeHandle.focus({preventScroll: true});
        resizeHandle.setPointerCapture(event.pointerId);
        drag = {
            pointerId: event.pointerId,
            startX: event.clientX,
            startWidth: sidebar.getBoundingClientRect().width,
            direction: inlineDirection(),
        };
        sidebar.classList.add('is-resizing');
    });

    resizeHandle.addEventListener('pointermove', (event) => {
        if (drag?.pointerId === event.pointerId && !mobileSidebarMedia.matches) {
            setSidebarWidth(drag.startWidth + (event.clientX - drag.startX) * drag.direction);
        }
    });

    resizeHandle.addEventListener('lostpointercapture', (event) => {
        if (drag?.pointerId === event.pointerId) {
            drag = undefined;
            sidebar.classList.remove('is-resizing');
            saveSidebarWidth();
        }
    });

    resizeHandle.addEventListener('keydown', (event) => {
        let width = sidebar.getBoundingClientRect().width;
        switch (event.key) {
            case 'ArrowLeft':
                width -= 16 * inlineDirection();
                break;
            case 'ArrowRight':
                width += 16 * inlineDirection();
                break;
            case 'Home':
                width = minWidth;
                break;
            case 'End':
                width = maxWidth;
                break;
            default:
                return;
        }

        event.preventDefault();
        setSidebarWidth(width);
        saveSidebarWidth();
    });
})();


// jquery toggle whole attribute
$.fn.toggleAttr = function (attr, val) {
    var test = $(this).attr(attr);
    if (test) {
        // if attrib exists with ANY value, still remove it
        $(this).removeAttr(attr);
    } else {
        $(this).attr(attr, val);
    }
    return this;
};

// jquery toggle just the attribute value
$.fn.toggleAttrVal = function (attr, val1, val2) {
    var test = $(this).attr(attr);
    if (test === val1) {
        $(this).attr(attr, val2);
        return this;
    }
    if (test === val2) {
        $(this).attr(attr, val1);
        return this;
    }
    // default to val1 if neither
    $(this).attr(attr, val1);
    return this;
};
