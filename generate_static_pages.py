#!/usr/bin/env python3
"""
Generate static HTML pages for all games and update all_games.json
"""
import requests
import json
import os
import shutil
import time
import re
import hashlib
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
from html import escape as html_escape
from urllib.parse import quote, urlparse
from datetime import datetime

BASE_URL = "http://localhost:8000"
SITE_URL = "https://btwgame.com"
SITE_NAME = "BTW game"
SITE_IMAGE = f"{SITE_URL}/assets/images/btwlogo.png"
INITIAL_CATALOG_CARD_COUNT = 120
CATALOG_PAGE_SIZE = 120
THUMBNAIL_CACHE_DIR = "static/assets/thumbnails"
THUMBNAIL_WIDTH = 320
THUMBNAIL_HEIGHT = 200
THUMBNAIL_VERSION = "cover-16x10-v2"
THUMBNAIL_QUALITY = 82
THUMBNAIL_TIMEOUT = 5
THUMBNAIL_WORKERS = 16

MOJIBAKE_REPLACEMENTS = {
    "Â\xa0": " ",
    "\xa0": " ",
    "Â": "",
    "â": "'",
    "â€™": "'",
    "â": "'",
    "â€˜": "'",
    "â": '"',
    "â€œ": '"',
    "â": '"',
    "â€": '"',
    "â": "-",
    "â€”": "-",
    "â": "-",
    "â€“": "-",
    "â": "-",
    "â€‘": "-",
    "â¦": "...",
    "â€¦": "...",
    "â¢": "-",
    "â€¢": "-",
    "â¼": "",
    "â\x80\x8b": "",
    "\u200b": "",
}

CATEGORY_GUIDES = {
    "Action": {
        "title": "Free action games",
        "intro": "Action games on BTW game focus on quick decisions, movement, timing, and short bursts of pressure. Open a game, learn the controls, and jump into a fast browser session.",
        "sections": [
            ("Fast movement games", "Choose action games when you want dodging, jumping, chasing, combat, or quick restarts."),
            ("Good next categories", "Parkour adds more jumping skill, Shooter adds aiming, and Strategy adds planning to the pressure."),
        ],
        "faq": [
            ("What are action games?", "Action games are browser games built around timing, movement, reactions, and active play."),
            ("Are action games free on BTW game?", "Yes. Action games in this catalog can be played free in the browser without downloads."),
        ],
    },
    "Adventure": {
        "title": "Free adventure games",
        "intro": "Adventure games are about exploring, escaping, solving problems, and discovering what happens next. They fit casual players who want a quick journey with browser-friendly controls.",
        "sections": [
            ("Escape and story games", "Many adventure games give you a situation to read, a route to find, or a small story beat to finish."),
            ("Explore more", "Try Parkour for movement challenges, Puzzle for calmer problem solving, or Simulation for slower exploration."),
        ],
        "faq": [
            ("What makes a game an adventure game?", "Adventure games usually give you a place to explore, a problem to solve, or a journey that moves forward."),
            ("Can adventure games be played quickly?", "Yes. Many adventure games on BTW game are suited to short browser sessions."),
        ],
    },
    "Racing": {
        "title": "Free racing games",
        "intro": "Racing games are built for speed, clean turns, stunts, traffic runs, and quick restarts. Pick a car, bike, or vehicle game and play instantly.",
        "sections": [
            ("Drift and stunt games", "Drift games reward control, while stunt games add ramps, loops, and open spaces."),
            ("Vehicle variety", "The racing shelf can include cars, bikes, traffic driving, boat races, and broader driving simulators."),
        ],
        "faq": [
            ("Are racing games only about cars?", "Mostly, but this category also includes bikes, stunt vehicles, traffic games, and simulators."),
            ("Do racing games need downloads?", "No. BTW game racing games are browser games and open from the game page."),
        ],
    },
    "Puzzle": {
        "title": "Free puzzle games",
        "intro": "Puzzle games give you a slower browser break: match pieces, solve patterns, plan moves, and look for the cleanest answer.",
        "sections": [
            ("Logic and pattern games", "Puzzle games reward attention and planning more than fast clicks."),
            ("Short-session play", "Many puzzle games work well for one board, one level, or one quick attempt."),
        ],
        "faq": [
            ("What are good puzzle games for a short break?", "Try games with clear rules, simple boards, and quick restarts."),
            ("Are puzzle games free on BTW game?", "Yes. The puzzle games listed here are free browser games."),
        ],
    },
    "Sports": {
        "title": "Free sports games",
        "intro": "Sports games turn familiar rules into quick browser matches, shots, races, and arcade-style competitions.",
        "sections": [
            ("Quick matches", "Many sports games are built around compact rounds, penalty shots, hoops, or short attempts."),
            ("Competitive feel", "Try Racing for speed, Action for pressure, or Casual for lower-stress play."),
        ],
        "faq": [
            ("What sports games can I play online?", "BTW game includes soccer, basketball, tennis, golf, and arcade sports games."),
            ("Are sports games quick to start?", "Yes. Most sports games here are designed for instant browser play."),
        ],
    },
    "Strategy": {
        "title": "Free strategy games",
        "intro": "Strategy games ask you to plan, react, defend, build, or choose the next move. They are useful when you want more thinking in a browser game.",
        "sections": [
            ("Planning games", "Tower defense, battle, board, and management games all reward better decisions over time."),
            ("Nearby categories", "Puzzle is calmer, Simulation adds systems, and Action keeps the pace higher."),
        ],
        "faq": [
            ("Are strategy games hard for beginners?", "Some are deeper, but many teach through short rounds and visible feedback."),
            ("Can I play strategy games without an account?", "Yes. These games are presented as free browser games."),
        ],
    },
    "Simulation": {
        "title": "Free simulation games",
        "intro": "Simulation games let you try a role, vehicle, job, or small world. They are good when you want control and discovery instead of constant pressure.",
        "sections": [
            ("Role and job games", "Try a task, learn the loop, and improve over time with familiar goals."),
            ("World and vehicle simulators", "Explore, test controls, and create your own small goals."),
        ],
        "faq": [
            ("Are simulation games relaxing?", "Many are, though some include action or timed challenges."),
            ("What categories are similar?", "Racing, Adventure, and Strategy are strong next shelves."),
        ],
    },
    "Casual": {
        "title": "Free casual games",
        "intro": "Casual games are simple to open, easy to understand, and good for short breaks at home, school, or between tasks.",
        "sections": [
            ("Quick break games", "These games get to the point quickly with simple rules and visible goals."),
            ("Light challenge", "Casual does not always mean easy; it means the game is easy to enter and retry."),
        ],
        "faq": [
            ("What is a casual game?", "A casual game is easy to start, simple to understand, and suited to shorter play sessions."),
            ("Are casual games good for students?", "Many are short and browser-friendly, but players should choose games that fit their setting and rules."),
        ],
    },
    "Clicker": {
        "title": "Free clicker games",
        "intro": "Clicker games turn small actions into visible progress. Click, upgrade, unlock, and watch the numbers or tools grow.",
        "sections": [
            ("Upgrade loops", "Most clicker games are about choosing what to improve next."),
            ("Idle-friendly play", "Some clicker games are easy to check between other activities."),
        ],
        "faq": [
            ("What is a clicker game?", "A clicker game uses repeated taps or clicks to earn progress and unlock upgrades."),
            ("What is similar to clicker games?", "Casual, Simulation, and Strategy games often have related progress loops."),
        ],
    },
    "Cooking": {
        "title": "Free cooking games",
        "intro": "Cooking games are about timing, orders, recipes, and serving customers. They are playful routine games with clear goals and quick feedback.",
        "sections": [
            ("Restaurant routines", "Take orders, prepare food, and keep the line moving."),
            ("Low-pressure progress", "Cooking games are easy to understand and often reward steady improvement."),
        ],
        "faq": [
            ("Are cooking games good for kids?", "Many use clear routines and friendly goals, but families should still choose age-appropriate games."),
            ("What categories are similar?", "Casual, Simulation, and Puzzle are close fits."),
        ],
    },
    "Parkour": {
        "title": "Free parkour games",
        "intro": "Parkour games focus on jumps, timing, routes, obstacles, and retries. They are ideal when you want movement skill without a long tutorial.",
        "sections": [
            ("Obby and obstacle games", "Fail, restart, and improve the route through visible platforms and hazards."),
            ("Speed and rhythm", "Some parkour games feel closer to runner or rhythm games where timing matters most."),
        ],
        "faq": [
            ("Are parkour games hard?", "They can be, but quick restarts make them easy to practice."),
            ("What categories are close to parkour?", "Action, Adventure, and Casual all overlap with parkour games."),
        ],
    },
    "Shooter": {
        "title": "Free shooter games",
        "intro": "Shooter games focus on aim, awareness, and fast reactions. The best first picks have clear controls and quick rounds.",
        "sections": [
            ("Arena and battle games", "Arena shooters reward positioning, awareness, and quick decisions."),
            ("Target games", "Sniper and target games slow the pace and focus on accuracy."),
        ],
        "faq": [
            ("Are shooter games suitable for every player?", "No. Some include combat themes, so younger players should choose with adult guidance."),
            ("What categories are close to shooter games?", "Action, Strategy, and io Games are nearby categories."),
        ],
    },
    "io Games": {
        "title": "Free io games",
        "intro": "Io games are quick competitive browser games with simple rules and fast restarts. They work well for short sessions and easy sharing.",
        "sections": [
            ("Fast competitive rounds", "Move, collect, survive, claim space, or compete with simple controls."),
            ("Quick retries", "The restart loop is short, so these games are easy to sample."),
        ],
        "faq": [
            ("What does io games mean?", "On BTW game it means fast browser games with simple rules, quick rounds, and competitive energy."),
            ("What categories are close to io games?", "Action, Shooter, and Casual are close fits."),
        ],
    },
}

CATEGORY_ORDER = [
    "Action", "Adventure", "Arcade", "Puzzle", "Match & Merge", "Mahjong & Card",
    "Word & Trivia", "Racing", "Driving", "Parking", "Sports", "Soccer",
    "Basketball", "Shooter", "Sniper", "Horror", "Survival", "Parkour",
    "Obby", "Platformer", "Runner", "Simulation", "Management",
    "Idle & Clicker", "Cooking", "Dress Up", "Beauty", "Two Player",
    "Multiplayer", "io Games", "Strategy", "Tower Defense", "Clicker", "Casual"
]

RAIL_CATEGORIES = ["Action", "Puzzle", "Racing", "Shooter", "Parkour", "Sports"]
MIN_PRIMARY_CATEGORY_GAMES = 10
THIN_CATEGORY_FALLBACKS = {
    "Arcade": "Casual",
    "Parking": "Driving",
    "Multiplayer": "io Games",
}
HOME_CATEGORY_LIMIT = 10
GEO_STATIC_PAGES = [
    "/about",
    "/contact",
    "/privacy",
    "/terms",
    "/editorial-policy",
    "/best/free-online-games",
    "/best/browser-games-for-school",
    "/best/quick-games",
    "/best/mobile-browser-games",
    "/best/no-download-games",
]

BEST_PAGE_DEFINITIONS = [
    {
        "slug": "free-online-games",
        "title": "Best free online games",
        "description": "Find free online games on BTW game that open in the browser without installs, accounts, or extra setup.",
        "h1": "Best free online games",
        "intro": "This list highlights free browser games that are easy to open, quick to understand, and useful when you want a short play session.",
        "selectors": {
            "categories": ["Action", "Puzzle", "Racing", "Casual", "Sports"],
        },
        "sections": [
            ("What makes these games good picks?", "They are chosen for fast loading, clear controls, replay value, and broad appeal across casual players."),
            ("How to choose", "Start with action for energy, puzzle for slower thinking, racing for speed, and casual games for lighter breaks."),
        ],
        "faq": [
            ("Are these online games free?", "Yes. BTW game focuses on free browser games that can be opened without a download."),
            ("Do I need an account?", "No. The listed games are intended for instant browser play without account setup on BTW game."),
        ],
    },
    {
        "slug": "browser-games-for-school",
        "title": "Best browser games for school breaks",
        "description": "Quick browser games for students and school breaks, with simple controls and short sessions.",
        "h1": "Best browser games for school breaks",
        "intro": "These games are selected for quick sessions, simple rules, and browser-friendly play. Always follow your school or family rules about when games are allowed.",
        "selectors": {
            "categories": ["Puzzle", "Casual", "Word & Trivia", "Sports", "Cooking"],
        },
        "sections": [
            ("Short-session games", "Pick games with clear rounds, quick restarts, and simple goals when time is limited."),
            ("Lower-pressure choices", "Puzzle, word, cooking, and casual games are often calmer than shooter or horror games."),
        ],
        "faq": [
            ("Are these games school appropriate?", "They are lighter browser-game picks, but players should follow school rules and choose age-appropriate games."),
            ("Can I play without downloading?", "Yes. These picks are browser games and do not require installing an app from BTW game."),
        ],
    },
    {
        "slug": "quick-games",
        "title": "Best quick games",
        "description": "Quick games for short breaks, fast retries, and instant browser play on BTW game.",
        "h1": "Best quick games",
        "intro": "Quick games are useful when you want a fast start, a compact round, and a clean stop after a short break.",
        "selectors": {
            "categories": ["Runner", "Parkour", "Action", "Arcade", "Puzzle"],
        },
        "sections": [
            ("Fast starts", "Look for games with one-screen rules, obvious goals, and immediate feedback."),
            ("Easy stopping points", "Runner, parkour, arcade, and puzzle games often work well because each attempt or level is compact."),
        ],
        "faq": [
            ("What counts as a quick game?", "A quick game starts fast, teaches quickly, and works in short browser sessions."),
            ("Which quick game category should I try first?", "Try Runner or Parkour for movement, Puzzle for calmer play, and Action for faster reactions."),
        ],
    },
    {
        "slug": "mobile-browser-games",
        "title": "Best mobile browser games",
        "description": "Mobile-friendly browser games that are easy to sample on phones, tablets, and desktop browsers.",
        "h1": "Best mobile browser games",
        "intro": "These picks favor simple interactions, clear screens, and game styles that can work well across phones, tablets, and desktop browsers.",
        "selectors": {
            "categories": ["Casual", "Puzzle", "Match & Merge", "Cooking", "Idle & Clicker"],
        },
        "sections": [
            ("Touch-friendly play", "Casual, puzzle, match, cooking, and clicker games often use simple taps, drags, or single-action controls."),
            ("Cross-device browsing", "Open a game page directly in the browser and check the in-game prompts for device-specific controls."),
        ],
        "faq": [
            ("Do all games work on mobile?", "Not every game is ideal on every device. Check the game page and in-game prompts for controls."),
            ("Do I need to install an app?", "No. BTW game links to browser games that open from the page."),
        ],
    },
    {
        "slug": "no-download-games",
        "title": "Best no-download games",
        "description": "No-download games that open directly in the browser for fast free play on BTW game.",
        "h1": "Best no-download games",
        "intro": "No-download games are browser games you can open from the page without installing a separate app or launcher from BTW game.",
        "selectors": {
            "categories": ["Action", "Puzzle", "Racing", "Sports", "Simulation"],
        },
        "sections": [
            ("Why no-download games are useful", "They reduce setup time and make it easier to try several games before choosing one to keep playing."),
            ("Good first picks", "Start with familiar categories like puzzle, racing, sports, or action if you want predictable controls."),
        ],
        "faq": [
            ("What is a no-download game?", "A no-download game opens in the browser without installing a separate app from BTW game."),
            ("Are no-download games free?", "The games listed on BTW game are presented as free browser games."),
        ],
    },
]

