// 游戏数据管理
const GAMES_DATA = {
    // 示例游戏数据
    games: [
        {
            id: 'monster-survivors',
            title: 'Monster Survivors',
            description: 'An intense survival game where you battle endless waves of monsters',
            thumbnail: 'https://btwgame.com/images/monster-survivors-thumb.jpg',
            category: 'Action',
            tags: ['Survival', 'Action', 'Shooter'],
            rating: 4.5,
            plays: 15420,
            isFeatured: true,
            isNew: false,
            gameUrl: 'https://cloud.onlinegames.io/games/2025/unity/monster-survivors/index-og.html',
            controls: {
                'WASD': 'Move your character',
                'Mouse': 'Aim your weapon',
                'Left Click': 'Fire weapon',
                'Space': 'Special ability',
                'E': 'Interact / Pick up',
                'ESC': 'Pause menu'
            },
            features: [
                'Intense Combat',
                'Easy Controls',
                'Progressive Difficulty',
                'Achievements',
                'Power-ups',
                'Strategic Gameplay'
            ],
            releaseDate: '2024-12-01'
        },
        {
            id: 'puzzle-master',
            title: 'Puzzle Master',
            description: 'Challenge your mind with hundreds of brain-teasing puzzles',
            thumbnail: 'https://btwgame.com/images/puzzle-master-thumb.jpg',
            category: 'Puzzle',
            tags: ['Puzzle', 'Brain', 'Logic'],
            rating: 4.3,
            plays: 8750,
            isFeatured: true,
            isNew: false,
            gameUrl: 'https://example.com/puzzle-master',
            controls: {
                'Mouse': 'Click to interact',
                'Space': 'Hint',
                'R': 'Reset puzzle',
                'ESC': 'Menu'
            },
            features: [
                '500+ Puzzles',
                'Multiple Difficulty Levels',
                'Hint System',
                'Progress Tracking',
                'Daily Challenges'
            ],
            releaseDate: '2024-11-15'
        },
        {
            id: 'racing-fever',
            title: 'Racing Fever',
            description: 'High-speed racing action with stunning graphics and realistic physics',
            thumbnail: 'https://btwgame.com/images/racing-fever-thumb.jpg',
            category: 'Racing',
            tags: ['Racing', 'Cars', 'Speed'],
            rating: 4.7,
            plays: 22100,
            isFeatured: false,
            isNew: true,
            gameUrl: 'https://example.com/racing-fever',
            controls: {
                'Arrow Keys': 'Steer and accelerate',
                'Space': 'Handbrake',
                'C': 'Change camera',
                'N': 'Nitro boost'
            },
            features: [
                'Realistic Physics',
                'Multiple Tracks',
                'Car Customization',
                'Tournament Mode',
                'Leaderboards'
            ],
            releaseDate: '2025-01-10'
        },
        {
            id: 'space-explorer',
            title: 'Space Explorer',
            description: 'Explore the vast universe and discover new planets and civilizations',
            thumbnail: 'https://btwgame.com/images/space-explorer-thumb.jpg',
            category: 'Adventure',
            tags: ['Space', 'Exploration', 'Sci-Fi'],
            rating: 4.4,
            plays: 12300,
            isFeatured: false,
            isNew: true,
            gameUrl: 'https://example.com/space-explorer',
            controls: {
                'WASD': 'Move spaceship',
                'Mouse': 'Look around',
                'Left Click': 'Interact',
                'Space': 'Boost',
                'M': 'Map'
            },
            features: [
                'Open World',
                'Planet Exploration',
                'Resource Management',
                'Alien Encounters',
                'Spaceship Upgrades'
            ],
            releaseDate: '2025-01-05'
        },
        {
            id: 'tower-defense-pro',
            title: 'Tower Defense Pro',
            description: 'Defend your base against waves of enemies with strategic tower placement',
            thumbnail: 'https://btwgame.com/images/tower-defense-thumb.jpg',
            category: 'Strategy',
            tags: ['Strategy', 'Defense', 'Tower'],
            rating: 4.6,
            plays: 18900,
            isFeatured: true,
            isNew: false,
            gameUrl: 'https://example.com/tower-defense-pro',
            controls: {
                'Mouse': 'Select and place towers',
                'Space': 'Pause/Resume',
                'U': 'Upgrade tower',
                'S': 'Sell tower'
            },
            features: [
                'Multiple Tower Types',
                'Upgrade System',
                'Boss Battles',
                'Multiple Maps',
                'Achievement System'
            ],
            releaseDate: '2024-10-20'
        },
        {
            id: 'ninja-warrior',
            title: 'Ninja Warrior',
            description: 'Master the art of stealth and combat in this action-packed ninja adventure',
            thumbnail: 'https://btwgame.com/images/ninja-warrior-thumb.jpg',
            category: 'Action',
            tags: ['Ninja', 'Action', 'Stealth'],
            rating: 4.2,
            plays: 9800,
            isFeatured: false,
            isNew: true,
            gameUrl: 'https://example.com/ninja-warrior',
            controls: {
                'Arrow Keys': 'Move',
                'Z': 'Attack',
                'X': 'Jump',
                'C': 'Stealth mode',
                'Space': 'Throw shuriken'
            },
            features: [
                'Stealth Gameplay',
                'Combat System',
                'Multiple Weapons',
                'Challenging Levels',
                'Boss Fights'
            ],
            releaseDate: '2025-01-03'
        }
    ],

    // 获取游戏数据的方法
    getGame: function(gameId) {
        return this.games.find(game => game.id === gameId);
    },

    getFeaturedGames: function() {
        return this.games.filter(game => game.isFeatured);
    },

    getNewGames: function() {
        return this.games.filter(game => game.isNew);
    },

    getGamesByCategory: function(category) {
        return this.games.filter(game => game.category === category);
    },

    getAllCategories: function() {
        return [...new Set(this.games.map(game => game.category))];
    },

    searchGames: function(query) {
        const searchTerm = query.toLowerCase();
        return this.games.filter(game =>
            game.title.toLowerCase().includes(searchTerm) ||
            game.description.toLowerCase().includes(searchTerm) ||
            game.tags.some(tag => tag.toLowerCase().includes(searchTerm))
        );
    },

    getPopularGames: function() {
        return this.games.sort((a, b) => b.plays - a.plays).slice(0, 6);
    }
};

// 导出数据供其他文件使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GAMES_DATA;
}