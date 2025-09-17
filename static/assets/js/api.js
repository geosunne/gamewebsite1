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
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Games API methods
    async getGames(params = {}) {
        const queryString = new URLSearchParams(params).toString();
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
        const queryString = new URLSearchParams(params).toString();
        const endpoint = queryString ? `/categories/${categoryId}/games?${queryString}` : `/categories/${categoryId}/games`;
        return this.request(endpoint);
    }

    // Search API methods
    async searchGames(query, params = {}) {
        const searchParams = new URLSearchParams({ q: query, ...params }).toString();
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
    }

    // Convert API game format to legacy format
    convertGameFormat(apiGame) {
        return {
            id: apiGame.slug || apiGame.id, // Use slug as ID for backward compatibility
            title: apiGame.title,
            description: apiGame.description,
            thumbnail: apiGame.thumbnail_url || '',
            category: apiGame.category_name,
            tags: apiGame.tags || [],
            rating: apiGame.rating,
            plays: apiGame.total_plays,
            isFeatured: apiGame.is_featured,
            isNew: apiGame.is_new,
            gameUrl: apiGame.game_url,
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
            console.error('Error fetching game:', error);
            return null;
        }
    }

    async getFeaturedGames() {
        try {
            const games = await this.api.getFeaturedGames();
            return games.map(game => this.convertGameFormat(game));
        } catch (error) {
            console.error('Error fetching featured games:', error);
            return [];
        }
    }

    async getNewGames(limit = 6) {
        try {
            const games = await this.api.getNewGames(limit);
            return games.map(game => this.convertGameFormat(game));
        } catch (error) {
            console.error('Error fetching new games:', error);
            return [];
        }
    }

    async getPopularGames(limit = 6) {
        try {
            const games = await this.api.getPopularGames(limit);
            return games.map(game => this.convertGameFormat(game));
        } catch (error) {
            console.error('Error fetching popular games:', error);
            return [];
        }
    }

    async getGamesByCategory(category) {
        try {
            const games = await this.api.getGamesByCategory(category);
            return games.map(game => this.convertGameFormat(game));
        } catch (error) {
            console.error('Error fetching games by category:', error);
            return [];
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
            console.error('Error fetching categories:', error);
            return [];
        }
    }

    async searchGames(query) {
        try {
            const response = await this.api.searchGames(query);
            return response.games.map(game => this.convertGameFormat(game));
        } catch (error) {
            console.error('Error searching games:', error);
            return [];
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
            console.error('Error recording game play:', error);
        }
    }
}

// Global API instance for backward compatibility
const GAMES_API = new GameDataAdapter();

// Maintain backward compatibility with old GAMES_DATA object
const GAMES_DATA = {
    games: [],
    _loaded: false,

    async _ensureLoaded() {
        if (!this._loaded) {
            try {
                const response = await GAMES_API.api.getGames({ per_page: 100 });
                this.games = response.games.map(game => GAMES_API.convertGameFormat(game));
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

// Export for Node.js compatibility
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { GameAPI, GameDataAdapter, GAMES_API, GAMES_DATA };
}