CATEGORY_GUIDES.update({
    "Arcade": {
        "title": "Free arcade games",
        "intro": "Arcade games are quick to understand, fast to replay, and built around simple goals that feel good in short browser sessions.",
        "sections": [
            ("Instant-play games", "Arcade games work well when you want a clear objective, quick feedback, and a short round."),
            ("Classic energy", "Try Action for more pressure, Puzzle for more thinking, or Runner for rhythm and timing."),
        ],
        "faq": [
            ("What are arcade games?", "Arcade games are easy-to-start games with compact rules, quick rounds, and score-focused play."),
            ("Do arcade games need downloads?", "No. The arcade games on BTW game run in the browser."),
        ],
    },
    "Match & Merge": {
        "title": "Free match and merge games",
        "intro": "Match and merge games are about spotting patterns, combining pieces, clearing boards, and building satisfying chains.",
        "sections": [
            ("Match, sort, and connect", "Look for tiles, bubbles, fruit, jewels, or blocks that can be matched, merged, sorted, or linked."),
            ("Relaxed puzzle loops", "These games are good for players who want puzzle structure without heavy controls."),
        ],
        "faq": [
            ("What are match and merge games?", "They are puzzle games where you combine, match, sort, or connect items to clear goals."),
            ("Are match games good for short breaks?", "Yes. Most boards and levels are compact enough for quick browser sessions."),
        ],
    },
    "Mahjong & Card": {
        "title": "Free mahjong and card games",
        "intro": "Mahjong, solitaire, chess, and card-style games give you slower decisions, clear boards, and familiar rules in the browser.",
        "sections": [
            ("Board and card classics", "This category groups tile matching, solitaire, mahjong, chess, and similar table games."),
            ("Calmer play", "Try Puzzle for broader logic games or Strategy for deeper planning."),
        ],
        "faq": [
            ("What games are in this category?", "Mahjong, solitaire, chess, card games, and related board-style browser games."),
            ("Can I play mahjong and card games free?", "Yes. Open a game page and play directly in your browser."),
        ],
    },
    "Word & Trivia": {
        "title": "Free word and trivia games",
        "intro": "Word and trivia games focus on letters, clues, questions, memory, and quick knowledge checks.",
        "sections": [
            ("Think with words", "Look for spelling, word building, quiz, and guessing games when you want a lighter mental challenge."),
            ("Nearby shelves", "Puzzle and Casual are good next categories if you want similar short-session play."),
        ],
        "faq": [
            ("What are word and trivia games?", "They are browser games based on words, clues, questions, guessing, or knowledge."),
            ("Are word games free here?", "Yes. These games can be played free on BTW game."),
        ],
    },
    "Driving": {
        "title": "Free driving games",
        "intro": "Driving games cover cars, trucks, buses, bikes, taxis, traffic runs, drifting, and open vehicle challenges.",
        "sections": [
            ("Vehicle control", "Choose driving games when you want steering, braking, traffic, stunt routes, or vehicle handling."),
            ("More speed", "Try Racing for competition or Parking for tighter precision challenges."),
        ],
        "faq": [
            ("Are driving games different from racing games?", "Driving games focus on vehicles and control, while racing games focus more on speed and competition."),
            ("Can I play driving games without downloads?", "Yes. BTW game driving games open in the browser."),
        ],
    },
    "Parking": {
        "title": "Free parking games",
        "intro": "Parking games are precise driving challenges where turns, timing, spacing, and careful movement matter.",
        "sections": [
            ("Precision driving", "Park, reverse, avoid obstacles, and learn the route before trying to move faster."),
            ("Related driving games", "Try Driving for broader vehicle play or Racing when you want speed."),
        ],
        "faq": [
            ("What are parking games?", "Parking games are vehicle games focused on careful movement and positioning."),
            ("Are parking games hard?", "Some are tricky, but quick restarts make them easy to practice."),
        ],
    },
    "Soccer": {
        "title": "Free soccer games",
        "intro": "Soccer games turn shots, passes, penalties, tournaments, and arcade matches into fast browser play.",
        "sections": [
            ("Quick football matches", "Try penalty kicks, head soccer, random soccer, and short match formats."),
            ("More sports", "Basketball and Sports offer nearby competitive games."),
        ],
        "faq": [
            ("Can I play soccer games online free?", "Yes. Soccer games on BTW game are free browser games."),
            ("Are soccer games quick to start?", "Most soccer games here start fast and fit short sessions."),
        ],
    },
    "Basketball": {
        "title": "Free basketball games",
        "intro": "Basketball games focus on shots, hoops, timing, dunks, arcade matches, and quick scoring challenges.",
        "sections": [
            ("Hoops and timing", "Use basketball games when you want short skill attempts or compact competitive matches."),
            ("Nearby games", "Try Sports for more events or Two Player for local matchups."),
        ],
        "faq": [
            ("What basketball games can I play?", "BTW game includes hoop, dunk, and arcade basketball browser games."),
            ("Do basketball games need installs?", "No. They run directly in the browser."),
        ],
    },
    "Sniper": {
        "title": "Free sniper games",
        "intro": "Sniper games slow shooter play down into aim, timing, target selection, and accuracy challenges.",
        "sections": [
            ("Aim carefully", "Sniper games reward patience, clean shots, and reading the scene before acting."),
            ("More shooting", "Try Shooter for broader arena, action, and combat games."),
        ],
        "faq": [
            ("What are sniper games?", "Sniper games are shooting games focused on precision and target accuracy."),
            ("Are sniper games suitable for all players?", "Some include combat themes, so younger players should choose with adult guidance."),
        ],
    },
    "Horror": {
        "title": "Free horror games",
        "intro": "Horror games use suspense, monsters, escape routes, haunted spaces, and tense moments for players who want a scarier challenge.",
        "sections": [
            ("Escape and survive", "Many horror games ask you to avoid danger, explore rooms, and react quickly."),
            ("Choose carefully", "Try Adventure for lighter exploration or Survival for pressure without as much scare focus."),
        ],
        "faq": [
            ("Are horror games for kids?", "Not always. Horror games may include scary themes, so families should choose carefully."),
            ("Can horror games be played in the browser?", "Yes. The horror games listed here are browser games."),
        ],
    },
    "Survival": {
        "title": "Free survival games",
        "intro": "Survival games focus on staying alive, adapting, fighting hazards, collecting resources, or outlasting enemies.",
        "sections": [
            ("Stay alive", "Watch your surroundings, learn threats, and use each attempt to last longer."),
            ("Related pressure", "Try Action, Shooter, or Strategy for similar challenge from different angles."),
        ],
        "faq": [
            ("What are survival games?", "Survival games ask players to stay alive against hazards, enemies, or resource pressure."),
            ("Are survival games free on BTW game?", "Yes. These games can be played free in the browser."),
        ],
    },
    "Obby": {
        "title": "Free obby games",
        "intro": "Obby games are obstacle-course challenges built around jumps, routes, timing, and frequent retries.",
        "sections": [
            ("Obstacle courses", "Jump across platforms, avoid hazards, and improve each route through practice."),
            ("Similar movement games", "Try Parkour, Platformer, and Runner when you want more movement-focused games."),
        ],
        "faq": [
            ("What is an obby game?", "An obby is an obstacle-course game focused on jumps, timing, and platform routes."),
            ("Are obby games good for quick play?", "Yes. Short attempts and quick restarts make them easy to sample."),
        ],
    },
    "Platformer": {
        "title": "Free platformer games",
        "intro": "Platformer games focus on jumping, routes, hazards, timing, and moving through stages with readable controls.",
        "sections": [
            ("Jump and move", "Platformer games reward timing, spacing, and learning the level layout."),
            ("Nearby categories", "Parkour and Runner are good choices when you want faster movement challenges."),
        ],
        "faq": [
            ("What are platformer games?", "Platformer games ask you to move across platforms, avoid hazards, and reach goals."),
            ("Can platformer games be played free?", "Yes. Platformer games here are free browser games."),
        ],
    },
    "Runner": {
        "title": "Free runner games",
        "intro": "Runner games are built around movement, dodging, collecting, and quick reactions through a forward-moving challenge.",
        "sections": [
            ("Endless movement", "Runner games often use lanes, jumps, slides, turns, and quick restarts."),
            ("More timing games", "Try Parkour, Platformer, or Arcade for related timing challenges."),
        ],
        "faq": [
            ("What are runner games?", "Runner games focus on moving forward, avoiding obstacles, and lasting as long as possible."),
            ("Are runner games easy to start?", "Yes. Most runner games use simple controls and short rounds."),
        ],
    },
    "Management": {
        "title": "Free management games",
        "intro": "Management games are about running systems, upgrading businesses, serving customers, organizing resources, and making better choices over time.",
        "sections": [
            ("Build and improve", "Manage shops, farms, restaurants, cities, teams, or other small systems."),
            ("Related progress games", "Try Simulation for role play or Idle & Clicker for upgrade loops."),
        ],
        "faq": [
            ("What are management games?", "Management games ask you to organize resources, upgrades, customers, or systems."),
            ("Are management games relaxing?", "Many are, though some include timers and busy routines."),
        ],
    },
    "Idle & Clicker": {
        "title": "Free idle and clicker games",
        "intro": "Idle and clicker games turn taps, upgrades, and small choices into steady progress you can check in short sessions.",
        "sections": [
            ("Upgrade loops", "Click, earn, improve, unlock, and watch the game grow over time."),
            ("Simple progress", "These games are good when you want low-pressure goals and visible rewards."),
        ],
        "faq": [
            ("What are idle and clicker games?", "They use repeated taps, upgrades, and automatic progress loops."),
            ("Can I play clicker games quickly?", "Yes. They are built for short checks and easy restarts."),
        ],
    },
    "Dress Up": {
        "title": "Free dress up games",
        "intro": "Dress up games focus on outfits, styling, characters, colors, and playful fashion choices.",
        "sections": [
            ("Style characters", "Choose clothes, looks, themes, and accessories in simple browser games."),
            ("More creative play", "Try Beauty for salon and makeup games or Casual for lighter quick games."),
        ],
        "faq": [
            ("What are dress up games?", "Dress up games let players style characters with outfits, colors, and accessories."),
            ("Are dress up games free?", "Yes. Dress up games here are free browser games."),
        ],
    },
    "Beauty": {
        "title": "Free beauty games",
        "intro": "Beauty games cover makeup, salons, nails, spa routines, makeovers, and creative styling.",
        "sections": [
            ("Salon routines", "Try makeup, nails, hair, skin care, and makeover challenges."),
            ("Related creative games", "Dress Up and Cooking are nearby casual categories with clear routines."),
        ],
        "faq": [
            ("What are beauty games?", "Beauty games focus on makeup, salons, nails, makeovers, and styling routines."),
            ("Can beauty games be played online?", "Yes. They run directly in the browser."),
        ],
    },
    "Two Player": {
        "title": "Free two player games",
        "intro": "Two player games are made for shared play, local duels, quick matches, and competitive rounds with simple controls.",
        "sections": [
            ("Play together", "Look for duels, random sports, fighting, racing, and party games."),
            ("More competition", "Multiplayer and io Games offer nearby online-style competition."),
        ],
        "faq": [
            ("What are two player games?", "Two player games are designed for two people to play or compete in the same game."),
            ("Are two player games free?", "Yes. The two player games here are free browser games."),
        ],
    },
    "Multiplayer": {
        "title": "Free multiplayer games",
        "intro": "Multiplayer games focus on shared competition, online arenas, co-op moments, and fast browser rounds.",
        "sections": [
            ("Shared competition", "Compete, cooperate, survive, or score against other players."),
            ("Nearby categories", "io Games, Shooter, and Two Player all overlap with multiplayer play."),
        ],
        "faq": [
            ("What are multiplayer games?", "Multiplayer games are built around playing with or against other players."),
            ("Do multiplayer games need downloads?", "No. The games listed here open from the browser."),
        ],
    },
    "Tower Defense": {
        "title": "Free tower defense games",
        "intro": "Tower defense games ask you to place, upgrade, and plan defenses against waves of enemies or hazards.",
        "sections": [
            ("Plan your defense", "Choose where to build, when to upgrade, and how to stop each wave."),
            ("More planning games", "Try Strategy for broader planning or Action for faster pressure."),
        ],
        "faq": [
            ("What are tower defense games?", "Tower defense games involve building defenses and stopping waves of enemies."),
            ("Are tower defense games strategy games?", "Yes. They are a focused type of strategy game."),
        ],
    },
})

def clean_text(value):
    """Clean known mojibake patterns while preserving normal game names."""
    if value is None:
        return value
    text = str(value)
    for bad, good in MOJIBAKE_REPLACEMENTS.items():
        text = text.replace(bad, good)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def clean_value(value):
    """Recursively clean strings inside common JSON-like values."""
    if isinstance(value, str):
        return clean_text(value)
    if isinstance(value, list):
        return [clean_value(item) for item in value]
    if isinstance(value, dict):
        return {clean_text(key): clean_value(item) for key, item in value.items()}
    return value

def slugify(value):
    text = clean_text(value or "")
    text = text.lower().replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "games"

