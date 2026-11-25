document.querySelectorAll('.change-form-tabs').forEach((group, groupIndex) => {
    const tabs = Array.from(group.querySelectorAll(':scope > .tab'));
    const panels = Array.from(group.querySelectorAll(':scope > .tab-content'));
    if (!tabs.length || tabs.length !== panels.length) return;

    const available = tabs.map((tab, index) => index).filter(index => {
        const panel = panels[index];
        if (panel.hasAttribute('data-default-form-panel') &&
            !panel.children.length && !panel.textContent.trim()) {
            tabs[index].hidden = true;
            return false;
        }
        return true;
    });
    if (!available.length) return;

    function activate(index) {
        tabs.forEach((tab, tabIndex) => {
            const selected = index === tabIndex;
            tab.classList.toggle('tab-active', selected);
            tab.setAttribute('aria-selected', String(selected));
            tab.tabIndex = selected ? 0 : -1;
            panels[tabIndex].classList.toggle('hidden', !selected);
        });
    }

    for (const index of available) {
        const tab = tabs[index];
        const panel = panels[index];
        const id = `daisy-form-tabs-${groupIndex}-${index}`;
        tab.id ||= `${id}-tab`;
        panel.id ||= `${id}-panel`;
        tab.setAttribute('role', 'tab');
        tab.setAttribute('aria-controls', panel.id);
        panel.setAttribute('role', 'tabpanel');
        panel.setAttribute('aria-labelledby', tab.id);
        tab.addEventListener('click', () => activate(index));
        tab.addEventListener('keydown', event => {
            const position = available.indexOf(index);
            const rtl = getComputedStyle(group).direction === 'rtl';
            let next;

            switch (event.key) {
                case 'Home':
                    next = 0;
                    break;
                case 'End':
                    next = available.length - 1;
                    break;
                case 'ArrowLeft':
                case 'ArrowRight': {
                    const forward = (event.key === 'ArrowRight') !== rtl;
                    next = (position + (forward ? 1 : -1) + available.length) % available.length;
                    break;
                }
                default:
                    return;
            }

            event.preventDefault();
            activate(available[next]);
            tabs[available[next]].focus();
        });
    }

    const preferred = group.hasAttribute('data-prefer-named-tab')
        ? available.find(index => !panels[index].hasAttribute('data-default-form-panel'))
        : available.find(index => tabs[index].classList.contains('tab-active'));
    activate(available.find(index => panels[index].querySelector('.errorlist')) ?? preferred ?? available[0]);

    let handlingInvalid = false;
    group.closest('form')?.addEventListener('invalid', event => {
        if (handlingInvalid) return;
        handlingInvalid = true;
        queueMicrotask(() => { handlingInvalid = false; });
        const index = available.find(index => panels[index].contains(event.target));
        if (index !== undefined) activate(index);
    }, true);
});
