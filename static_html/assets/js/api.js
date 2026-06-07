// API client for BTW Games Flask backend
class GameAPI {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
    }

    // Generic API request method
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            const contentType = response.headers.get('content-type') || '';
            if (!contentType.includes('application/json')) {
                throw new Error(`Expected JSON response from ${url}`);
            }
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }

            return data;
        } catch (error) {
            throw error;
        }
    }

    // Games API methods
    async getGames(params = {}) {
        // Filter out undefined/null values
        const cleanParams = Object.fromEntries(
            Object.entries(params).filter(([_, v]) => v != null)
        );
        const queryString = new URLSearchParams(cleanParams).toString();
        const endpoint = queryString ? `/games?${queryString}` : '/games';
        return this.request(endpoint);
    }

    async getGame(gameId) {
        return this.request(`/games/${gameId}`);
    }

    async getGameBySlug(slug) {
        return this.request(`/games/slug/${slug}`);
    }

    async recordGamePlay(gameId, duration = 0) {
        return this.request(`/games/${gameId}/play`, {
            method: 'POST',
            body: JSON.stringify({ duration })
        });
    }

    // Categories API methods
    async getCategories() {
        return this.request('/categories');
    }

    async getGamesByCategory(categoryId, params = {}) {
        // Filter out undefined/null values
        const cleanParams = Object.fromEntries(
            Object.entries(params).filter(([_, v]) => v != null)
        );
        const queryString = new URLSearchParams(cleanParams).toString();
        const endpoint = queryString ? `/categories/${categoryId}/games?${queryString}` : `/categories/${categoryId}/games`;
        return this.request(endpoint);
    }

    // Search API methods
    async searchGames(query, params = {}) {
        // Filter out undefined/null values
        const allParams = { q: query, ...params };
        const cleanParams = Object.fromEntries(
            Object.entries(allParams).filter(([_, v]) => v != null)
        );
        const searchParams = new URLSearchParams(cleanParams).toString();
        return this.request(`/search?${searchParams}`);
    }

    // Statistics API methods
    async getGamesStats() {
        return this.request('/stats/games');
    }

    async getGameStats(gameId) {
        return this.request(`/stats/games/${gameId}`);
    }

    // Utility methods for filtering and sorting
    async getFeaturedGames(limit = 6) {
        const response = await this.getGames({
            featured: true,
            per_page: limit,
            sort: 'popular'
        });
        return response.games;
    }

    async getNewGames(limit = 6) {
        const response = await this.getGames({
            new: true,
            per_page: limit,
            sort: 'newest'
        });
        return response.games;
    }

    async getPopularGames(limit = 6) {
        const response = await this.getGames({
            per_page: limit,
            sort: 'popular'
        });
        return response.games;
    }

    async getGamesByCategory(category, params = {}) {
        const response = await this.getGames({
            category,
            ...params
        });
        return response.games;
    }
}

// Game data adapter to match the old static data format
class GameDataAdapter {
    constructor() {
        this.api = new GameAPI();
        this.cachedCategories = null;
        this.cachedStaticGames = null;
    }

    async getStaticGames() {
        if (!this.cachedStaticGames) {
            const response = await fetch('/all_games.json');
            const data = await response.json();
            this.cachedStaticGames = Array.isArray(data) ? data : (data.games || []);
        }
        return this.cachedStaticGames;
    }

    async getStaticCategories() {
        if (!this.cachedCategories) {
            const response = await fetch('/categories.json');
            const data = await response.json();
            this.cachedCategories = data.map(cat => cat.name || cat);
        }
        return this.cachedCategories;
    }

    sortGames(games, sort = 'popular') {
        const sorted = [...games];
        if (sort === 'newest') {
            sorted.sort((a, b) => new Date(b.created_at || b.release_date || 0) - new Date(a.created_at || a.release_date || 0));
        } else if (sort === 'rating') {
            sorted.sort((a, b) => (b.rating || 0) - (a.rating || 0));
        } else if (sort === 'title') {
            sorted.sort((a, b) => (a.title || '').localeCompare(b.title || ''));
        } else {
            sorted.sort((a, b) => (b.total_plays || b.plays || 0) - (a.total_plays || a.plays || 0));
        }
        return sorted;
    }

    async getStaticGamesList(params = {}) {
        let games = (await this.getStaticGames()).filter(game => game.is_active !== false);
        if (params.featured) {
            games = games.filter(game => game.is_featured || game.isFeatured);
        }
        if (params.new) {
            games = games.filter(game => game.is_new || game.isNew);
        }
        if (params.category && params.category !== 'all') {
            games = games.filter(game => (game.category_name || game.category) === params.category);
        }
        if (params.q) {
            const query = String(params.q).toLowerCase();
            games = games.filter(game => [game.title, game.description, game.category_name, ...(game.tags || [])]
                .filter(Boolean)
                .join(' ')
                .toLowerCase()
                .includes(query));
        }
        games = this.sortGames(games, params.sort);
        const limit = Number(params.per_page || params.limit || games.length);
        return games.slice(0, limit).map(game => this.convertGameFormat(game));
    }