def normalize_slug(value):
    return slugify(value)

def category_text(game_data):
    values = [
        game_data.get('slug'),
        game_data.get('title'),
        game_data.get('description'),
        game_data.get('source_page_title'),
    ]
    values.extend(game_data.get('tags') or [])
    return clean_text(" ".join(str(value) for value in values if value)).lower()

def has_any(text, keywords):
    return any(keyword in text for keyword in keywords)

def has_word(text, words):
    return any(re.search(rf"(^|[^a-z0-9]){re.escape(word)}([^a-z0-9]|$)", text) for word in words)

def classify_game_category(game_data):
    """Choose one primary category from title, slug, tags, and description."""
    text = category_text(game_data)
    slug = normalize_slug(game_data.get('slug') or game_data.get('id') or game_data.get('title'))
    title = clean_text(game_data.get('title') or '').lower()

    # Strong series and brand rules first.
    if has_any(text, ["papa's", "papas-", "pizzeria", "burgeria", "freezeria", "donuteria", "cupcakeria", "sushiria", "bakeria", "wingeria", "taco mia"]):
        return "Cooking"
    if has_any(text, ["five nights", "fnaf", "freddy", "granny", "backrooms", "poppy", "haunted", "horror", "scary", "nightmare", "dreader"]):
        return "Horror"
    if has_any(text, ["fireboy", "watergirl", "vex-", "vex ", "fancy pants", "electric man"]):
        return "Platformer"
    if has_any(text, ["flappy bird", "pacman", "pac-man"]):
        return "Arcade"

    # Precise subcategories before broad genres.
    if has_any(text, ["tower defense", "tower defence", "bloons", "defense war", "defence war", "backpack block td"]):
        return "Tower Defense"
    if has_any(text, ["sniper", "marksman", "sharpshooter", "sharp shooter"]):
        return "Sniper"
    if has_any(text, ["parking", "park me", "car out"]) and not has_any(text, ["parkour", "park "]):
        return "Parking"
    if has_any(text, ["mahjong", "solitaire", "freecell", "blackjack", "yatzy", "ludo", "chess", "card", "cards", "billiards", "pool elite"]):
        return "Mahjong & Card"
    if has_word(text, ["word", "words", "trivia", "quiz", "guess", "scramble", "knowledge", "crossword"]):
        return "Word & Trivia"
    if has_any(text, ["idle", "clicker", "tycoon", "incremental", "tap tap", "spacebar clicker"]):
        return "Idle & Clicker"
    if has_any(text, ["makeup", "beauty", "salon", "nail", "spa", "makeover", "skincare", "cosmetics", "barber"]):
        return "Beauty"
    if has_any(text, ["dress up", "dress-up", "fashion", "outfit", "wardrobe", "princess dress", "dollhouse", "avatar maker"]):
        return "Dress Up"
    if has_any(text, ["2 player", "two player", "two-player", "duel", "random", "with friends", "party game", "local multiplayer"]):
        return "Two Player"
    if has_any(text, ["obby", "obstacle course"]):
        return "Obby"
    if has_any(text, ["parkour", "only up", "platform parkour"]):
        return "Parkour"
    if has_any(text, ["runner", "subway", "tomb runner", "run 3", "run-3", "run away", "endless run", "running game", "snow rider", "slope run", "slope-"]):
        return "Runner"
    if has_any(text, ["platformer", "platform game", "jumping platform", "geometry dash", "geometry jump", "geometry arrow", "red ball", "jump jump"]):
        return "Platformer"
    if has_any(text, ["restaurant", "cooking", "cook ", "kitchen", "pizza", "burger", "food festival", "donut", "ice cream", "bbq"]):
        return "Cooking"
    if has_any(text, ["management", "manage", "supermarket", "hotel", "hospital", "shop", "mall", "business", "farm", "organizer", "organize", "storage", "cash tycoon"]):
        return "Management"
    if has_any(text, ["survival", "survive", "survivor", "raft", "doomsday", "apocalypse"]):
        return "Survival"

    # Vehicle categories.
    if has_any(text, ["drift", "racing", "race ", "race-", "grand prix", "rally", "speed racing"]):
        return "Racing"
    if has_word(text, ["car", "cars", "truck", "bus", "taxi", "bike", "motor", "moto", "vehicle", "driving", "drive", "driver", "traffic", "highway", "boat"]) or has_any(slug, ["train-simulator", "airplane", "plane-", "-plane"]):
        return "Driving"

    # Sports subcategories.
    if has_any(text, ["soccer", "football", "penalty", "head soccer"]):
        return "Soccer"
    if has_any(text, ["basketball", "basket ", "hoop", "dunk"]):
        return "Basketball"
    if has_any(text, ["golf", "tennis", "rugby", "ski ", "ski-", "sport", "sports", "bowling", "ping pong", "tabletennis"]):
        return "Sports"

    # Combat and competitive categories.
    if has_any(text, ["shoot", "shooter", "gun", "fps", "tank", "bullet", "weapon", "aim", "archery", "archer"]):
        return "Shooter"
    if ".io" in title or slug.endswith("-io") or has_any(text, [" io game", "io games", "arena io", "multiplayer arena"]):
        return "io Games"
    if has_any(text, ["multiplayer", "online battle", "pvp", "co-op", "co op"]):
        return "Multiplayer"
    if has_any(text, ["strategy", "battle simulator", "war ", "wars", "kingdom", "empire", "legion", "chess classic"]):
        return "Strategy"
    if has_any(text, ["action", "fight", "fighter", "combat", "battle", "warrior", "ninja", "hero", "monster", "zombie", "attack", "assault"]):
        return "Action"

    # Puzzle families after more specific cards/word/match cases.
    if has_any(text, ["match", "merge", "bubble", "tile", "jewel", "candy", "fruit", "sort", "connect", "link", "2048", "water sort", "block puzzle", "tetris", "blast", "pop stone"]):
        return "Match & Merge"
    if has_any(text, ["puzzle", "logic", "brain", "solve", "hidden", "find", "draw", "pin ", "screw", "rope", "line", "maze", "sudoku"]):
        return "Puzzle"
    if has_any(text, ["simulation", "simulator", "sim ", "life", "doctor", "pet", "animal", "craft", "building", "world"]):
        return "Simulation"
    if has_any(text, ["arcade", "classic", "retro", "pixel", "snake", "pac-man", "flappy"]):
        return "Arcade"

    current = clean_text(game_data.get('category_name') or game_data.get('category') or '')
    if current in CATEGORY_ORDER:
        return current
    return "Casual"

def apply_primary_category_fallbacks(games):
    counts = {}
    for game in games:
        category = game.get('category_name')
        if category:
            counts[category] = counts.get(category, 0) + 1
    for game in games:
        category = game.get('category_name')
        fallback = THIN_CATEGORY_FALLBACKS.get(category)
        if fallback and counts.get(category, 0) < MIN_PRIMARY_CATEGORY_GAMES:
            game['thin_category_name'] = category
            game['category_name'] = fallback
    return games

def normalize_game_data(game_data):
    cleaned = clean_value(game_data.copy())
    original_slug = cleaned.get('slug') or cleaned.get('id') or cleaned.get('title')
    cleaned['original_slug'] = clean_text(original_slug)
    cleaned['slug'] = normalize_slug(original_slug)
    if cleaned.get('title'):
        cleaned['title'] = clean_text(cleaned['title']).replace('JailBreak', 'Jailbreak')
    if not cleaned.get('category_name') and cleaned.get('category'):
        cleaned['category_name'] = cleaned.get('category')
    previous_category = clean_text(cleaned.get('category_name') or 'Casual')
    cleaned['previous_category_name'] = previous_category
    cleaned['category_name'] = classify_game_category(cleaned)
    return cleaned

def truncate(text, length=160):
    text = clean_text(text or "")
    if len(text) <= length:
        return text
    return text[:length - 3].rstrip() + "..."

def site_absolute_url(url):
    url = clean_text(url or "")
    if not url:
        return SITE_IMAGE
    if url.startswith("http://") or url.startswith("https://"):
        return url
    if url.startswith("/"):
        return f"{SITE_URL}{url}"
    return f"{SITE_URL}/{url.lstrip('/')}"

def category_slug(category):
    return slugify(category)

def category_url(category):
    return f"/categories/{category_slug(category)}"

def category_full_url(category):
    return f"{SITE_URL}{category_url(category)}"

def game_url(slug):
    return f"/games/{normalize_slug(slug)}"

def game_full_url(slug):
    return f"{SITE_URL}{game_url(slug)}"

def thumbnail_cache_filename(url, slug):
    parsed = urlparse(url)
    source_key = f"{THUMBNAIL_VERSION}:{parsed.netloc}{parsed.path}?{parsed.query}"
    digest = hashlib.sha1(source_key.encode("utf-8")).hexdigest()[:12]
    safe_slug = normalize_slug(slug or digest)[:80] or "game"
    return f"{safe_slug}-{digest}.webp"

def cover_resize(image, image_module, width, height):
    source_width, source_height = image.size
    target_ratio = width / height
    source_ratio = source_width / source_height

    if source_ratio > target_ratio:
        crop_width = int(source_height * target_ratio)
        left = (source_width - crop_width) // 2
        box = (left, 0, left + crop_width, source_height)
    else:
        crop_height = int(source_width / target_ratio)
        top = (source_height - crop_height) // 2
        box = (0, top, source_width, top + crop_height)

    return image.crop(box).resize((width, height), image_module.Resampling.LANCZOS)

