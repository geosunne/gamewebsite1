// Static API client for BTW Games - uses pre-loaded data instead of server calls
class GameAPI {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
        this.allGamesData = null;
        this.newGamesData = null;
        this.categoriesData = null;
        this.loadStaticData();
    }

    async loadStaticData() {
        try {
            // Load pre-generated static data
            const [allGamesResponse, newGamesResponse, categoriesResponse] = await Promise.all([
                fetch('/all_games.json'),
                fetch('/new_games.json'),
                fetch('/categories.json')
            ]);

            this.allGamesData = await allGamesResponse.json();
            this.newGamesData = await newGamesResponse.json();
            this.categoriesData = await categoriesResponse.json();
        } catch (error) {
            console.error('Failed to load static data:', error);
            // Fallback to empty data
            this.allGamesData = { games: [] };
            this.newGamesData = { games: [] };
            this.categoriesData = { categories: [] };
        }
    }

    // Wait for data to be loaded
    async ensureDataLoaded() {
        while (!this.allGamesData || !this.newGamesData || !this.categoriesData) {
            await new Promise(resolve => setTimeout(resolve, 10));
        }
    }

    // Games API methods - now use static data
    async getGames(params = {}) {
        await this.ensureDataLoaded();

        let games = [...this.allGamesData.games];

        // Apply filters
        if (params.category) {
            games = games.filter(game => game.category_name === params.category);
        }

        if (params.new) {
            games = games.filter(game => game.is_new);
        }

        if (params.featured) {
            games = games.filter(game => game.is_featured);
        }

        // Apply sorting
        if (params.sort === 'newest') {
            games.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        } else if (params.sort === 'popular') {
            games.sort((a, b) => (b.total_plays || 0) - (a.total_plays || 0));
        }

        // Apply pagination
        const perPage = parseInt(params.per_page || 20);
        const page = parseInt(params.page || 1);
        const start = (page - 1) * perPage;
        const paginatedGames = games.slice(start, start + perPage);

        return {
            games: paginatedGames,
            total: games.length,
            page,
            per_page: perPage,
            total_pages: Math.ceil(games.length / perPage)
        };
    }

    async getGame(gameId) {
        await this.ensureDataLoaded();
        const game = this.allGamesData.games.find(g => g.id == gameId);
        return game ? { game } : null;
    }

    async getGameBySlug(slug) {
        await this.ensureDataLoaded();
        const game = this.allGamesData.games.find(g => g.slug === slug);
        return game ? { game } : null;
    }

    async recordGamePlay(gameId, duration = 0) {
        // Static version - just log the play (no server call)
        console.log(`Game play recorded: ${gameId}, duration: ${duration}s`);
        return { success: true };
    }

    // Categories API methods
    async getCategories() {
        await this.ensureDataLoaded();
        return this.categoriesData;
    }

    async getGamesByCategory(categoryId, params = {}) {
        await this.ensureDataLoaded();

        // Find category name by ID
        const category = this.categoriesData.categories.find(c => c.id == categoryId);
        if (!category) return { games: [] };

        return this.getGames({ ...params, category: category.name });
    }

    // Search API methods
    async searchGames(query, params = {}) {
        await this.ensureDataLoaded();

        const searchQuery = query.toLowerCase();
        const games = this.allGamesData.games.filter(game =>
            game.title.toLowerCase().includes(searchQuery) ||
            game.description.toLowerCase().includes(searchQuery) ||
            (game.tags && game.tags.some(tag => tag.toLowerCase().includes(searchQuery)))
        );

        return {
            games,
            total: games.length,
            query
        };
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
            id: apiGame.slug || apiGame.id,
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
            let response;
            if (isNaN(gameId)) {
                response = await this.api.getGameBySlug(gameId);
            } else {
                response = await this.api.getGame(gameId);
            }
            return response ? this.convertGameFormat(response.game) : null;
        } catch (error) {
            console.error('Error fetching game:', error);
            return null;
        }
    }

    async getFeaturedGames(limit = 6) {
        try {
            const games = await this.api.getFeaturedGames(limit);
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
            const response = await this.api.getGames({ category });
            return response.games.map(game => this.convertGameFormat(game));
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

    // Record game play for analytics (static version)
    async recordPlay(gameId, duration = 0) {
        try {
            await this.api.recordGamePlay(gameId, duration);
        } catch (error) {
            console.error('Error recording game play:', error);
        }
    }

    // Ensure data is loaded
    async _ensureLoaded() {
        await this.api.ensureDataLoaded();
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
                await GAMES_API._ensureLoaded();
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

    async getFeaturedGames(limit = 6) {
        return await GAMES_API.getFeaturedGames(limit);
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