    // Convert API game format to legacy format
    convertGameFormat(apiGame) {
        return {
            id: apiGame.slug || apiGame.id, // Use slug as ID for backward compatibility
            slug: apiGame.slug || apiGame.id,
            title: apiGame.title,
            description: apiGame.description,
            thumbnail: apiGame.thumbnail_url || '',
            thumbnail_url: apiGame.thumbnail_url || '',
            category: apiGame.category_name,
            tags: apiGame.tags || [],
            rating: apiGame.rating,
            plays: apiGame.total_plays,
            isFeatured: apiGame.is_featured,
            isNew: apiGame.is_new,
            sourceUrl: apiGame.game_url,
            gameUrl: apiGame.iframe_url || apiGame.game_url,
            iframeUrl: apiGame.iframe_url || apiGame.game_url,
            controls: apiGame.controls || {},
            features: apiGame.features || [],
            releaseDate: apiGame.release_date
        };
    }

    // Legacy API compatibility methods
    async getGame(gameId) {
        try {
            // Try to get by slug first, then by ID
            let response;
            if (isNaN(gameId)) {
                response = await this.api.getGameBySlug(gameId);
            } else {
                response = await this.api.getGame(gameId);
            }
            return this.convertGameFormat(response.game);
        } catch (error) {
            const games = await this.getStaticGames();
            const game = games.find(item => String(item.slug || item.id) === String(gameId));
            return game ? this.convertGameFormat(game) : null;
        }
    }

    async getFeaturedGames() {
        try {
            const games = await this.api.getFeaturedGames();
            return games.map(game => this.convertGameFormat(game));
        } catch (error) {
            return await this.getStaticGamesList({ featured: true, sort: 'popular', per_page: 6 });
        }
    }

    async getNewGames(limit = 6) {
        try {
            const games = await this.api.getNewGames(limit);
            return games.map(game => this.convertGameFormat(game));
        } catch (error) {
            return await this.getStaticGamesList({ new: true, sort: 'newest', per_page: limit });
        }
    }

    async getPopularGames(limit = 6) {
        try {
            const games = await this.api.getPopularGames(limit);
            return games.map(game => this.convertGameFormat(game));
        } catch (error) {
            return await this.getStaticGamesList({ sort: 'popular', per_page: limit });
        }
    }

    async getGamesByCategory(category) {
        try {
            const games = await this.api.getGamesByCategory(category);
            return games.map(game => this.convertGameFormat(game));
        } catch (error) {
            return await this.getStaticGamesList({ category, sort: 'popular' });
        }
    }

    async getAllCategories() {
        try {
            if (!this.cachedCategories) {
                const response = await this.api.getCategories();
                this.cachedCategories = response.categories.map(cat => cat.name);
            }
            return this.cachedCategories;
        } catch (error) {
            return await this.getStaticCategories();
        }
    }

    async searchGames(query) {
        try {
            const response = await this.api.searchGames(query);
            return response.games.map(game => this.convertGameFormat(game));
        } catch (error) {
            return await this.getStaticGamesList({ q: query, sort: 'popular' });
        }
    }

    // Record game play for analytics
    async recordPlay(gameId, duration = 0) {
        try {
            // Convert slug to numeric ID if needed
            let numericGameId = gameId;
            if (isNaN(gameId)) {
                const game = await this.api.getGameBySlug(gameId);
                numericGameId = game.game.id;
            }
            await this.api.recordGamePlay(numericGameId, duration);
        } catch (error) {
            // Static deployments do not expose analytics write endpoints.
        }
    }
}

// Global API instance for backward compatibility
const GAMES_API = new GameDataAdapter();

// Maintain backward compatibility with old GAMES_DATA object
// Only define if not already defined by games-data.js
if (typeof GAMES_DATA === 'undefined') {
    var GAMES_DATA = {
        games: [],
        _loaded: false,

        async _ensureLoaded() {
            if (!this._loaded) {
                try {
                    this.games = await GAMES_API.getStaticGamesList({ per_page: 1000, sort: 'popular' });
                    this._loaded = true;
                } catch (error) {
                    console.error('Error loading games data:', error);
                }
            }
        },

        async getGame(gameId) {
            return await GAMES_API.getGame(gameId);
        },

        async getFeaturedGames() {
            return await GAMES_API.getFeaturedGames();
        },

        async getNewGames(limit = 6) {
            return await GAMES_API.getNewGames(limit);
        },

        async getGamesByCategory(category) {
            return await GAMES_API.getGamesByCategory(category);
        },

        async getAllCategories() {
            return await GAMES_API.getAllCategories();
        },

        async searchGames(query) {
            return await GAMES_API.searchGames(query);
        },

        async getPopularGames(limit = 6) {
            return await GAMES_API.getPopularGames(limit);
        }
    };
}

// Export for Node.js compatibility
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { GameAPI, GameDataAdapter, GAMES_API, GAMES_DATA };
}