def cache_remote_thumbnail(url, slug, session, image_module):
    url = clean_text(url)
    if not url or url.startswith("/"):
        return url
    if not (url.startswith("http://") or url.startswith("https://")):
        return url

    os.makedirs(THUMBNAIL_CACHE_DIR, exist_ok=True)
    filename = thumbnail_cache_filename(url, slug)
    output_path = os.path.join(THUMBNAIL_CACHE_DIR, filename)
    public_path = f"/assets/thumbnails/{filename}"
    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        return public_path

    try:
        response = session.get(url, timeout=THUMBNAIL_TIMEOUT, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        image = image_module.open(BytesIO(response.content)).convert("RGB")
        cover_resize(image, image_module, THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT).save(
            output_path,
            "WEBP",
            quality=THUMBNAIL_QUALITY,
            method=6
        )
        return public_path
    except Exception:
        return url

def cache_game_thumbnails(games):
    try:
        from PIL import Image
    except ImportError:
        print("⚠️  Pillow is not installed; skipping local thumbnail cache. Run `python3 -m pip install -r requirements.txt`.")
        return games

    candidates = []
    for index, game in enumerate(games):
        source_url = clean_text(game.get("thumbnail_url") or game.get("thumbnail") or "")
        if source_url:
            candidates.append((index, game, source_url))

    cached = 0
    remote = len(games) - len(candidates)

    def cache_one(item):
        index, game, source_url = item
        session = requests.Session()
        game.setdefault("original_thumbnail_url", source_url)
        local_url = cache_remote_thumbnail(source_url, game.get("slug"), session, Image)
        return index, source_url, local_url

    total = len(candidates)
    print(f"🖼️  Preparing thumbnail cache for {total} images...")
    with ThreadPoolExecutor(max_workers=THUMBNAIL_WORKERS) as executor:
        futures = [executor.submit(cache_one, item) for item in candidates]
        for processed, future in enumerate(as_completed(futures), 1):
            index, source_url, local_url = future.result()
            if local_url != source_url:
                cached += 1
                games[index]["thumbnail_url"] = local_url
                games[index]["thumbnail"] = local_url
            else:
                remote += 1
            if processed % 100 == 0 or processed == total:
                print(f"🖼️  Thumbnail cache progress: {processed}/{total}")
    print(f"🖼️  Thumbnail cache ready: {cached} local, {remote} remote/empty")
    return games

def get_fallback_label(title):
    words = [word for word in re.split(r"\s+", clean_text(title or "")) if word]
    return ''.join(word[0] for word in words[:2]).upper() or 'PLAY'

def matches_category(game, category):
    if category == "all":
        return True
    labels = [game.get('category_name'), game.get('category')]
    labels.extend(game.get('standardized_tags') or [])
    labels.extend(game.get('tags') or [])
    normalized = {clean_text(label).lower() for label in labels if label}
    return clean_text(category).lower() in normalized

def get_all_categories(games):
    primary_counts = {}
    for game in games:
        category = game.get('category_name')
        if category:
            primary_counts[category] = primary_counts.get(category, 0) + 1
    found = []
    for category in CATEGORY_ORDER:
        if primary_counts.get(category, 0) < MIN_PRIMARY_CATEGORY_GAMES:
            continue
        if any(matches_category(game, category) for game in games):
            found.append(category)
    primary = sorted({game.get('category_name') for game in games if game.get('category_name')})
    for category in primary:
        if primary_counts.get(category, 0) >= MIN_PRIMARY_CATEGORY_GAMES and category not in found:
            found.append(category)
    return found

def category_guide(category):
    if category in CATEGORY_GUIDES:
        return CATEGORY_GUIDES[category]
    title = clean_text(category or "Games")
    return {
        "title": f"Free {title.lower()} games",
        "intro": f"Browse free {title.lower()} games on BTW game. Pick a browser game, open the page, and start playing without downloads.",
        "sections": [
            (f"Play {title.lower()} games online", f"This category collects quick {title.lower()} games for casual browser play."),
            ("Find your next game", "Use the game cards below to compare titles, categories, ratings, and quick-play options."),
        ],
        "faq": [
            (f"Are {title.lower()} games free?", f"Yes. The {title.lower()} games listed here can be played free in the browser."),
            ("Do I need to download anything?", "No. Open a game page and play directly in your browser."),
        ],
    }

def fetch_game_data_from_db(slug):
    """Fetch game data directly from database"""
    try:
        from app import create_app, db
        from models import Game, game_schema

        app = create_app()
        with app.app_context():
            game = Game.query.filter_by(slug=slug, is_active=True).first()
            if game:
                return game_schema.dump(game)
            return None
    except Exception as e:
        print(f"❌ Database error for {slug}: {e}")
        return None

def fetch_game_data(slug):
    """Fetch game data from database first, fallback to API"""
    # Try database first
    game_data = fetch_game_data_from_db(slug)
    if game_data:
        return game_data

    # Fallback to API if database fails
    try:
        response = requests.get(f"{BASE_URL}/api/games/slug/{slug}")
        if response.status_code == 200:
            return response.json()['game']
        else:
            print(f"Error fetching {slug}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching {slug}: {e}")
        return None

def fetch_related_games_from_db(category_name, exclude_slug, limit=6):
    """Fetch related games from database"""
    try:
        from app import create_app, db
        from models import Game, Category, games_schema

        app = create_app()
        with app.app_context():
            # Find category
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                return []

            # Get related games
            games = Game.query.filter(
                Game.category_id == category.id,
                Game.slug != exclude_slug,
                Game.is_active == True
            ).order_by(Game.total_plays.desc()).limit(limit).all()

            return games_schema.dump(games)
    except Exception as e:
        print(f"❌ Database error fetching related games: {e}")
        return []

def fetch_related_games(category_name, exclude_slug, limit=6):
    """Fetch related games from database first, fallback to API"""
    # Try database first
    related = fetch_related_games_from_db(category_name, exclude_slug, limit)
    if related:
        return related

    # Fallback to API
    try:
        response = requests.get(f"{BASE_URL}/api/games", params={
            'category': category_name,
            'per_page': limit + 1  # Get one extra to exclude current game
        })
        if response.status_code == 200:
            games = response.json()['games']
            # Exclude current game and limit results
            related = [g for g in games if g['slug'] != exclude_slug][:limit]
            return related
        else:
            return []
    except Exception as e:
        print(f"Error fetching related games: {e}")
        return []

def standardize_game_tags(game_data):
    """Generate standardized tags based on game data"""
    title = clean_text(game_data.get('title', '')).lower()
    description = clean_text(game_data.get('description', '')).lower()
    category_name = clean_text(game_data.get('category_name', '')).lower()
    iframe_url = game_data.get('iframe_url', '') or game_data.get('game_url', '')

    tags = []

    # Platform tags based on iframe URL
    if 'gamedistribution.com' in iframe_url or 'html5' in iframe_url.lower():
        tags.append('HTML5')
    elif 'unity' in iframe_url.lower():
        tags.append('Unity')
    elif iframe_url and 'html5' not in iframe_url.lower() and 'unity' not in iframe_url.lower():
        tags.append('HTML5')  # Default for browser games

    # Genre tags based on title, description, and category
    genre_keywords = {
        'Action': ['action', 'fight', 'combat', 'battle', 'war', 'shoot', 'gun', 'zombie', 'adventure'],
        'Strategy': ['strategy', 'tower defense', 'defense', 'build', 'manage', 'city', 'empire'],
        'Puzzle': ['puzzle', 'brain', 'logic', 'solve', 'match', 'tetris', 'block'],
        'Match & Merge': ['match', 'merge', 'bubble', 'tile', 'jewel', 'candy', 'fruit', 'sort', 'connect', '2048'],
        'Mahjong & Card': ['mahjong', 'solitaire', 'card', 'cards', 'chess', 'blackjack', 'yatzy', 'ludo'],
        'Word & Trivia': ['word', 'trivia', 'quiz', 'guess', 'crossword', 'scramble'],
        'Racing': ['race', 'racing', 'car', 'drive', 'speed', 'drift', 'bike', 'motorcycle'],
        'Driving': ['car', 'truck', 'bus', 'taxi', 'vehicle', 'traffic', 'highway', 'driving'],
        'Parking': ['parking', 'park me'],
        'Sports': ['sport', 'football', 'soccer', 'basketball', 'tennis', 'golf', 'baseball'],
        'Soccer': ['soccer', 'football', 'penalty'],
        'Basketball': ['basketball', 'basket', 'hoop', 'dunk'],
        'Arcade': ['arcade', 'classic', 'retro', 'pixel', 'old school'],
        'Platformer': ['platform', 'platformer', 'jump'],
        'Parkour': ['parkour', 'only up'],
        'Obby': ['obby', 'obstacle course'],
        'Runner': ['runner', 'endless run', 'subway', 'run', 'dodge'],
        'Simulation': ['simulation', 'sim', 'life', 'city', 'farm', 'cooking', 'restaurant'],
        'Management': ['manage', 'management', 'business', 'shop', 'hotel', 'supermarket', 'organize'],
        'RPG': ['rpg', 'role', 'character', 'level up', 'quest', 'adventure'],
        'Casual': ['casual', 'relaxing', 'simple', 'easy', 'family'],
        'Multiplayer': ['multiplayer', 'online', 'vs', 'versus', 'pvp', 'co-op'],
        'Two Player': ['2 player', 'two player', 'duel', 'with friends'],
        'Idle & Clicker': ['clicker', 'click', 'idle', 'incremental', 'tap'],
        'Cooking': ['cooking', 'cook', 'restaurant', 'pizza', 'burger', 'kitchen'],
        'Dress Up': ['dress up', 'fashion', 'outfit', 'wardrobe', 'doll'],
        'Beauty': ['makeup', 'beauty', 'salon', 'nail', 'spa', 'makeover'],
        'Educational': ['educational', 'learn', 'math', 'quiz', 'knowledge'],
        'Horror': ['horror', 'scary', 'fear', 'nightmare', 'ghost', 'monster'],
        'Survival': ['survival', 'survive', 'survivor', 'raft', 'apocalypse'],
        'Shooter': ['shooter', 'shoot', 'gun', 'fps', 'tank', 'bullet', 'weapon'],
        'Sniper': ['sniper', 'marksman'],
        'Tower Defense': ['tower defense', 'defense', 'defence'],
        'Rhythm': ['rhythm', 'music', 'beat', 'dance', 'sound'],
        'Card': ['card', 'poker', 'blackjack', 'solitaire', 'deck']
    }

    content_text = f"{title} {description} {category_name}"

    for genre, keywords in genre_keywords.items():
        if any(keyword in content_text for keyword in keywords):
            tags.append(genre)

    # Special game type tags
    if any(word in content_text for word in ['io', '.io']):
        tags.append('IO Game')

    if any(word in content_text for word in ['3d', 'three dimensional']):
        tags.append('3D')

    if any(word in content_text for word in ['2d', 'two dimensional', 'pixel']):
        tags.append('2D')

    # Remove duplicates and ensure we have at least some basic tags
    tags = list(dict.fromkeys(tags))  # Remove duplicates while preserving order

    # Ensure every game has at least HTML5 and one genre tag
    if not any(tag in ['HTML5', 'Unity'] for tag in tags):
        tags.insert(0, 'HTML5')

    if category_name:
        canonical_category = next((category for category in CATEGORY_ORDER if category.lower() == category_name), None)
        if canonical_category:
            tags.append(canonical_category)

    tags = list(dict.fromkeys(tags))

    if not any(tag in genre_keywords.keys() for tag in tags):
        if 'game' in content_text:
            tags.append('Casual')
        else:
            tags.append('Action')

    return tags[:8]  # Limit to 8 tags maximum

def render_game_card(game, priority=False, extra_class="", show_badge=True):
    title = clean_text(game.get('title') or 'Untitled game')
    slug = normalize_slug(game.get('slug') or game.get('id') or title)
    thumbnail = clean_text(game.get('thumbnail_url') or game.get('thumbnail') or '')
    badge = ''
    if show_badge and (game.get('is_new') or game.get('isNew')):
        badge = '<div class="game-badge">NEW</div>'
    elif show_badge and (game.get('is_featured') or game.get('isFeatured')):
        badge = '<div class="game-badge featured">FEATURED</div>'
    image_html = ''
    if thumbnail:
        image_html = f'<img src="{html_escape(thumbnail, quote=True)}" alt="{html_escape(title, quote=True)}" width="{THUMBNAIL_WIDTH}" height="{THUMBNAIL_HEIGHT}" loading="{"eager" if priority else "lazy"}" decoding="async" onerror="this.style.display=\'none\'; this.nextElementSibling.style.display=\'grid\';">'
    return f'''
        <a class="game-card {html_escape(extra_class)}" href="{game_url(slug)}">
            <div class="game-thumbnail">
                {badge}
                {image_html}
                <div class="thumbnail-fallback" style="{'display:none;' if thumbnail else ''}">{html_escape(get_fallback_label(title))}</div>
                <div class="game-info">
                    <h3 class="game-title">{html_escape(title)}</h3>
                </div>
            </div>
        </a>
    '''

def render_catalog_links(games):
    links = []
    for game in games:
        title = clean_text(game.get('title') or 'Untitled game')
        slug = normalize_slug(game.get('slug') or game.get('id') or title)
        category = clean_text(game.get('category_name') or game.get('category') or 'Games')
        links.append(f'<li><a href="{game_url(slug)}">{html_escape(title)}</a><span>{html_escape(category)}</span></li>')
    return "\n".join(links)

def category_icon(category):
    return {
        "Action": "✹",
        "Adventure": "♣",
        "Arcade": "◆",
        "Puzzle": "✚",
        "Match & Merge": "◈",
        "Mahjong & Card": "▣",
        "Word & Trivia": "?",
        "Racing": "⚑",
        "Driving": "◇",
        "Sports": "●",
        "Soccer": "◒",
        "Basketball": "○",
        "Shooter": "◎",
        "Sniper": "⌖",
        "Horror": "◐",
        "Survival": "▲",
        "Parkour": "↗",
        "Obby": "▵",
        "Platformer": "▴",
        "Runner": "▶",
        "Simulation": "▤",
        "Management": "▦",
        "Idle & Clicker": "✦",
        "Cooking": "◍",
        "Dress Up": "✧",
        "Beauty": "✺",
        "Two Player": "Ⅱ",
        "Multiplayer": "◌",
        "io Games": "io",
        "Strategy": "♟",
        "Tower Defense": "▰",
        "Casual": "☼",
    }.get(category, "●")

def render_rail_links(active_category=None, categories=None):
    categories = categories or RAIL_CATEGORIES
    links = []
    for category in categories:
        active = ' aria-current="page"' if active_category == category else ''
        icon = category_icon(category)
        links.append(f'<li><a href="{category_url(category)}"{active}><span class="rail-icon">{icon}</span>{html_escape(category)}</a></li>')
    return "\n".join(links)

def build_game_faq(title, category_name, controls):
    control_text = ", ".join(f"{clean_text(k)} for {clean_text(v)}" for k, v in (controls or {}).items())
    questions = [
        (
            f"Can I play {title} for free?",
            f"Yes. {title} is available as a free browser game on BTW game."
        ),
        (
            f"What kind of game is {title}?",
            f"{title} is listed in the {category_name} category and is designed for quick online play."
        ),
        (
            f"Do I need to download {title}?",
            f"No. Open the {title} game page and play in your browser without installing a separate app."
        ),
    ]
    if control_text:
        questions.insert(1, (f"How do I control {title}?", f"Use {control_text}. Controls can vary by device, so check the in-game prompts too."))
    return questions

def render_faq_html(faq_items):
    items = []
    for question, answer in faq_items:
        items.append(f'''
            <details class="faq-item">
                <summary>{html_escape(question)}</summary>
                <p>{html_escape(answer)}</p>
            </details>
        ''')
    return "\n".join(items)

def build_game_content(title, description, long_description, category_name, tags, controls):
    base_description = clean_text(long_description or description)
    if len(base_description) < 140:
        tag_text = ", ".join(tags[:3]) if tags else category_name
        base_description = (
            f"{base_description} {title} is a free {category_name.lower()} browser game on BTW game. "
            f"It is a good fit for quick breaks, casual play, and players who want to try {tag_text.lower()} games without downloads."
        ).strip()
    how_to = (
        f"Press Play, wait for the browser game to load, then follow the on-screen prompts. "
        f"Focus on the main objective, learn each restart, and use the related games list when you want another {category_name.lower()} game."
    )
    controls_text = ""
    if controls:
        controls_text = " ".join(f"{clean_text(key)}: {clean_text(value)}." for key, value in controls.items())
    else:
        controls_text = "Use the keyboard, mouse, touch controls, or the in-game prompts shown after the game loads."
    tips = [
        "Start with a short round to learn the pace before chasing a high score.",
        "Use fullscreen or a wider browser window when the game needs precise movement.",
        f"Try related {category_name.lower()} games if you want a similar feel with a different challenge.",
    ]
    return base_description, how_to, controls_text, tips

def build_game_jsonld(game, tags, faq_items):
    title = clean_text(game.get('title'))
    slug = normalize_slug(game.get('slug'))
    description = truncate(game.get('description') or f"Play {title} online for free at BTW game.", 220)
    image = site_absolute_url(game.get('thumbnail_url') or '')
    category_name = clean_text(game.get('category_name') or 'Games')
    scripts = [
        {
            "@context": "https://schema.org",
            "@type": "Game",
            "name": title,
            "description": description,
            "url": game_full_url(slug),
            "image": image,
            "about": f"{title} is a free browser game in the {category_name} category on BTW game.",
            "genre": category_name,
            "keywords": tags,
            "gamePlatform": "Web Browser",
            "operatingSystem": "Any",
            "applicationCategory": "Game",
            "isAccessibleForFree": True,
            "inLanguage": "en",
            "audience": {
                "@type": "Audience",
                "audienceType": "Casual players"
            },
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD",
                "availability": "https://schema.org/InStock"
            },
            "publisher": {
                "@id": f"{SITE_URL}/#organization"
            }
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": "Games", "item": f"{SITE_URL}/games"},
                {"@type": "ListItem", "position": 3, "name": category_name, "item": category_full_url(category_name)},
                {"@type": "ListItem", "position": 4, "name": title, "item": game_full_url(slug)}
            ]
        },
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": question,
                    "acceptedAnswer": {"@type": "Answer", "text": answer}
                }
                for question, answer in faq_items
            ]
        }
    ]
    return "\n".join(
        f'<script type="application/ld+json">{json.dumps(script, ensure_ascii=False)}</script>'
        for script in scripts
    )

def render_brand_mark():
    return '''
            <a href="/" class="brand-mark" aria-label="BTW game home">
                <span class="brand-icon" aria-hidden="true">
                    <svg class="brand-gamepad" viewBox="0 0 32 24" role="img" focusable="false">
                        <path d="M9.2 6.2h13.6c3.1 0 5.7 2.1 6.5 5.1l1 3.8c.7 2.7-1.3 5.3-4.1 5.3-1.3 0-2.5-.6-3.3-1.6l-1.7-2.2H10.3l-1.7 2.2c-.8 1-2 1.6-3.3 1.6-2.8 0-4.8-2.6-4.1-5.3l1-3.8c.8-3 3.9-5.1 7-5.1Z" fill="currentColor"/>
                        <path d="M8.7 10.2v5.2M6.1 12.8h5.2M22.8 11.1h.1M26 14.4h.1" stroke="white" stroke-width="2.1" stroke-linecap="round"/>
                    </svg>
                </span>
                <span class="brand-word">BTW game <span class="brand-tagline">By the way, play!</span></span>
            </a>
    '''

