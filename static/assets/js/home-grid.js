// Match CSS Grid's dense placement and keep the longest complete set of rows.
(() => {
    function span(start, end) {
        const values = [start, end].map(value => Number(/\bspan\s+(\d+)/.exec(value || '')?.[1]) || 1);
        return Math.max(...values);
    }

    function completePrefix(items, columns) {
        const cells = [];
        let used = 0;
        let best = 0;
        items.forEach((item, index) => {
            const width = Math.min(item.columns, columns);
            const height = item.rows;
            let row = 0;
            let column = 0;
            let found = false;
            while (!found) {
                for (column = 0; column <= columns - width; column += 1) {
                    found = true;
                    for (let y = row; y < row + height && found; y += 1) {
                        for (let x = column; x < column + width; x += 1) {
                            if (cells[y]?.[x]) { found = false; break; }
                        }
                    }
                    if (found) break;
                }
                if (!found) row += 1;
            }
            for (let y = row; y < row + height; y += 1) {
                cells[y] ||= [];
                for (let x = column; x < column + width; x += 1) cells[y][x] = true;
            }
            used += width * height;
            if (used === cells.length * columns) best = index + 1;
        });
        return best;
    }

    if (typeof module !== 'undefined' && module.exports) module.exports = { span, completePrefix };
    if (typeof document === 'undefined') return;

    function balanceGrid(grid) {
        const cards = [...grid.children].filter(card => card.matches('.game-card'));
        cards.forEach(card => card.classList.remove('is-row-trimmed'));
        grid.style.removeProperty('--home-grid-template');
        if (!cards.length || !grid.clientWidth) return;
        const items = cards.map(card => {
            const style = getComputedStyle(card);
            return { columns: span(style.gridColumnStart, style.gridColumnEnd), rows: span(style.gridRowStart, style.gridRowEnd) };
        });
        let columns = getComputedStyle(grid).gridTemplateColumns.split(/\s+/).filter(value => value && value !== 'none').length;
        if (!columns) return;
        if (cards.length < columns) {
            columns = Math.max(Math.max(...items.map(item => item.columns)), cards.length);
            grid.style.setProperty('--home-grid-template', `repeat(${columns}, minmax(0, 1fr))`);
        }
        const visible = completePrefix(items, columns);
        if (!visible) return; // Keep discovery usable if an unsupported placement cannot be balanced.
        const focused = document.activeElement;
        cards.forEach((card, index) => card.classList.toggle('is-row-trimmed', index >= visible));
        if (cards.slice(visible).some(card => card.contains(focused))) cards[visible - 1].focus();
    }

    function balanceAll() {
        document.querySelectorAll('.home-main .home-games-grid').forEach(balanceGrid);
    }
    let frame = 0;
    function schedule() {
        if (frame) return;
        frame = requestAnimationFrame(() => { frame = 0; balanceAll(); });
    }
    function start() {
        balanceAll();
        const grids = [...document.querySelectorAll('.home-main .home-games-grid')];
        if (typeof ResizeObserver === 'function') {
            const widths = new WeakMap(grids.map(grid => [grid, grid.getBoundingClientRect().width]));
            const resize = new ResizeObserver(entries => {
                let changed = false;
                entries.forEach(({ target, contentRect }) => {
                    if (Math.abs((widths.get(target) || 0) - contentRect.width) > 0.5) {
                        widths.set(target, contentRect.width);
                        changed = true;
                    }
                });
                if (changed) schedule();
            });
            grids.forEach(grid => resize.observe(grid));
        }
        const mutations = new MutationObserver(schedule);
        grids.forEach(grid => mutations.observe(grid, { childList: true }));
        window.addEventListener('resize', schedule);
        document.addEventListener('catalog-status-changed', schedule);
    }
    window.balanceHomeGameRows = balanceAll;
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once: true });
    else start();
})();
