// NEW uses the catalog's first-added timestamp, never a provider release date.
(() => {
    const windowMs = 14 * 24 * 60 * 60 * 1000;
    function isRecent(game, now = Date.now()) {
        const added = Date.parse(game.catalog_added_at || '');
        return Number.isFinite(added) && added <= now && now - added < windowMs;
    }
    function expireBadges() {
        const now = Date.now();
        let nextExpiry = Infinity;
        let removed = false;
        document.querySelectorAll('[data-new-until]').forEach(badge => {
            const expiry = Date.parse(badge.dataset.newUntil);
            if (!Number.isFinite(expiry) || expiry <= now) {
                const card = badge.closest('[data-recent-games] .game-card');
                if (card) card.remove();
                else badge.remove();
                removed = true;
            }
            else nextExpiry = Math.min(nextExpiry, expiry);
        });
        document.querySelectorAll('[data-recent-games]').forEach(list => {
            if (!list.querySelector('.game-card')) list.innerHTML = '<p class="section-note">No games added in the last 14 days. <a href="/games">Browse all games</a>.</p>';
        });
        if (removed) document.dispatchEvent(new Event('catalog-status-changed'));
        if (Number.isFinite(nextExpiry)) {
            clearTimeout(expireBadges.timer);
            expireBadges.timer = setTimeout(expireBadges, Math.min(nextExpiry - now + 1, 60 * 60 * 1000));
        }
    }
    window.BTWCatalogStatus = { isRecent };
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', expireBadges, { once: true });
    else expireBadges();
    document.addEventListener('visibilitychange', () => {
        if (!document.hidden) expireBadges();
    });
})();