def render_header(active=""):
    return f'''
    <header class="site-header">
        <nav class="site-nav container" aria-label="Primary navigation">
            {render_brand_mark()}
            <div class="nav-search" role="search">
                <form onsubmit="event.preventDefault(); navSearchGames();">
                    <input type="search" class="search-bar" placeholder="Search games..." id="navSearchInput" autocomplete="off">
                    <button class="search-btn compact" type="submit">Search</button>
                </form>
            </div>
            <button class="mobile-menu" type="button" onclick="toggleMenu()" aria-label="Open navigation" aria-controls="navLinks">
                <span></span><span></span><span></span>
            </button>
            <ul class="nav-links" id="navLinks">
                <li><a href="/"{' aria-current="page"' if active == 'home' else ''}>Home</a></li>
                <li><a href="/games"{' aria-current="page"' if active == 'games' else ''}>All games</a></li>
                <li><a href="/games?filter=new">New</a></li>
                <li><a href="/games?filter=featured">Featured</a></li>
            </ul>
        </nav>
    </header>
    '''

def render_footer():
    return '''
    <footer class="site-footer">
        <div class="footer-content container">
            <p>&copy; 2026 BTW game. All rights reserved.</p>
            <ul class="footer-links">
                <li><a href="/">Home</a></li>
                <li><a href="/games">All games</a></li>
                <li><a href="/best/free-online-games">Best games</a></li>
                <li><a href="/about">About</a></li>
                <li><a href="/editorial-policy">Editorial policy</a></li>
                <li><a href="/games?filter=new">New games</a></li>
                <li><a href="/games?filter=featured">Featured</a></li>
            </ul>
        </div>
    </footer>
    '''

def render_nav_script():
    return '''
    <script>
        function toggleMenu() {
            document.getElementById('navLinks').classList.toggle('active');
        }
        function navSearchGames() {
            const query = document.getElementById('navSearchInput').value.trim();
            window.location.href = query ? `/games?search=${encodeURIComponent(query)}` : '/games';
        }
    </script>
    '''

def render_head(title, description, canonical_path, og_image=SITE_IMAGE, extra_jsonld=None):
    canonical = f"{SITE_URL}{canonical_path}"
    image = og_image or SITE_IMAGE
    jsonld = extra_jsonld or ""
    return f'''<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{html_escape(truncate(description, 160), quote=True)}">
    <meta name="keywords" content="free online games, browser games, BTW game, no download games, instant play games">
    <meta name="author" content="BTW game">
    <meta property="og:title" content="{html_escape(title, quote=True)}">
    <meta property="og:description" content="{html_escape(truncate(description, 180), quote=True)}">
    <meta property="og:image" content="{html_escape(image, quote=True)}">
    <meta property="og:url" content="{html_escape(canonical, quote=True)}">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{html_escape(title, quote=True)}">
    <meta name="twitter:description" content="{html_escape(truncate(description, 180), quote=True)}">
    <meta name="twitter:image" content="{html_escape(image, quote=True)}">
    <link rel="canonical" href="{html_escape(canonical, quote=True)}">
    <link rel="stylesheet" href="/assets/css/site.css">
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-SM7PBYVK97"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag() {{ dataLayer.push(arguments); }}
        gtag('js', new Date());
        gtag('config', 'G-SM7PBYVK97');
    </script>
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8930741225505243" crossorigin="anonymous"></script>
    {jsonld}
    <title>{html_escape(title)}</title>
</head>'''

def jsonld_script(data):
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'

def site_entity_jsonld():
    website_jsonld = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": SITE_NAME,
        "alternateName": ["BTW game", "btw game", "By the way, play!"],
        "url": f"{SITE_URL}/",
        "description": "BTW game is a free browser game catalog for quick, casual play.",
        "publisher": {"@id": f"{SITE_URL}/#organization"},
        "potentialAction": {
            "@type": "SearchAction",
            "target": f"{SITE_URL}/games?search={{search_term_string}}",
            "query-input": "required name=search_term_string"
        }
    }
    organization_jsonld = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "@id": f"{SITE_URL}/#organization",
        "name": SITE_NAME,
        "alternateName": ["BTW game", "btw game"],
        "slogan": "By the way, play!",
        "url": SITE_URL,
        "logo": SITE_IMAGE,
        "description": "BTW game helps casual players find fast, free browser games for short breaks."
    }
    return jsonld_script(website_jsonld) + "\n" + jsonld_script(organization_jsonld)

def render_home_grid_balance_script():
    return '''
    <script>
        function balanceHomeGameRows() {
            document.querySelectorAll('.home-main .home-games-grid').forEach(grid => {
                const cards = Array.from(grid.querySelectorAll('.game-card'));
                cards.forEach(card => card.classList.remove('is-row-trimmed'));

                const columns = getComputedStyle(grid).gridTemplateColumns.split(' ').filter(Boolean).length;
                if (!columns || columns < 2 || cards.length <= columns) return;
                const minimumRows = grid.classList.contains('category-home-grid') ? 2 : 1;
                const minimumCells = columns * minimumRows;

                let usedCells = 0;
                cards.forEach(card => {
                    const style = getComputedStyle(card);
                    const columnSpan = style.gridColumnEnd && style.gridColumnEnd.startsWith('span')
                        ? Number(style.gridColumnEnd.replace('span', '').trim()) || 1
                        : 1;
                    const rowSpan = style.gridRowEnd && style.gridRowEnd.startsWith('span')
                        ? Number(style.gridRowEnd.replace('span', '').trim()) || 1
                        : 1;
                    usedCells += columnSpan * rowSpan;
                });

                const extraCells = usedCells % columns;
                if (!extraCells) return;
                if (usedCells <= minimumCells || usedCells - extraCells < minimumCells) return;

                let removedCells = 0;
                for (let index = cards.length - 1; index >= 0 && removedCells < extraCells; index -= 1) {
                    const card = cards[index];
                    const style = getComputedStyle(card);
                    const columnSpan = style.gridColumnEnd && style.gridColumnEnd.startsWith('span')
                        ? Number(style.gridColumnEnd.replace('span', '').trim()) || 1
                        : 1;
                    const rowSpan = style.gridRowEnd && style.gridRowEnd.startsWith('span')
                        ? Number(style.gridRowEnd.replace('span', '').trim()) || 1
                        : 1;
                    card.classList.add('is-row-trimmed');
                    removedCells += columnSpan * rowSpan;
                }
            });
        }

        window.addEventListener('load', balanceHomeGameRows);
        window.addEventListener('resize', () => {
            window.clearTimeout(window.__btwBalanceRowsTimer);
            window.__btwBalanceRowsTimer = window.setTimeout(balanceHomeGameRows, 120);
        });
    </script>
    '''

def render_side_rail(active_category=None, categories=None):
    return f'''
        <aside class="side-rail" aria-label="Explore BTW game">
            <section class="rail-panel">
                <h2 class="rail-title">Explore</h2>
                <ul class="rail-links">
                    <li><a href="/"><span class="rail-icon">⌂</span>Home</a></li>
                    <li><a href="/games"><span class="rail-icon">▦</span>All games</a></li>
                    <li><a href="/games?filter=new"><span class="rail-icon">✦</span>New games</a></li>
                    <li><a href="/games?filter=featured"><span class="rail-icon">★</span>Featured</a></li>
                </ul>
            </section>
            <section class="rail-panel">
                <h2 class="rail-title">Categories</h2>
                <ul class="rail-links">
                    {render_rail_links(active_category, categories)}
                </ul>
            </section>
        </aside>
    '''

def collection_jsonld(name, description, url, games, faq_items=None):
    scripts = [
        {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": name,
            "description": description,
            "url": url,
            "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": SITE_URL}
        },
        {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": name,
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": index + 1,
                    "url": game_full_url(normalize_slug(game.get('slug'))),
                    "name": clean_text(game.get('title'))
                }
                for index, game in enumerate(games[:100])
            ]
        }
    ]
    if faq_items:
        scripts.append({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": question,
                    "acceptedAnswer": {"@type": "Answer", "text": answer}
                }
                for question, answer in faq_items
            ]
        })
    return "\n".join(
        f'<script type="application/ld+json">{json.dumps(script, ensure_ascii=False)}</script>'
        for script in scripts
    )

def render_category_guide_html(category, games):
    guide = category_guide(category)
    sections = "\n".join(
        f'<article class="guide-section"><h3>{html_escape(title)}</h3><p>{html_escape(body)}</p></article>'
        for title, body in guide["sections"]
    )
    popular_links = "\n".join(
        f'<a href="{game_url(normalize_slug(game.get("slug")))}">{html_escape(clean_text(game.get("title")))}</a>'
        for game in games[:8]
    )
    related = [item for item in CATEGORY_ORDER if item != category][:6]
    related_links = "\n".join(
        f'<a href="{category_url(item)}">{html_escape(item)}</a>'
        for item in related
    )
    return f'''
        <section class="category-guide" aria-labelledby="categoryGuideTitle">
            <div class="category-guide-header">
                <div>
                    <h2 id="categoryGuideTitle">{html_escape(guide["title"])}</h2>
                    <p>{html_escape(guide["intro"])}</p>
                </div>
                <span class="guide-count">{len(games)} games</span>
            </div>
            <div class="guide-link-block">
                <h3>Popular games</h3>
                <div class="guide-link-list">{popular_links}</div>
            </div>
            <div class="guide-sections">{sections}</div>
            <div class="guide-related" aria-label="Related categories">{related_links}</div>
            <div class="guide-faq">
                <h2>FAQ</h2>
                <div class="faq-list">{render_faq_html(guide["faq"])}</div>
            </div>
        </section>
    '''

def render_home_category_shelf(category, category_games, index):
    if not category_games:
        return ""
    limit = 36
    cards = "\n".join(
        render_game_card(game, priority=index == 0 and card_index < 8, show_badge=False)
        for card_index, game in enumerate(category_games[:limit])
    )
    guide = category_guide(category)
    tone = ["tone-coral", "tone-yellow", "tone-violet", "tone-sky", "tone-green"][index % 5]
    return f'''
                <section class="home-category-shelf {tone}" aria-labelledby="homeCategory{index}">
                    <div class="section-header shelf-header">
                        <div>
                            <h2 class="section-title" id="homeCategory{index}">{html_escape(category)}</h2>
                            <p class="section-note">{html_escape(guide["intro"])}</p>
                        </div>
                        <a href="{category_url(category)}" class="view-all-btn">View {html_escape(category)}</a>
                    </div>
                    <div class="games-grid compact home-games-grid category-home-grid">{cards}</div>
                </section>
    '''

def render_home_geo_section():
    faq_items = [
        ("What is BTW game?", "BTW game is a free browser game catalog for quick breaks. The name means By the way, play!"),
        ("Are games on BTW game free?", "Yes. BTW game focuses on free online games that open in the browser without a download from the site."),
        ("Do I need to install anything?", "No. Open a game page and play directly in the browser when the game is available for your device."),
        ("What games are good for quick breaks?", "Puzzle, casual, racing, runner, and parkour games are good first picks because they start quickly and have short sessions."),
        ("Is BTW game suitable for kids and students?", "BTW game is designed for casual players, kids, and students, but players should follow family or school rules and choose age-appropriate games."),
    ]
    best_links = [
        ("/best/free-online-games", "Best free online games"),
        ("/best/browser-games-for-school", "Browser games for school breaks"),
        ("/best/quick-games", "Quick games"),
        ("/best/mobile-browser-games", "Mobile browser games"),
        ("/best/no-download-games", "No-download games"),
    ]
    return f'''
                <section class="geo-answer-section content-band" aria-labelledby="homeGeoTitle">
                    <div class="category-guide-header">
                        <div>
                            <h2 id="homeGeoTitle">Free browser games for quick breaks</h2>
                            <p>BTW game means By the way, play! It is built for casual players who want fast, playful, and trustworthy browser games without extra setup.</p>
                        </div>
                    </div>
                    <div class="guide-related" aria-label="Best game guides">
                        {"".join(f'<a href="{href}">{html_escape(label)}</a>' for href, label in best_links)}
                    </div>
                    <div class="guide-faq">
                        <h2>FAQ</h2>
                        <div class="faq-list">{render_faq_html(faq_items)}</div>
                    </div>
                </section>
    '''

