(() => {
    const search = document.getElementById('global-search');
    if (!search) return;
    const input = document.getElementById('global-search-input');
    const dropdown = document.getElementById('global-search-dropdown');
    const status = document.getElementById('global-search-status');
    const results = document.getElementById('global-search-results');
    let timer, controller, sequence = 0;

    const historyKey = `daisy-search:${search.dataset.url}:${search.dataset.user}`;
    let recent = [];
    try {
        const saved = JSON.parse(sessionStorage.getItem(historyKey));
        if (Array.isArray(saved)) recent = saved.slice(0, 3);
    } catch {
        // Storage may be unavailable or contain invalid data.
    }

    function renderResults(items) {
        results.replaceChildren();
        let lastGroup;
        items.forEach(result => {
            if (lastGroup !== result.group) {
                const heading = document.createElement('li');
                heading.className = 'menu-title';
                heading.textContent = result.group;
                results.appendChild(heading);
                lastGroup = result.group;
            }
            const row = document.createElement('li');
            const link = document.createElement('a');
            link.className = 'daisy-search-result';
            const url = new URL(result.url, document.baseURI);
            if (url.origin !== location.origin || !['http:', 'https:'].includes(url.protocol)) {
                return;
            }
            link.href = url.href;
            const remember = () => {
                recent = [result, ...recent.filter(item => item.url !== result.url)].slice(0, 3);
                try {
                    sessionStorage.setItem(historyKey, JSON.stringify(recent));
                } catch {
                    // Storage may be disabled.
                }
            };
            link.addEventListener('click', remember);
            link.addEventListener('auxclick', event => {
                if (event.button === 1) remember();
            });
            const label = document.createElement('span');
            label.textContent = result.label;
            const detail = document.createElement('small');
            detail.textContent = result.description;
            const summary = document.createElement('span');
            summary.className = 'daisy-search-summary';
            summary.append(label, detail);
            link.appendChild(summary);
            row.appendChild(link);
            results.appendChild(row);
        });
    }

    function openSearch() {
        if (!input.value.trim()) {
            status.textContent = recent.length ? '' : search.dataset.prompt;
            renderResults(recent.map(item => ({...item, group: search.dataset.recent})));
        }
        dropdown.hidden = false;
        search.classList.add('is-open');
    }
    function closeSearch() {
        dropdown.hidden = true;
        search.classList.remove('is-open');
    }
    input.addEventListener('focus', openSearch);
    input.addEventListener('click', openSearch);
    document.addEventListener('pointerdown', event => {
        if (!search.contains(event.target)) closeSearch();
    });
    search.addEventListener('focusout', event => {
        if (!search.contains(event.relatedTarget)) closeSearch();
    });
    document.addEventListener('keydown', event => {
        if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
            event.preventDefault();
            input.focus();
            openSearch();
        } else if (event.key === 'Escape' && !dropdown.hidden) {
            event.preventDefault();
            input.focus();
            closeSearch();
        }
    });
    input.addEventListener('keydown', event => {
        if (event.key === 'ArrowDown') {
            const first = results.querySelector('a');
            if (first) { event.preventDefault(); openSearch(); first.focus(); }
        }
    });
    results.addEventListener('keydown', event => {
        if (!['ArrowUp', 'ArrowDown'].includes(event.key)) return;
        const links = Array.from(results.querySelectorAll('a'));
        const index = links.indexOf(document.activeElement);
        if (index < 0) return;
        event.preventDefault();
        if (event.key === 'ArrowUp' && index === 0) input.focus();
        else links[Math.max(0, Math.min(links.length - 1, index + (event.key === 'ArrowDown' ? 1 : -1)))].focus();
    });
    input.addEventListener('input', () => {
        clearTimeout(timer);
        if (controller) controller.abort();
        const current = ++sequence;
        results.replaceChildren();
        const term = input.value.trim();
        status.textContent = term.length < 2 ? search.dataset.prompt : search.dataset.loading;
        openSearch();
        if (term.length < 2) return;
        timer = setTimeout(async () => {
            controller = new AbortController();
            try {
                const url = new URL(search.dataset.url, document.baseURI);
                url.searchParams.set('q', term);
                const response = await fetch(url, {signal: controller.signal, headers: {'Accept': 'application/json'}});
                if (!response.ok || response.redirected) throw new Error('Search failed');
                const data = await response.json();
                if (current !== sequence) return;
                status.textContent = data.results.length ? '' : search.dataset.empty;
                renderResults(data.results);
            } catch (error) {
                if (error.name !== 'AbortError' && current === sequence) status.textContent = search.dataset.error;
            }
        }, 250);
    });
})();