def generate_index_page(games):
    categories = get_all_categories(games)
    popular = sorted(games, key=lambda game: game.get('total_plays') or 0, reverse=True)
    new_games = sorted(games, key=lambda game: game.get('created_at') or game.get('release_date') or '', reverse=True)
    top_games = popular[:32]
    fresh_games = new_games[:24]
    popular_cards = "\n".join(
        render_game_card(game, priority=index < 14, extra_class='spotlight-card' if index in (0, 7) else '')
        for index, game in enumerate(top_games)
    )
    new_cards = "\n".join(render_game_card(game, priority=False, show_badge=True) for game in fresh_games)
    category_map = {
        category: sorted(
            [game for game in games if matches_category(game, category)],
            key=lambda game: game.get('total_plays') or 0,
            reverse=True
        )
        for category in categories
    }
    priority_categories = [category for category in [
        "Action", "Puzzle", "Match & Merge", "Racing", "Shooter", "Parkour",
        "Runner", "Idle & Clicker", "Beauty", "Cooking", "Sports", "Horror"
    ] if category in category_map]
    remaining_categories = [category for category in categories if category not in priority_categories]
    home_categories = (priority_categories + remaining_categories)[:HOME_CATEGORY_LIMIT]
    category_shelves = "\n".join(
        render_home_category_shelf(category, category_map.get(category, []), index)
        for index, category in enumerate(home_categories)
    )
    home_faq = [
        ("What is BTW game?", "BTW game is a free browser game catalog for quick breaks. The name means By the way, play!"),
        ("Are games on BTW game free?", "Yes. BTW game focuses on free online games that open in the browser without a download from the site."),
        ("Do I need to install anything?", "No. Open a game page and play directly in the browser when the game is available for your device."),
        ("What games are good for quick breaks?", "Puzzle, casual, racing, runner, and parkour games are good first picks because they start quickly and have short sessions."),
        ("Is BTW game suitable for kids and students?", "BTW game is designed for casual players, kids, and students, but players should follow family or school rules and choose age-appropriate games."),
    ]
    faq_jsonld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": question, "acceptedAnswer": {"@type": "Answer", "text": answer}}
            for question, answer in home_faq
        ]
    }
    extra_jsonld = site_entity_jsonld() + "\n" + jsonld_script(faq_jsonld)
    return f'''<!DOCTYPE html>
<html lang="en">
{render_head("BTW game - Free Online Games for Quick Breaks", "Play 1300+ free online games at BTW game. Fast browser games for quick breaks, with action, puzzle, racing, sports, and casual games.", "/", SITE_IMAGE, extra_jsonld)}
<body>
    {render_header("home")}
    <main>
        <div class="home-layout container">
            {render_side_rail(categories=categories)}
            <div class="home-main">
                <section class="content-band game-shelf priority-shelf" aria-labelledby="popular-games-title">
                    <div class="section-header">
                        <div>
                            <h1 class="section-title" id="popular-games-title">Hot games</h1>
                            <p class="section-note">Games players open most often.</p>
                        </div>
                        <a href="/games" class="view-all-btn">View all</a>
                    </div>
                    <div class="games-grid home-games-grid" id="popularGamesGrid">{popular_cards}</div>
                </section>
                <section class="content-band game-shelf" aria-labelledby="new-games-title">
                    <div class="section-header">
                        <div>
                            <h2 class="section-title" id="new-games-title">New games</h2>
                            <p class="section-note">Fresh picks from the current library.</p>
                        </div>
                        <a href="/games?filter=new" class="view-all-btn">View new games</a>
                    </div>
                    <div class="games-grid compact home-games-grid" id="newGamesGrid">{new_cards}</div>
                </section>
                {category_shelves}
                {render_home_geo_section()}
            </div>
        </div>
    </main>
    {render_footer()}
    <script src="/assets/js/api.js"></script>
    {render_nav_script()}
    {render_home_grid_balance_script()}
</body>
</html>'''

def generate_games_page(games):
    categories = get_all_categories(games)
    initial_games = games[:INITIAL_CATALOG_CARD_COUNT]
    game_cards = "\n".join(render_game_card(game, priority=index < 8) for index, game in enumerate(initial_games))
    catalog_links = render_catalog_links(games)
    catalog_data = []
    for game in games:
        title = clean_text(game.get('title') or 'Untitled game')
        slug = normalize_slug(game.get('slug') or game.get('id') or title)
        catalog_data.append({
            "title": title,
            "slug": slug,
            "thumbnail_url": clean_text(game.get('thumbnail_url') or game.get('thumbnail') or ''),
            "category_name": clean_text(game.get('category_name') or game.get('category') or 'Games'),
            "tags": clean_value(game.get('standardized_tags') or game.get('tags') or []),
            "description": truncate(game.get('description') or '', 120),
            "rating": game.get('rating') or 0,
            "total_plays": game.get('total_plays') or game.get('plays') or 0,
            "created_at": clean_text(game.get('created_at') or game.get('release_date') or ''),
            "is_new": bool(game.get('is_new') or game.get('isNew')),
            "is_featured": bool(game.get('is_featured') or game.get('isFeatured')),
            "fallback": get_fallback_label(title),
        })
    catalog_json = json.dumps(catalog_data, ensure_ascii=False, separators=(',', ':')).replace("</", "<\\/")
    all_guide = {
        "title": "Free online games by category",
        "intro": "Find quick browser games for short breaks, school downtime, and casual play. Pick a category, open a game, and start playing without downloads or accounts.",
        "sections": [
            ("Pick by mood", "Choose action when you want fast reactions, puzzle for slower thinking, racing for speed, and casual games for an easy break."),
            ("Every game is linked", "This page includes a crawlable link to every game page so players and search engines can discover the full catalog."),
        ],
        "faq": [
            ("Are these games free to play?", "Yes. BTW game is built around free browser games that open without downloads."),
            ("Which category should I try first?", "Use Action or Parkour for movement, Puzzle for slower thinking, Racing for speed, and Cooking or Casual for lighter play."),
        ],
    }
    extra_jsonld = collection_jsonld("All Games | BTW game", all_guide["intro"], f"{SITE_URL}/games", games, all_guide["faq"])
    guide_html = render_category_guide_html("all", games[:24]).replace(category_guide("all").get("title", "Free all games"), all_guide["title"])
    sections = "\n".join(f'<article class="guide-section"><h3>{html_escape(title)}</h3><p>{html_escape(body)}</p></article>' for title, body in all_guide["sections"])
    guide_html = f'''
        <section class="category-guide" aria-labelledby="categoryGuideTitle">
            <div class="category-guide-header">
                <div>
                    <h2 id="categoryGuideTitle">{html_escape(all_guide["title"])}</h2>
                    <p>{html_escape(all_guide["intro"])}</p>
                </div>
                <span class="guide-count">{len(games)} games</span>
            </div>
            <div class="guide-link-block"><h3>Popular games</h3><div class="guide-link-list">{"".join(f'<a href="{game_url(normalize_slug(game.get("slug")))}">{html_escape(clean_text(game.get("title")))}</a>' for game in games[:12])}</div></div>
            <div class="guide-sections">{sections}</div>
            <div class="guide-related" aria-label="Related categories">{"".join(f'<a href="{category_url(category)}">{html_escape(category)}</a>' for category in categories[:10])}</div>
            <div class="guide-faq"><h2>FAQ</h2><div class="faq-list">{render_faq_html(all_guide["faq"])}</div></div>
        </section>
    '''
    return f'''<!DOCTYPE html>
<html lang="en">
{render_head("All Games | BTW game", "Browse all 500+ free online games at BTW game. Find action, puzzle, racing, sports, and casual games that play instantly in your browser.", "/games", SITE_IMAGE, extra_jsonld)}
<body>
    {render_header("games")}
    <main class="container">
        <div class="app-layout">
            {render_side_rail(categories=categories)}
            <div>
                <section class="filters-section">
                    <div class="toolbar-row">
                        <h1 class="filters-title" id="pageTitle">All games</h1>
                        <span class="results-count" id="resultsCount">{len(games)} games found</span>
                    </div>
                    <div class="catalog-toolbar">
                        <input type="search" class="search-bar" placeholder="Search games..." id="searchInput" autocomplete="off">
                        <div class="filter-group">
                            <label class="filter-label" for="sortSelect">Sort by</label>
                            <select class="filter-select" id="sortSelect">
                                <option value="popular">Most popular</option>
                                <option value="newest">Newest first</option>
                                <option value="rating">Highest rated</option>
                                <option value="name">Name A-Z</option>
                            </select>
                        </div>
                    </div>
                </section>
                <section class="games-section">
                    <div class="games-grid" id="gamesGrid">{game_cards}</div>
                    <div class="catalog-actions">
                        <button class="load-more-btn" id="loadMoreBtn" type="button">Load more games</button>
                    </div>
                    <div class="no-results" id="noResults" style="display: none;"><h2>No games found</h2><p>Try a broader search or switch back to All games.</p></div>
                </section>
                <details class="catalog-link-index">
                    <summary>All game links</summary>
                    <ul>{catalog_links}</ul>
                </details>
                {guide_html}
            </div>
        </div>
    </main>
    {render_footer()}
    <script src="/assets/js/api.js"></script>
    {render_nav_script()}
    <script type="application/json" id="catalogData">{catalog_json}</script>
    <script>
        const catalogData = JSON.parse(document.getElementById('catalogData').textContent);
        const gamesGrid = document.getElementById('gamesGrid');
        const searchInput = document.getElementById('searchInput');
        const sortSelect = document.getElementById('sortSelect');
        const resultsCount = document.getElementById('resultsCount');
        const noResults = document.getElementById('noResults');
        const loadMoreBtn = document.getElementById('loadMoreBtn');
        const pageSize = {CATALOG_PAGE_SIZE};
        let visibleLimit = {INITIAL_CATALOG_CARD_COUNT};
        let filteredGames = [...catalogData];

        function escapeHtml(value) {{
            return String(value || '').replace(/[&<>"']/g, char => ({{
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            }}[char]));
        }}

        function gameCard(game, index) {{
            const badge = game.is_new ? '<div class="game-badge">NEW</div>' : (game.is_featured ? '<div class="game-badge featured">FEATURED</div>' : '');
            const image = game.thumbnail_url
                ? `<img src="${{escapeHtml(game.thumbnail_url)}}" alt="${{escapeHtml(game.title)}}" width="{THUMBNAIL_WIDTH}" height="{THUMBNAIL_HEIGHT}" loading="${{index < 8 ? 'eager' : 'lazy'}}" decoding="async" onerror="this.style.display='none'; this.nextElementSibling.style.display='grid';">`
                : '';
            return `
                <a class="game-card" href="/games/${{escapeHtml(game.slug)}}">
                    <div class="game-thumbnail">
                        ${{badge}}
                        ${{image}}
                        <div class="thumbnail-fallback" style="${{game.thumbnail_url ? 'display:none;' : ''}}">${{escapeHtml(game.fallback || 'PLAY')}}</div>
                        <div class="game-info"><h3 class="game-title">${{escapeHtml(game.title)}}</h3></div>
                    </div>
                </a>`;
        }}

        function sortGames(games) {{
            const sort = sortSelect.value;
            return [...games].sort((a, b) => {{
                if (sort === 'newest') return new Date(b.created_at || 0) - new Date(a.created_at || 0);
                if (sort === 'rating') return (b.rating || 0) - (a.rating || 0);
                if (sort === 'name') return (a.title || '').localeCompare(b.title || '');
                return (b.total_plays || 0) - (a.total_plays || 0);
            }});
        }}

        function applyCatalogFilters(resetLimit = true) {{
            const query = searchInput.value.trim().toLowerCase();
            if (resetLimit) visibleLimit = pageSize;
            filteredGames = catalogData.filter(game => {{
                if (!query) return true;
                return [game.title, game.description, game.category_name, ...(game.tags || [])]
                    .filter(Boolean)
                    .join(' ')
                    .toLowerCase()
                    .includes(query);
            }});
            filteredGames = sortGames(filteredGames);
            renderCatalog();
        }}

        function renderCatalog() {{
            const visibleGames = filteredGames.slice(0, visibleLimit);
            gamesGrid.innerHTML = visibleGames.map(gameCard).join('');
            resultsCount.textContent = `${{filteredGames.length}} games found`;
            noResults.style.display = filteredGames.length ? 'none' : 'block';
            loadMoreBtn.hidden = visibleLimit >= filteredGames.length;
        }}

        loadMoreBtn.addEventListener('click', function() {{
            visibleLimit += pageSize;
            renderCatalog();
        }});
        searchInput.addEventListener('input', () => applyCatalogFilters(true));
        sortSelect.addEventListener('change', () => applyCatalogFilters(true));

        const initialSearch = new URLSearchParams(window.location.search).get('search');
        if (initialSearch) {{
            searchInput.value = initialSearch;
            applyCatalogFilters(true);
        }} else {{
            filteredGames = sortGames(filteredGames);
            renderCatalog();
        }}
    </script>
</body>
</html>'''

def generate_category_page(category, games):
    guide = category_guide(category)
    category_games = [game for game in games if matches_category(game, category)]
    if not category_games:
        return None
    category_games = sorted(category_games, key=lambda game: game.get('total_plays') or 0, reverse=True)
    cards = "\n".join(render_game_card(game, priority=index < 18) for index, game in enumerate(category_games))
    title = f"{guide['title']} | BTW game"
    description = guide["intro"]
    extra_jsonld = collection_jsonld(title, description, category_full_url(category), category_games, guide["faq"])
    categories = get_all_categories(games)
    return f'''<!DOCTYPE html>
<html lang="en">
{render_head(title, description, category_url(category), SITE_IMAGE, extra_jsonld)}
<body>
    {render_header("games")}
    <main class="container">
        <div class="app-layout">
            {render_side_rail(category, categories)}
            <div>
                <section class="list-page-header">
                    <h1 class="filters-title">{html_escape(guide["title"])}</h1>
                    <span class="results-count">{len(category_games)} games found</span>
                </section>
                <section class="games-section">
                    <div class="games-grid">{cards}</div>
                </section>
                {render_category_guide_html(category, category_games)}
            </div>
        </div>
    </main>
    {render_footer()}
    {render_nav_script()}
</body>
</html>'''

def select_best_games(games, definition):
    selector_categories = definition.get("selectors", {}).get("categories", [])
    selected = [
        game for game in games
        if any(matches_category(game, category) for category in selector_categories)
    ]
    selected = sorted(selected, key=lambda game: game.get('total_plays') or 0, reverse=True)
    if len(selected) < 24:
        seen = {normalize_slug(game.get('slug')) for game in selected}
        for game in sorted(games, key=lambda item: item.get('total_plays') or 0, reverse=True):
            slug = normalize_slug(game.get('slug'))
            if slug not in seen:
                selected.append(game)
                seen.add(slug)
            if len(selected) >= 36:
                break
    return selected[:36]

def generate_best_page(definition, games):
    selected_games = select_best_games(games, definition)
    cards = "\n".join(render_game_card(game, priority=index < 12) for index, game in enumerate(selected_games))
    sections = "\n".join(
        f'<article class="guide-section"><h2>{html_escape(title)}</h2><p>{html_escape(body)}</p></article>'
        for title, body in definition["sections"]
    )
    faq_html = render_faq_html(definition["faq"])
    related_links = "\n".join(
        f'<a href="/best/{html_escape(item["slug"])}">{html_escape(item["title"])}</a>'
        for item in BEST_PAGE_DEFINITIONS
        if item["slug"] != definition["slug"]
    )
    canonical_path = f'/best/{definition["slug"]}'
    extra_jsonld = collection_jsonld(
        f'{definition["title"]} | BTW game',
        definition["description"],
        f'{SITE_URL}{canonical_path}',
        selected_games,
        definition["faq"]
    )
    return f'''<!DOCTYPE html>
<html lang="en">
{render_head(f'{definition["title"]} | BTW game', definition["description"], canonical_path, SITE_IMAGE, extra_jsonld)}
<body>
    {render_header("games")}
    <main class="container">
        <div class="app-layout">
            {render_side_rail(categories=get_all_categories(games))}
            <div>
                <section class="list-page-header geo-page-header">
                    <div>
                        <p class="eyebrow">Best games guide</p>
                        <h1 class="filters-title">{html_escape(definition["h1"])}</h1>
                        <p class="section-note">{html_escape(definition["intro"])}</p>
                    </div>
                    <span class="results-count">{len(selected_games)} picks</span>
                </section>
                <section class="games-section">
                    <div class="games-grid">{cards}</div>
                </section>
                <section class="category-guide geo-guide" aria-labelledby="bestGuideTitle">
                    <div class="category-guide-header">
                        <div>
                            <h2 id="bestGuideTitle">How this guide helps</h2>
                            <p>{html_escape(definition["description"])}</p>
                        </div>
                    </div>
                    <div class="guide-sections">{sections}</div>
                    <div class="guide-related" aria-label="Related best game guides">{related_links}</div>
                    <div class="guide-faq"><h2>FAQ</h2><div class="faq-list">{faq_html}</div></div>
                </section>
            </div>
        </div>
    </main>
    {render_footer()}
    {render_nav_script()}
</body>
</html>'''

def render_plain_content_page(slug, title, description, sections, faq_items=None):
    canonical_path = f"/{slug}"
    article_jsonld = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": f"{title} | BTW game",
        "description": description,
        "url": f"{SITE_URL}{canonical_path}",
        "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": SITE_URL},
        "publisher": {"@id": f"{SITE_URL}/#organization"}
    }
    jsonld = jsonld_script(article_jsonld)
    if faq_items:
        jsonld += "\n" + jsonld_script({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": question, "acceptedAnswer": {"@type": "Answer", "text": answer}}
                for question, answer in faq_items
            ]
        })
    section_html = "\n".join(
        f'<section class="content-page-section"><h2>{html_escape(heading)}</h2><p>{html_escape(body)}</p></section>'
        for heading, body in sections
    )
    faq_html = f'<section class="content-page-section"><h2>FAQ</h2><div class="faq-list">{render_faq_html(faq_items)}</div></section>' if faq_items else ''
    return f'''<!DOCTYPE html>
<html lang="en">
{render_head(f'{title} | BTW game', description, canonical_path, SITE_IMAGE, jsonld)}
<body>
    {render_header("")}
    <main class="container">
        <article class="content-page">
            <p class="eyebrow">BTW game</p>
            <h1>{html_escape(title)}</h1>
            <p class="content-page-lede">{html_escape(description)}</p>
            {section_html}
            {faq_html}
        </article>
    </main>
    {render_footer()}
    {render_nav_script()}
</body>
</html>'''

def generate_trust_pages():
    pages = {
        "about": render_plain_content_page(
            "about",
            "About BTW game",
            "BTW game means By the way, play! We help casual players find fast, free browser games for quick breaks.",
            [
                ("What BTW game is", "BTW game is a curated browser-game catalog for casual players, kids, and students who want quick sessions without extra setup."),
                ("What we value", "The site is designed to feel fast, playful, and trustworthy, without casino styling, dark patterns, or unnecessary barriers."),
                ("How to use it", "Open a category, choose a game card, and play in the browser. Use the best-games guides when you want a faster recommendation."),
            ],
            [
                ("What does BTW game mean?", "BTW game means By the way, play! It describes short, casual play that fits between other moments."),
                ("Are games free?", "BTW game focuses on free browser games that can be opened from the site."),
            ]
        ),
        "contact": render_plain_content_page(
            "contact",
            "Contact BTW game",
            "Contact BTW game for site feedback, game listing questions, or content concerns.",
            [
                ("Site feedback", "Use this page as the contact reference for reporting broken games, incorrect thumbnails, category issues, or page quality problems."),
                ("Content concerns", "If a game listing appears inaccurate or inappropriate, include the game URL and a short description of the issue."),
                ("Publisher questions", "For game ownership or embed concerns, include the original game title, source URL, and the BTW game page URL."),
            ],
            [
                ("What should I include in a report?", "Include the page URL, game title, device, browser, and a short description of the problem."),
            ]
        ),
        "privacy": render_plain_content_page(
            "privacy",
            "Privacy Policy",
            "BTW game is a browser-game catalog. This policy summarizes the basic privacy posture of the site.",
            [
                ("Analytics and ads", "The site may use analytics and advertising scripts to understand traffic, improve pages, and support free access."),
                ("Game embeds", "Some games may load from third-party providers. Those providers can have their own privacy practices."),
                ("Data minimization", "BTW game is designed for browsing and playing games, not for collecting unnecessary account information."),
            ],
            [
                ("Do I need an account?", "No. BTW game does not require an account to browse the catalog."),
            ]
        ),
        "terms": render_plain_content_page(
            "terms",
            "Terms of Use",
            "These terms describe basic use of BTW game as a free browser-game catalog.",
            [
                ("Use of the site", "Use BTW game for lawful, personal browsing and gameplay. Follow school, family, and local rules about when games are appropriate."),
                ("Third-party games", "Game content can be provided by third-party sources. Availability, controls, and compatibility can vary by game."),
                ("Changes", "The catalog, categories, thumbnails, and links may change as the site is improved."),
            ],
            [
                ("Are all games guaranteed to work?", "No. Browser, device, network, or third-party source changes can affect individual games."),
            ]
        ),
        "editorial-policy": render_plain_content_page(
            "editorial-policy",
            "Editorial Policy",
            "BTW game organizes browser games with an emphasis on fast access, clear categories, and useful recommendations.",
            [
                ("How games are organized", "Games are grouped by category, tags, title, description, controls, and observed catalog patterns."),
                ("How recommendations are made", "Best-game guides prioritize quick starts, clear controls, browser access, category fit, and casual-player usefulness."),
                ("Accuracy standards", "Game pages avoid invented ratings and avoid claiming specific mechanics unless they are present in the source data or game description."),
            ],
            [
                ("Why can a category change?", "Categories can change when game data is cleaned or when a better fit is found for browsing and discovery."),
                ("Do you invent ratings?", "No. If reliable rating data is not available, the site avoids adding fake aggregate ratings."),
            ]
        ),
    }
    for slug, html in pages.items():
        with open(f"static_html/{slug}.html", "w", encoding="utf-8") as f:
            f.write(html)
    return list(pages.keys())

def generate_best_pages(games):
    os.makedirs("static_html/best", exist_ok=True)
    generated = []
    for definition in BEST_PAGE_DEFINITIONS:
        html = generate_best_page(definition, games)
        with open(f"static_html/best/{definition['slug']}.html", "w", encoding="utf-8") as f:
            f.write(html)
        generated.append(definition["slug"])
    return generated

def generate_llms_txt(games):
    categories = get_all_categories(games)
    lines = [
        "# BTW game",
        "",
        "BTW game means By the way, play! It is a free browser-game catalog for quick breaks, casual players, kids, and students.",
        "",
        "Canonical site: https://btwgame.com",
        "Sitemap: https://btwgame.com/sitemap.xml",
        "All games: https://btwgame.com/games",
        "",
        "Important pages:",
        "- https://btwgame.com/about",
        "- https://btwgame.com/editorial-policy",
        "- https://btwgame.com/best/free-online-games",
        "- https://btwgame.com/best/browser-games-for-school",
        "- https://btwgame.com/best/quick-games",
        "- https://btwgame.com/best/mobile-browser-games",
        "- https://btwgame.com/best/no-download-games",
        "",
        "Main categories:",
    ]
    lines.extend(f"- https://btwgame.com{category_url(category)}" for category in categories[:30])
    lines.extend([
        "",
        "Content notes:",
        "- Games are intended for free browser play.",
        "- Game pages include category, controls when available, FAQ, and related games.",
        "- Best-game pages are recommendation guides based on category fit, quick access, and casual play usefulness.",
    ])
    with open("static_html/llms.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

def generate_listing_pages(games, sync_static_sources=True):
    games = [normalize_game_data(game) for game in games]
    games = sorted(games, key=lambda game: game.get('total_plays') or 0, reverse=True)
    os.makedirs('static_html/categories', exist_ok=True)
    if os.path.exists('static/assets'):
        if os.path.exists('static_html/assets'):
            shutil.rmtree('static_html/assets')
        shutil.copytree('static/assets', 'static_html/assets')
    index_html = generate_index_page(games)
    games_html = generate_games_page(games)
    with open('static_html/index.html', 'w', encoding='utf-8') as f:
        f.write(index_html)
    with open('static_html/games.html', 'w', encoding='utf-8') as f:
        f.write(games_html)
    if sync_static_sources:
        with open('static/index.html', 'w', encoding='utf-8') as f:
            f.write(index_html)
        with open('static/games.html', 'w', encoding='utf-8') as f:
            f.write(games_html)
    categories = get_all_categories(games)
    generated = []
    for category in categories:
        html = generate_category_page(category, games)
        if not html:
            continue
        path = f"static_html/categories/{category_slug(category)}.html"
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        generated.append(category)
    with open('static_html/categories.json', 'w', encoding='utf-8') as f:
        json.dump([{"name": category, "slug": category_slug(category), "url": category_url(category)} for category in generated], f, ensure_ascii=False, indent=2)
    best_pages = generate_best_pages(games)
    trust_pages = generate_trust_pages()
    generate_llms_txt(games)
    print(f"📚 Generated index, games, {len(generated)} category pages, {len(best_pages)} best pages, and {len(trust_pages)} trust pages")

def generate_game_page(game_data, related_games):
    """Generate static HTML for a game page"""
    game_data = normalize_game_data(game_data)
    related_games = [normalize_game_data(game) for game in related_games]

    # Basic game information
    title = clean_text(game_data.get('title', 'Unknown Game'))
    description = clean_text(game_data.get('description', ''))
    long_description = clean_text(game_data.get('long_description', description))
    thumbnail_url = clean_text(game_data.get('thumbnail_url', ''))
    iframe_url = clean_text(game_data.get('iframe_url') or game_data.get('game_url', ''))
    category_name = clean_text(game_data.get('category_name', 'General'))
    rating = game_data.get('rating', 0)
    total_plays = game_data.get('total_plays', 0)
    tags = standardize_game_tags(game_data)  # Use standardized tags instead of API tags
    features = clean_value(game_data.get('features', []))
    controls = clean_value(game_data.get('controls', {}))
    release_date = clean_text(game_data.get('release_date', ''))
    slug = normalize_slug(game_data.get('slug', ''))
    expanded_description, how_to_play, controls_text, tips = build_game_content(title, description, long_description, category_name, tags, controls)
    faq_items = build_game_faq(title, category_name, controls)
    jsonld_html = build_game_jsonld(game_data, tags, faq_items)
    title_html = html_escape(title)
    description_html = html_escape(description)
    expanded_description_html = html_escape(expanded_description)
    how_to_play_html = html_escape(how_to_play)
    controls_text_html = html_escape(controls_text)
    tips_html = ''.join(f'<li>{html_escape(tip)}</li>' for tip in tips)
    faq_html = render_faq_html(faq_items)
    category_html = html_escape(category_name)
    title_attr = html_escape(title, quote=True)
    description_attr = html_escape(truncate(description or expanded_description, 155), quote=True)
    slug_attr = html_escape(slug, quote=True)
    iframe_attr = html_escape(iframe_url, quote=True)
    thumbnail_attr = html_escape(site_absolute_url(thumbnail_url), quote=True)
    category_href = category_url(category_name)
    category_href_attr = html_escape(category_href, quote=True)

    # Generate related games HTML
    related_games_html = ""
    play_next_html = ""
    if related_games:
        for related_game in related_games:
            related_thumbnail = clean_text(related_game.get('thumbnail_url', ''))
            related_slug = html_escape(normalize_slug(related_game.get('slug', '')))
            related_title_raw = clean_text(related_game.get('title', ''))
            related_title = html_escape(related_title_raw)
            related_category = html_escape(clean_text(related_game.get('category_name') or category_name))
            related_fallback = html_escape(get_fallback_label(related_title_raw))
            related_img = ''
            if related_thumbnail:
                escaped_thumbnail = html_escape(related_thumbnail, quote=True)
                related_img = f'<img src="{escaped_thumbnail}" alt="{related_title}" loading="lazy" onerror="this.style.display=\'none\'; this.nextElementSibling.style.display=\'grid\';">'
            related_games_html += f'''
                <a class="game-card wide" href="/games/{related_slug}">
                    <div class="game-thumbnail">
                        {related_img}
                        <div class="thumbnail-fallback" style="{'display:none;' if related_thumbnail else ''}">{related_fallback}</div>
                        <div class="game-info">
                            <h3 class="game-title">{related_title}</h3>
                        </div>
                    </div>
                </a>
            '''
            play_next_html += f'''
                <a class="play-next-item" href="/games/{related_slug}">
                    <div class="play-next-thumb">
                        {related_img}
                        <div class="thumbnail-fallback" style="{'display:none;' if related_thumbnail else ''}">{related_fallback}</div>
                    </div>
                    <div class="play-next-copy">
                        <strong>{related_title}</strong>
                        <span>{related_category}</span>
                    </div>
                </a>
            '''

    # Generate features HTML
    features_html = ""
    if features:
        for feature in features:
            features_html += f'''
                        <li>
                            <div class="feature-icon">✓</div>
                            <span>{html_escape(str(feature))}</span>
                        </li>
            '''

    # Generate controls HTML
    controls_html = ""
    if controls:
        for key, description in controls.items():
            controls_html += f'''
                        <div class="control-item">
                            <span class="control-key">{html_escape(str(key))}</span>
                            <span>{html_escape(str(description))}</span>
                        </div>
            '''

    # Generate tags HTML
    tags_html = ""
    if tags:
        for tag in tags:
            tags_html += f'<span class="tag">{html_escape(str(tag))}</span>'

    # Format release date
    release_date_formatted = "Coming Soon"
    if release_date:
        try:
            from datetime import datetime
            date_obj = datetime.fromisoformat(release_date.replace('Z', '+00:00'))
            release_date_formatted = date_obj.strftime('%B %d, %Y')
        except:
            release_date_formatted = release_date

    game_embed_html = ""
    if iframe_url:
        game_embed_html = f'''
        <section class="game-container" id="gameContainer">
            <div class="game-wrapper">
                <div class="loading-indicator">Loading game...</div>
                <iframe id="gameIframe" class="game-iframe" src="{iframe_attr}" title="{title_html}" allowfullscreen loading="lazy" onload="this.previousElementSibling.style.display='none'"></iframe>
            </div>
        </section>'''

    tags_section_html = f'<div class="game-tags">{tags_html}</div>' if tags_html else ''
    features_card_html = f'<div class="info-card"><h3 class="card-title">Game Features</h3><ul class="features-list">{features_html}</ul></div>' if features_html else ''
    controls_card_html = f'<div class="info-card"><h3 class="card-title">Controls</h3><div class="controls-grid">{controls_html}</div></div>' if controls_html else ''
    fact_summary_html = f'''
                        <section class="fact-summary-card" aria-labelledby="factSummaryTitle">
                            <h2 class="card-title" id="factSummaryTitle">{title_html} facts</h2>
                            <dl class="fact-summary-grid">
                                <div><dt>Game name</dt><dd>{title_html}</dd></div>
                                <div><dt>Category</dt><dd>{category_html}</dd></div>
                                <div><dt>Play style</dt><dd>Free browser game</dd></div>
                                <div><dt>Best for</dt><dd>Quick breaks and casual play</dd></div>
                                <div><dt>Device</dt><dd>Modern browser</dd></div>
                                <div><dt>Download required</dt><dd>No</dd></div>
                                <div><dt>Price</dt><dd>Free</dd></div>
                            </dl>
                        </section>
    '''
    related_section_html = f'''
                <section class="related-games">
                    <div class="section-header">
                        <div>
                            <h2 class="section-title">More games to try</h2>
                            <p class="section-note">Games from the same shelf as {title_html}.</p>
                        </div>
                        <a href="/games" class="view-all-btn">View all games</a>
                    </div>
                    <div class="games-grid compact">{related_games_html}</div>
                </section>''' if related_games_html else ''
    play_next_section_html = f'''
                        <aside class="play-next-panel" aria-label="Play next">
                            <div class="play-next-header">
                                <h2 class="card-title">Play next</h2>
                                <a href="{category_href_attr}" class="view-all-btn">More</a>
                            </div>
                            <div class="play-next-list">{play_next_html}</div>
                        </aside>''' if play_next_html else ''

    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Play {title_attr} free online at BTW game. {description_attr}">
    <meta name="keywords" content="free online game, browser game, BTW game, {category_html}, {', '.join(html_escape(str(tag)) for tag in tags)}">
    <meta name="author" content="BTW game">
    <meta property="og:title" content="{title_attr} | BTW game">
    <meta property="og:description" content="{description_attr}">
    <meta property="og:image" content="{thumbnail_attr}">
    <meta property="og:url" content="https://btwgame.com/games/{slug_attr}">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title_attr} | BTW game">
    <meta name="twitter:description" content="{description_attr}">
    <meta name="twitter:image" content="{thumbnail_attr}">
    <link rel="canonical" href="https://btwgame.com/games/{slug_attr}">
    <link rel="stylesheet" href="/assets/css/site.css">
    {jsonld_html}

    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-SM7PBYVK97"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag() {{ dataLayer.push(arguments); }}
        gtag('js', new Date());
        gtag('config', 'G-SM7PBYVK97');
    </script>
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8930741225505243"
         crossorigin="anonymous"></script>

    <title>{title_html} | BTW game</title>
</head>
<body>
    <header class="site-header">
        <nav class="site-nav container" aria-label="Primary navigation">
            {render_brand_mark()}
            <div class="nav-search" role="search">
                <form onsubmit="event.preventDefault(); navSearchGames();">
                    <input type="search" class="search-bar" placeholder="Search games..." id="navSearchInput" autocomplete="off">
                    <button class="search-btn compact" type="submit">Search</button>
                </form>
            </div>
            <button class="mobile-menu" type="button" onclick="toggleMenu()" aria-label="Open navigation" aria-controls="navLinks">
                <span></span>
                <span></span>
                <span></span>
            </button>
            <ul class="nav-links" id="navLinks">
                <li><a href="/">Home</a></li>
                <li><a href="/games">All games</a></li>
                <li><a href="/games?filter=new">New</a></li>
                <li><a href="/games?filter=featured">Featured</a></li>
            </ul>
        </nav>
    </header>

    <main class="container">
        <div class="app-layout detail-app-layout">
            <aside class="side-rail" aria-label="Game navigation">
                <section class="rail-panel">
                    <h2 class="rail-title">Explore</h2>
                    <ul class="rail-links">
                        <li><a href="/"><span class="rail-icon">⌂</span>Home</a></li>
                        <li><a href="/games"><span class="rail-icon">▦</span>All games</a></li>
                        <li><a href="/games?filter=new"><span class="rail-icon">✦</span>New games</a></li>
                        <li><a href="/games?filter=featured"><span class="rail-icon">★</span>Featured</a></li>
                    </ul>
                </section>
                <section class="rail-panel">
                    <h2 class="rail-title">Category</h2>
                    <ul class="rail-links">
                        <li><a href="{category_href_attr}" aria-current="page"><span class="rail-icon">●</span>{category_html}</a></li>
                        {render_rail_links(category_name)}
                    </ul>
                </section>
            </aside>

            <div>
                <section class="game-stage-layout" aria-label="{title_html}">
                    <div class="game-stage-main">
                        {game_embed_html}

                        <div class="game-title-bar">
                            <div>
                                <div class="game-breadcrumbs">
                                    <a href="/games">Games</a>
                                    <span>/</span>
                                    <a href="{category_href_attr}">{category_html}</a>
                                </div>
                                <h1 class="game-detail-title">{title_html}</h1>
                            </div>
                            <div class="game-action-row">
                                <a class="button-primary" href="#gameContainer">Play now</a>
                                <a class="button-secondary" href="{category_href_attr}">More {category_html}</a>
                            </div>
                        </div>

                        <div class="game-meta-row" aria-label="Game details">
                            <span class="meta-pill">Rating {rating:.1f}</span>
                            <span class="meta-pill">{total_plays:,} plays</span>
                            <span class="meta-pill">{category_html}</span>
                            <span class="meta-pill">Updated {html_escape(str(release_date_formatted))}</span>
                        </div>
                    </div>
                    {play_next_section_html}
                </section>

                <section class="game-info-layout" aria-label="About and controls">
                    <div class="game-description-panel">
                        <h2 class="card-title">About {title_html}</h2>
                        <p>{expanded_description_html}</p>
                        {tags_section_html}
                        {fact_summary_html}
                        <h2 class="card-title">How to play {title_html}</h2>
                        <p>{how_to_play_html}</p>
                        <h2 class="card-title">Controls</h2>
                        <p>{controls_text_html}</p>
                        <h2 class="card-title">Tips for {title_html}</h2>
                        <ul class="features-list">{tips_html}</ul>
                        <h2 class="card-title">FAQ</h2>
                        <div class="faq-list">{faq_html}</div>
                    </div>

                    <aside class="game-sidebar" aria-label="Game help">
                        {features_card_html}
                        {controls_card_html}
                        <div class="info-card">
                            <h2 class="card-title">Game info</h2>
                            <div class="controls-grid">
                                <div class="control-item"><span>Category</span><span class="control-key">{category_html}</span></div>
                                <div class="control-item"><span>Plays</span><span class="control-key">{total_plays:,}</span></div>
                                <div class="control-item"><span>Rating</span><span class="control-key">{rating:.1f}</span></div>
                            </div>
                        </div>
                    </aside>
                </section>

                {related_section_html}
            </div>
        </div>
    </main>

    <footer class="site-footer">
        <div class="footer-content container">
            <p>&copy; 2026 BTW game. All rights reserved.</p>
            <ul class="footer-links">
                <li><a href="/">Home</a></li>
                <li><a href="/games">All games</a></li>
                <li><a href="/games?filter=new">New games</a></li>
            </ul>
        </div>
    </footer>

    <script>
        function toggleMenu() {{
            document.getElementById('navLinks').classList.toggle('active');
        }}

        function navSearchGames() {{
            const query = document.getElementById('navSearchInput').value.trim();
            window.location.href = query ? `/games?search=${{encodeURIComponent(query)}}` : '/games';
        }}

        document.addEventListener('DOMContentLoaded', function() {{
            if (typeof gtag !== 'undefined') {{
                gtag('event', 'game_view', {{
                    'game_name': '{title_attr}',
                    'game_category': '{category_html}'
                }});
            }}
        }});
    </script>
</body>
</html>'''

    return html_content

def save_all_games_json(all_games_data):
    """Save all games data to static_html/all_games.json"""
    try:
        games_json_data = {
            "metadata": {
                "total_games": len(all_games_data),
                "generated_at": datetime.now().isoformat(),
                "website": "BTW game",
                "api_base_url": BASE_URL
            },
            "games": all_games_data
        }

        with open('static_html/all_games.json', 'w', encoding='utf-8') as f:
            json.dump(games_json_data, f, indent=2, ensure_ascii=False)

        new_games = [game for game in all_games_data if game.get('is_new') or game.get('isNew')]
        if not new_games:
            new_games = sorted(
                all_games_data,
                key=lambda game: game.get('created_at') or game.get('release_date') or '',
                reverse=True
            )[:24]
        with open('static_html/new_games.json', 'w', encoding='utf-8') as f:
            json.dump({"games": new_games}, f, indent=2, ensure_ascii=False)

        print(f"📊 Updated static_html/all_games.json with {len(all_games_data)} games")
        return True
    except Exception as e:
        print(f"❌ Error saving all_games.json: {e}")
        return False

def fetch_all_games_from_db():
    """Fetch all game slugs directly from database"""
    try:
        from app import create_app, db
        from models import Game

        app = create_app()
        with app.app_context():
            games = Game.query.filter_by(is_active=True).all()
            slugs = [game.slug for game in games]
            print(f"📊 Fetched {len(slugs)} games from database")
            return slugs
    except Exception as e:
        print(f"❌ Error fetching from database: {e}")
        return None

def load_external_static_games():
    """Load extra static game records from optional source files."""
    external_games = []
    for path in ['crazygames_games.json', 'minigame_games.json']:
        if not os.path.exists(path):
            continue
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            games = data.get('games', []) if isinstance(data, dict) else data
            for game in games:
                if game.get('title') and game.get('iframe_url'):
                    external_games.append(normalize_game_data(game))
            print(f"📦 Loaded {len(games)} external games from {path}")
        except Exception as e:
            print(f"⚠️  Failed to load {path}: {e}")
    return external_games

def main():
    """Generate all static game pages and update all_games.json"""

    print("🚀 Generating static game pages and updating all_games.json...")

    # Try to get game slugs from database first
    game_slugs = fetch_all_games_from_db()

    # Fallback to game_slugs.txt if database fetch fails
    if not game_slugs:
        print("⚠️  Database fetch failed, trying game_slugs.txt...")
        try:
            with open('static_html/game_slugs.txt', 'r') as f:
                game_slugs = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print("❌ game_slugs.txt not found and database fetch failed!")
            print("💡 Make sure the database is set up or game_slugs.txt exists")
            return

    print(f"📋 Found {len(game_slugs)} games to process")

    # Create games directory
    os.makedirs('static_html/games', exist_ok=True)
    for existing_file in os.listdir('static_html/games'):
        if existing_file.endswith('.html'):
            os.remove(os.path.join('static_html/games', existing_file))

    success_count = 0
    error_count = 0
    all_games_data = []
    seen_slugs = set()

    generated_page_data = []
    for slug in game_slugs:
        print(f"📄 Processing {slug}...")

        # Fetch game data
        game_data = fetch_game_data(slug)
        if not game_data:
            error_count += 1
            continue
        game_data = normalize_game_data(game_data)
        normalized_slug = game_data.get('slug')

        # Add to all games collection with standardized tags
        game_data_with_tags = game_data.copy()
        game_data_with_tags['standardized_tags'] = standardize_game_tags(game_data)
        if normalized_slug in seen_slugs:
            print(f"⚠️  Skipping duplicate slug after normalization: {normalized_slug}")
            continue
        seen_slugs.add(normalized_slug)
        all_games_data.append(game_data_with_tags)

        generated_page_data.append(game_data)

    external_games = load_external_static_games()
    for game_data in external_games:
        normalized_slug = game_data.get('slug')
        if not normalized_slug or normalized_slug in seen_slugs:
            continue
        print(f"📄 Processing external {normalized_slug}...")
        game_data_with_tags = game_data.copy()
        game_data_with_tags['standardized_tags'] = standardize_game_tags(game_data)
        seen_slugs.add(normalized_slug)
        all_games_data.append(game_data_with_tags)
        generated_page_data.append(game_data)

    all_games_data = apply_primary_category_fallbacks(all_games_data)
    page_data_by_slug = {
        normalize_slug(game.get('slug')): game
        for game in apply_primary_category_fallbacks(generated_page_data)
    }
    all_games_data = cache_game_thumbnails(all_games_data)
    for cached_game in all_games_data:
        normalized_slug = normalize_slug(cached_game.get('slug'))
        if normalized_slug in page_data_by_slug:
            page_data_by_slug[normalized_slug]['thumbnail_url'] = cached_game.get('thumbnail_url')
            page_data_by_slug[normalized_slug]['thumbnail'] = cached_game.get('thumbnail')
            page_data_by_slug[normalized_slug]['original_thumbnail_url'] = cached_game.get('original_thumbnail_url')

    for game_data_with_tags in all_games_data:
        normalized_slug = normalize_slug(game_data_with_tags.get('slug'))
        game_data = page_data_by_slug.get(normalized_slug, game_data_with_tags)
        related_games = [
            game for game in all_games_data
            if matches_category(game, game_data.get('category_name')) and normalize_slug(game.get('slug')) != normalized_slug
        ][:6]
        try:
            html_content = generate_game_page(game_data, related_games)
            filename = f"static_html/games/{normalized_slug}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            success_count += 1
            print(f"✅ Generated {filename}")
        except Exception as e:
            print(f"❌ Error generating page for {normalized_slug}: {e}")
            error_count += 1

    # Save all games data to JSON
    if all_games_data:
        save_all_games_json(all_games_data)
        generate_listing_pages(all_games_data)

    print(f"\n🎯 Generation complete!")
    print(f"✅ Success: {success_count} pages")
    print(f"❌ Errors: {error_count} pages")
    print(f"📁 Pages saved in: static_html/games/")
    print(f"📊 Games data saved in: static_html/all_games.json")

if __name__ == "__main__":
    main()
