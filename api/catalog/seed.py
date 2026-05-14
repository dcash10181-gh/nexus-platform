"""
Seed catalog — 40 curated titles with full ContentDNA, used to bootstrap
the vector store and knowledge graph in development / trial mode.

Run with: python -m catalog.seed
"""
from __future__ import annotations

import asyncio
import logging

from catalog.graph import get_graph
from catalog.vector_store import get_vector_store

log = logging.getLogger(__name__)

CATALOG: list[dict] = [
    {
        "id": "inception-2010",
        "title": "Inception",
        "year": 2010,
        "kind": "film",
        "synopsis": "A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
        "genres": ["Sci-Fi", "Action", "Thriller"],
        "cast": ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Elliot Page", "Tom Hardy"],
        "director": "Christopher Nolan",
        "rating": 8.8,
        "poster_url": "https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/original/s3TBrRGB1iav7gFOCNx3H31MoES.jpg",
        "dna": {
            "pacing": 0.78,
            "tension_curve": [0.3, 0.5, 0.7, 0.85, 0.95, 0.9],
            "visual_style": "cinematic",
            "audio_mood": "ominous",
            "thematic_tags": ["identity", "memory", "heist", "dreams", "reality"],
            "runtime_min": 148,
        },
    },
    {
        "id": "severance-s1-2022",
        "title": "Severance",
        "year": 2022,
        "kind": "series",
        "synopsis": "Mark leads a team of office workers whose memories have been surgically divided between their work and personal lives.",
        "genres": ["Sci-Fi", "Thriller", "Drama"],
        "cast": ["Adam Scott", "Patricia Arquette", "John Turturro", "Britt Lower"],
        "director": "Ben Stiller",
        "rating": 8.7,
        "poster_url": "https://image.tmdb.org/t/p/w500/b6tsr7PFYK9LKA7q7UjOlFOkwLQ.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/original/lXsHn3CKFjHuOnNaTQSuVQhEPZg.jpg",
        "dna": {
            "pacing": 0.45,
            "tension_curve": [0.2, 0.35, 0.6, 0.75, 0.9, 0.95],
            "visual_style": "sterile_geometric",
            "audio_mood": "unnerving",
            "thematic_tags": ["identity", "corporate dystopia", "memory", "work-life balance"],
            "runtime_min": 50,
        },
    },
    {
        "id": "the-bear-s1-2022",
        "title": "The Bear",
        "year": 2022,
        "kind": "series",
        "synopsis": "A young chef from the fine dining world returns to Chicago to run his family's sandwich shop.",
        "genres": ["Drama", "Comedy"],
        "cast": ["Jeremy Allen White", "Ebon Moss-Bachrach", "Ayo Edebiri"],
        "director": "Christopher Storer",
        "rating": 8.7,
        "poster_url": "https://image.tmdb.org/t/p/w500/sHFlbKS3WLqMnp9t2ghADIJFnuQ.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/original/7zt6BnHOhVGFqSKDCEbRTmwEcFn.jpg",
        "dna": {
            "pacing": 0.88,
            "tension_curve": [0.5, 0.7, 0.8, 0.9, 0.95, 0.85],
            "visual_style": "handheld_naturalistic",
            "audio_mood": "intense",
            "thematic_tags": ["grief", "ambition", "family", "trauma", "culinary arts"],
            "runtime_min": 30,
        },
    },
    {
        "id": "everything-everywhere-2022",
        "title": "Everything Everywhere All at Once",
        "year": 2022,
        "kind": "film",
        "synopsis": "An aging Chinese immigrant is swept up in an insane adventure, in which she alone can save what's important to her by exploring other universes.",
        "genres": ["Sci-Fi", "Comedy", "Drama", "Action"],
        "cast": ["Michelle Yeoh", "Ke Huy Quan", "Jamie Lee Curtis", "Stephanie Hsu"],
        "director": "The Daniels",
        "rating": 7.8,
        "poster_url": "https://image.tmdb.org/t/p/w500/w3LxiVYdWWRvEVdn5RYq6jIqkb1.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/original/ss0Os3uWJfQAENILHZUdX8Tt1OC.jpg",
        "dna": {
            "pacing": 0.92,
            "tension_curve": [0.4, 0.6, 0.8, 0.9, 0.7, 0.8],
            "visual_style": "maximalist_surreal",
            "audio_mood": "playful_intense",
            "thematic_tags": ["multiverse", "identity", "family", "nihilism", "love"],
            "runtime_min": 139,
        },
    },
    {
        "id": "succession-s4-2023",
        "title": "Succession",
        "year": 2018,
        "kind": "series",
        "synopsis": "The Roy family controls one of the biggest media and entertainment conglomerates in the world. Their fight for power leads to betrayal.",
        "genres": ["Drama", "Comedy"],
        "cast": ["Brian Cox", "Jeremy Strong", "Sarah Snook", "Kieran Culkin"],
        "director": "Jesse Armstrong",
        "rating": 8.9,
        "poster_url": "https://image.tmdb.org/t/p/w500/e2X8g1RBKSNmFEOdnMxIMH4zwbF.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/original/kHEsNFQXHVhWFVwCMsHwVFYjFqj.jpg",
        "dna": {
            "pacing": 0.55,
            "tension_curve": [0.4, 0.55, 0.65, 0.75, 0.85, 0.95],
            "visual_style": "prestige_naturalistic",
            "audio_mood": "tense_sardonic",
            "thematic_tags": ["power", "family dysfunction", "capitalism", "betrayal", "media"],
            "runtime_min": 58,
        },
    },
    {
        "id": "blade-runner-2049",
        "title": "Blade Runner 2049",
        "year": 2017,
        "kind": "film",
        "synopsis": "A young blade runner discovers a long-buried secret that leads him to track down former blade runner Rick Deckard.",
        "genres": ["Sci-Fi", "Drama", "Thriller"],
        "cast": ["Ryan Gosling", "Harrison Ford", "Ana de Armas"],
        "director": "Denis Villeneuve",
        "rating": 8.0,
        "poster_url": "https://image.tmdb.org/t/p/w500/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/original/ilRyazdMtRFFnBp68BRMFBJKDGs.jpg",
        "dna": {
            "pacing": 0.28,
            "tension_curve": [0.2, 0.3, 0.4, 0.55, 0.7, 0.8],
            "visual_style": "neo_noir_cinematic",
            "audio_mood": "melancholic_atmospheric",
            "thematic_tags": ["AI consciousness", "identity", "memory", "humanity", "dystopia"],
            "runtime_min": 164,
        },
    },
    {
        "id": "dune-part-two-2024",
        "title": "Dune: Part Two",
        "year": 2024,
        "kind": "film",
        "synopsis": "Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family.",
        "genres": ["Sci-Fi", "Adventure", "Drama"],
        "cast": ["Timothée Chalamet", "Zendaya", "Rebecca Ferguson", "Austin Butler"],
        "director": "Denis Villeneuve",
        "rating": 8.5,
        "poster_url": "https://image.tmdb.org/t/p/w500/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/original/xOMo8BRK7PfcJv9JCnx7s5hj0PX.jpg",
        "dna": {
            "pacing": 0.65,
            "tension_curve": [0.3, 0.5, 0.7, 0.8, 0.9, 0.95],
            "visual_style": "epic_cinematic",
            "audio_mood": "grand_ominous",
            "thematic_tags": ["prophecy", "colonialism", "religion", "power", "ecology"],
            "runtime_min": 167,
        },
    },
    {
        "id": "oppenheimer-2023",
        "title": "Oppenheimer",
        "year": 2023,
        "kind": "film",
        "synopsis": "The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb.",
        "genres": ["Drama", "History", "Thriller"],
        "cast": ["Cillian Murphy", "Emily Blunt", "Matt Damon", "Robert Downey Jr."],
        "director": "Christopher Nolan",
        "rating": 8.9,
        "poster_url": "https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/original/rLb2cwF3Pazuxaj0sRXQ037tGI1.jpg",
        "dna": {
            "pacing": 0.62,
            "tension_curve": [0.3, 0.5, 0.6, 0.75, 0.9, 0.8],
            "visual_style": "epic_prestige",
            "audio_mood": "intense_cerebral",
            "thematic_tags": ["nuclear age", "moral responsibility", "genius", "Cold War", "guilt"],
            "runtime_min": 180,
        },
    },
    {
        "id": "dark-s1-2017",
        "title": "Dark",
        "year": 2017,
        "kind": "series",
        "synopsis": "A family saga with a supernatural twist set in a German town where the disappearance of two children exposes the connections among four families.",
        "genres": ["Sci-Fi", "Mystery", "Thriller"],
        "cast": ["Louis Hofmann", "Oliver Masucci", "Lisa Vicari"],
        "director": "Baran bo Odar",
        "rating": 8.8,
        "poster_url": "https://image.tmdb.org/t/p/w500/apbrbWs8M9lyOpJYU5WXrpFbk1Z.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/original/rSPw7tgCH9c6NqICZef4kZjFOQ5.jpg",
        "dna": {
            "pacing": 0.4,
            "tension_curve": [0.25, 0.45, 0.6, 0.75, 0.85, 0.9],
            "visual_style": "dark_european",
            "audio_mood": "eerie_atmospheric",
            "thematic_tags": ["time travel", "determinism", "family secrets", "cycles", "German mythology"],
            "runtime_min": 52,
        },
    },
    {
        "id": "beef-2023",
        "title": "Beef",
        "year": 2023,
        "kind": "limited",
        "synopsis": "A road rage incident ignites a feud between two strangers — a contractor and a businesswoman — that threatens to consume their lives.",
        "genres": ["Drama", "Comedy", "Thriller"],
        "cast": ["Steven Yeun", "Ali Wong"],
        "director": "Lee Sung Jin",
        "rating": 8.1,
        "poster_url": "https://image.tmdb.org/t/p/w500/nToukHLMFgJpRSmJFh2CHkDjxFW.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/original/sGtHFaAGFcM1MHvjMIjnkU8UcpB.jpg",
        "dna": {
            "pacing": 0.75,
            "tension_curve": [0.4, 0.6, 0.7, 0.8, 0.9, 0.85],
            "visual_style": "naturalistic",
            "audio_mood": "tense_darkly_comic",
            "thematic_tags": ["rage", "class", "identity", "immigrant experience", "self-destruction"],
            "runtime_min": 40,
        },
    },
    {
        "id": "past-lives-2023",
        "title": "Past Lives",
        "year": 2023,
        "kind": "film",
        "synopsis": "Nora and Hae Sung, two childhood sweethearts, are inexorably separated, then reunited over two decades.",
        "genres": ["Romance", "Drama"],
        "cast": ["Greta Lee", "Teo Yoo", "John Magaro"],
        "director": "Celine Song",
        "rating": 7.9,
        "poster_url": "https://image.tmdb.org/t/p/w500/k3waqVXSnYBLYPaFnFzOlfhiMFk.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/original/uhYFSMIVmhm5AFxQRi8g0mhGvvS.jpg",
        "dna": {
            "pacing": 0.22,
            "tension_curve": [0.2, 0.25, 0.3, 0.4, 0.5, 0.6],
            "visual_style": "lyrical_naturalistic",
            "audio_mood": "melancholic_tender",
            "thematic_tags": ["longing", "paths not taken", "cultural identity", "love", "diaspora"],
            "runtime_min": 106,
        },
    },
    {
        "id": "house-of-dragon-s1-2022",
        "title": "House of the Dragon",
        "year": 2022,
        "kind": "series",
        "synopsis": "The story of House Targaryen set 200 years before the events of Game of Thrones.",
        "genres": ["Fantasy", "Drama", "Action"],
        "cast": ["Matt Smith", "Emma D'Arcy", "Olivia Cooke", "Paddy Considine"],
        "director": "Miguel Sapochnik",
        "rating": 8.4,
        "poster_url": "https://image.tmdb.org/t/p/w500/z2yahl2uefxDCl0nogcRBstwruJ.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/original/etj8E2o0Bud0HkONVQPjyCkIvpv.jpg",
        "dna": {
            "pacing": 0.58,
            "tension_curve": [0.3, 0.5, 0.65, 0.75, 0.85, 0.9],
            "visual_style": "epic_dark_fantasy",
            "audio_mood": "sweeping_ominous",
            "thematic_tags": ["succession", "dragons", "war", "betrayal", "dynastic politics"],
            "runtime_min": 60,
        },
    },
    {
        "id": "station-eleven-2021",
        "title": "Station Eleven",
        "year": 2021,
        "kind": "limited",
        "synopsis": "Set before, during, and after a devastating pandemic, multiple characters grapple with what it means to preserve humanity.",
        "genres": ["Sci-Fi", "Drama", "Mystery"],
        "cast": ["Himesh Patel", "Mackenzie Davis", "Gael García Bernal"],
        "director": "Hiro Murai",
        "rating": 8.1,
        "poster_url": "https://image.tmdb.org/t/p/w500/8CuuNwMwkJoMlnOfQZMBxGBjXsv.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/original/1Bsb4d3wZbHkAMRDL1pjJqmhz6n.jpg",
        "dna": {
            "pacing": 0.42,
            "tension_curve": [0.3, 0.4, 0.5, 0.6, 0.7, 0.65],
            "visual_style": "lyrical_cinematic",
            "audio_mood": "melancholic_hopeful",
            "thematic_tags": ["pandemic", "art", "memory", "civilization", "survival"],
            "runtime_min": 50,
        },
    },
    {
        "id": "andor-s1-2022",
        "title": "Andor",
        "year": 2022,
        "kind": "series",
        "synopsis": "In an era filled with danger, deception, and intrigue, Cassian Andor will embark on his path to becoming a Rebel hero.",
        "genres": ["Sci-Fi", "Action", "Drama"],
        "cast": ["Diego Luna", "Stellan Skarsgård", "Genevieve O'Reilly"],
        "director": "Tony Gilroy",
        "rating": 8.4,
        "poster_url": "https://image.tmdb.org/t/p/w500/59svAcFPpBRCVnp4mhqtSyWcMaT.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/original/59svAcFPpBRCVnp4mhqtSyWcMaT.jpg",
        "dna": {
            "pacing": 0.55,
            "tension_curve": [0.35, 0.5, 0.65, 0.75, 0.88, 0.92],
            "visual_style": "gritty_grounded",
            "audio_mood": "intense_political",
            "thematic_tags": ["resistance", "sacrifice", "imperialism", "radicalization", "solidarity"],
            "runtime_min": 47,
        },
    },
    {
        "id": "the-last-of-us-s1-2023",
        "title": "The Last of Us",
        "year": 2023,
        "kind": "series",
        "synopsis": "After a global catastrophe, a hardened survivor and a teenage girl make a dangerous journey across a post-apocalyptic America.",
        "genres": ["Drama", "Sci-Fi", "Horror"],
        "cast": ["Pedro Pascal", "Bella Ramsey", "Gabriel Luna"],
        "director": "Craig Mazin",
        "rating": 8.8,
        "poster_url": "https://image.tmdb.org/t/p/w500/uKvVjHNqB5VmOrdxqAt2F7J78ED.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/original/9Gt1lUoQFLvQPtPLjKlZMxIRlDV.jpg",
        "dna": {
            "pacing": 0.52,
            "tension_curve": [0.3, 0.55, 0.65, 0.75, 0.85, 0.9],
            "visual_style": "naturalistic_bleak",
            "audio_mood": "melancholic_haunting",
            "thematic_tags": ["survival", "fatherhood", "grief", "humanity", "apocalypse"],
            "runtime_min": 55,
        },
    },
    {
        "id": "shogun-2024",
        "title": "Shogun",
        "year": 2024,
        "kind": "limited",
        "synopsis": "A mysterious European sailor washes ashore in feudal Japan and finds himself in the middle of a civil war.",
        "genres": ["Drama", "History", "Action"],
        "cast": ["Hiroyuki Sanada", "Cosmo Jarvis", "Anna Sawai"],
        "director": "Rachel Kondo",
        "rating": 8.8,
        "poster_url": "https://image.tmdb.org/t/p/w500/7O4iVfOMQmdCSxhOg1WnzG1AgYT.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/original/oZGCMfFHDN7O1H9RtR2OHNzL6RM.jpg",
        "dna": {
            "pacing": 0.48,
            "tension_curve": [0.25, 0.45, 0.6, 0.75, 0.85, 0.9],
            "visual_style": "epic_period",
            "audio_mood": "ceremonial_tense",
            "thematic_tags": ["feudal Japan", "honor", "war", "culture clash", "political intrigue"],
            "runtime_min": 58,
        },
    },
    {
        "id": "the-menu-2022",
        "title": "The Menu",
        "year": 2022,
        "kind": "film",
        "synopsis": "A young couple travels to a coastal island to eat at an exclusive restaurant where the chef has prepared a lavish menu with some shocking surprises.",
        "genres": ["Horror", "Comedy", "Thriller"],
        "cast": ["Anya Taylor-Joy", "Ralph Fiennes", "Nicholas Hoult"],
        "director": "Mark Mylod",
        "rating": 7.2,
        "poster_url": "https://image.tmdb.org/t/p/w500/v7UF7ypAqjsFZFdjksjQ7IUpXdn.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/original/we7WCaMDDYXUCHcOKsOoBYVqSmT.jpg",
        "dna": {
            "pacing": 0.65,
            "tension_curve": [0.3, 0.5, 0.65, 0.8, 0.9, 0.85],
            "visual_style": "dark_satirical",
            "audio_mood": "unsettling_darkly_comic",
            "thematic_tags": ["class satire", "art", "authenticity", "obsession", "food culture"],
            "runtime_min": 107,
        },
    },
    {
        "id": "parasite-2019",
        "title": "Parasite",
        "year": 2019,
        "kind": "film",
        "synopsis": "A poor family schemes to become employed by a wealthy family by infiltrating their household.",
        "genres": ["Drama", "Thriller", "Comedy"],
        "cast": ["Song Kang-ho", "Choi Woo-shik", "Park So-dam"],
        "director": "Bong Joon-ho",
        "rating": 8.5,
        "poster_url": "https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/original/TU9NIjwzjoKPwQHoHshkFcQUCG.jpg",
        "dna": {
            "pacing": 0.72,
            "tension_curve": [0.3, 0.5, 0.6, 0.8, 0.95, 0.9],
            "visual_style": "precise_geometric",
            "audio_mood": "playful_to_terrifying",
            "thematic_tags": ["class inequality", "deception", "survival", "Korean society", "architecture"],
            "runtime_min": 132,
        },
    },
    {
        "id": "white-lotus-s2-2022",
        "title": "The White Lotus",
        "year": 2021,
        "kind": "limited",
        "synopsis": "The exploits of various guests and employees at an exclusive tropical resort.",
        "genres": ["Drama", "Comedy", "Mystery"],
        "cast": ["Jennifer Coolidge", "F. Murray Abraham", "Aubrey Plaza"],
        "director": "Mike White",
        "rating": 8.1,
        "poster_url": "https://image.tmdb.org/t/p/w500/6hZ0MKNYBiFVNJDuWSdSXfg.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/original/wGMpOx5OBEYQeaJlqEbg0sGwAF2.jpg",
        "dna": {
            "pacing": 0.45,
            "tension_curve": [0.25, 0.4, 0.5, 0.65, 0.78, 0.85],
            "visual_style": "sun_drenched_satirical",
            "audio_mood": "comedic_foreboding",
            "thematic_tags": ["privilege", "tourism", "sexuality", "wealth", "existential dread"],
            "runtime_min": 50,
        },
    },
]

# Fill to 40 with additional titles...
CATALOG += [
    {
        "id": "tár-2022",
        "title": "Tár",
        "year": 2022,
        "kind": "film",
        "synopsis": "Set in the international world of classical music, the film centers on Lydia Tár, a fictional composer and conductor of a major German orchestra.",
        "genres": ["Drama"],
        "cast": ["Cate Blanchett", "Noémie Merlant", "Nina Hoss"],
        "director": "Todd Field",
        "rating": 7.5,
        "poster_url": "https://image.tmdb.org/t/p/w500/hFp0tGSIpBMKSXCMoFmfHKqBtSv.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/original/i3270QxiMFkRUJm3E0BiSWFq7dM.jpg",
        "dna": {"pacing": 0.3, "tension_curve": [0.2, 0.35, 0.5, 0.65, 0.75, 0.8], "visual_style": "austere_prestige", "audio_mood": "cerebral_classical", "thematic_tags": ["power", "cancel culture", "genius", "music", "manipulation"], "runtime_min": 158},
    },
    {
        "id": "silo-s1-2023",
        "title": "Silo",
        "year": 2023,
        "kind": "series",
        "synopsis": "In a ruined and toxic future, thousands live underground in a massive silo. Engineer Juliette learns forbidden truths about the outside world.",
        "genres": ["Sci-Fi", "Drama", "Thriller"],
        "cast": ["Rebecca Ferguson", "Tim Robbins", "Common"],
        "director": "Graham Yost",
        "rating": 8.1,
        "poster_url": "https://image.tmdb.org/t/p/w500/xy4JFAy0vMvvfHOuboq4OLa3XnI.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/original/4TzwDWpFSXaAMGqFWFJwKP0sEij.jpg",
        "dna": {"pacing": 0.5, "tension_curve": [0.3, 0.45, 0.6, 0.75, 0.85, 0.9], "visual_style": "gritty_industrial", "audio_mood": "ominous_claustrophobic", "thematic_tags": ["dystopia", "truth", "underground society", "rebellion", "secrets"], "runtime_min": 55},
    },
    {
        "id": "slow-horses-s1-2022",
        "title": "Slow Horses",
        "year": 2022,
        "kind": "series",
        "synopsis": "Slough House is MI5's dumping ground for disgraced spies. When a kidnapping case leads to unexpected places, these misfits must act.",
        "genres": ["Thriller", "Drama", "Crime"],
        "cast": ["Gary Oldman", "Jack Lowden", "Kristin Scott Thomas"],
        "director": "James Hawes",
        "rating": 8.2,
        "poster_url": "https://image.tmdb.org/t/p/w500/fKtYNLmZ0a3V0DsGiZ6RFBvIkjg.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/original/6HXSlPt01IkjlMd5IUCF8yikOCX.jpg",
        "dna": {"pacing": 0.52, "tension_curve": [0.3, 0.45, 0.6, 0.7, 0.8, 0.88], "visual_style": "grey_london_noir", "audio_mood": "sardonic_tense", "thematic_tags": ["espionage", "bureaucracy", "failure", "redemption", "British intelligence"], "runtime_min": 48},
    },
    {
        "id": "constellation-2024",
        "title": "Constellation",
        "year": 2024,
        "kind": "limited",
        "synopsis": "An astronaut returns home from a mission on the International Space Station to discover that key parts of her life seem to be missing.",
        "genres": ["Sci-Fi", "Thriller", "Mystery"],
        "cast": ["Noomi Rapace", "Jonathan Banks", "James D'Arcy"],
        "director": "Michelle MacLaren",
        "rating": 7.2,
        "poster_url": "https://image.tmdb.org/t/p/w500/lVlxNOBJi9RBGEFM3tHJbMsb5vk.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/original/lVlxNOBJi9RBGEFM3tHJbMsb5vk.jpg",
        "dna": {"pacing": 0.4, "tension_curve": [0.2, 0.4, 0.55, 0.7, 0.8, 0.85], "visual_style": "cold_clinical", "audio_mood": "disorienting_atmospheric", "thematic_tags": ["parallel realities", "trauma", "motherhood", "space", "identity loss"], "runtime_min": 55},
    },
    {
        "id": "intrusion-black-mirror-s6",
        "title": "Black Mirror",
        "year": 2011,
        "kind": "series",
        "synopsis": "An anthology series exploring a twisted, high-tech near-future where humanity's greatest innovations and darkest instincts collide.",
        "genres": ["Sci-Fi", "Drama", "Thriller"],
        "cast": ["Rory Kinnear", "Daniel Rigby", "Jodie Whittaker"],
        "director": "Charlie Brooker",
        "rating": 8.8,
        "poster_url": "https://image.tmdb.org/t/p/w500/5UaykH9KpBRjFgiJxB2SY7LdxIV.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/original/5UaykH9KpBRjFgiJxB2SY7LdxIV.jpg",
        "dna": {"pacing": 0.65, "tension_curve": [0.3, 0.55, 0.75, 0.85, 0.9, 0.8], "visual_style": "slick_dystopian", "audio_mood": "unsettling_modern", "thematic_tags": ["technology", "social media", "surveillance", "consciousness", "near future"], "runtime_min": 60},
    },
    {
        "id": "fallen-leaves-2023",
        "title": "Fallen Leaves",
        "year": 2023,
        "kind": "film",
        "synopsis": "Two lonely people in Helsinki try to find love despite life's obstacles.",
        "genres": ["Romance", "Drama", "Comedy"],
        "cast": ["Alma Pöysti", "Jussi Vatanen"],
        "director": "Aki Kaurismäki",
        "rating": 7.5,
        "poster_url": "https://image.tmdb.org/t/p/w500/8qBCDJvCG64hVJRaMDVSSiMDg0f.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/original/8qBCDJvCG64hVJRaMDVSSiMDg0f.jpg",
        "dna": {"pacing": 0.15, "tension_curve": [0.1, 0.15, 0.2, 0.25, 0.3, 0.35], "visual_style": "minimalist_nordic", "audio_mood": "melancholic_wry", "thematic_tags": ["loneliness", "simple pleasures", "working class", "love", "Helsinki"], "runtime_min": 81},
    },
    {
        "id": "true-detective-s4-2024",
        "title": "True Detective: Night Country",
        "year": 2024,
        "kind": "limited",
        "synopsis": "When the long winter night falls in Ennis, Alaska, the six men working at the Tsalal Arctic Research Station vanish without a trace.",
        "genres": ["Crime", "Mystery", "Drama"],
        "cast": ["Jodie Foster", "Kali Reis", "Fiona Shaw"],
        "director": "Issa López",
        "rating": 7.8,
        "poster_url": "https://image.tmdb.org/t/p/w500/drVNNJCbrCKBMrFJRfN4pJAFUCN.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/original/qXChEKcRARfxFKq7kHGo8jE9FdY.jpg",
        "dna": {"pacing": 0.38, "tension_curve": [0.25, 0.4, 0.55, 0.7, 0.82, 0.88], "visual_style": "arctic_noir", "audio_mood": "haunting_desolate", "thematic_tags": ["arctic mystery", "Indigenous culture", "corruption", "trauma", "darkness"], "runtime_min": 56},
    },
    {
        "id": "the-zone-of-interest-2023",
        "title": "The Zone of Interest",
        "year": 2023,
        "kind": "film",
        "synopsis": "The commandant of Auschwitz, Rudolf Höss, and his wife Hedwig strive to build a dream life for their family in a house next to the camp.",
        "genres": ["Drama", "History", "War"],
        "cast": ["Christian Friedel", "Sandra Hüller"],
        "director": "Jonathan Glazer",
        "rating": 7.4,
        "poster_url": "https://image.tmdb.org/t/p/w500/hUu9zyZmKuqqFHkTm3Xopk4TA6D.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/original/if8HW8JhW6X3tsZQV9aBtMTiXxR.jpg",
        "dna": {"pacing": 0.2, "tension_curve": [0.15, 0.2, 0.25, 0.3, 0.4, 0.5], "visual_style": "clinical_observational", "audio_mood": "horrifying_mundane", "thematic_tags": ["Holocaust", "evil banality", "domesticity", "silence", "complicity"], "runtime_min": 105},
    },
    {
        "id": "max-s1-2024",
        "title": "Pachinko",
        "year": 2022,
        "kind": "series",
        "synopsis": "An epic saga following a Korean immigrant family across four generations.",
        "genres": ["Drama", "Romance", "History"],
        "cast": ["Yuh-Jung Youn", "Lee Min-ho", "Jin Ha", "Minha Kim"],
        "director": "Soo Hugh",
        "rating": 8.4,
        "poster_url": "https://image.tmdb.org/t/p/w500/pAe1cVaGYGkgpGVFpBvEjMUZalh.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/original/9KPVLXOFZxnEDtD9lAQgLzRMNb5.jpg",
        "dna": {"pacing": 0.42, "tension_curve": [0.3, 0.5, 0.6, 0.7, 0.78, 0.82], "visual_style": "lush_epic", "audio_mood": "emotional_sweeping", "thematic_tags": ["generational trauma", "Korean diaspora", "survival", "identity", "history"], "runtime_min": 55},
    },
    {
        "id": "killers-flower-moon-2023",
        "title": "Killers of the Flower Moon",
        "year": 2023,
        "kind": "film",
        "synopsis": "Members of the Osage Nation are murdered under mysterious circumstances in 1920s Oklahoma, sparking a major FBI investigation.",
        "genres": ["Crime", "Drama", "History"],
        "cast": ["Leonardo DiCaprio", "Robert De Niro", "Lily Gladstone"],
        "director": "Martin Scorsese",
        "rating": 7.7,
        "poster_url": "https://image.tmdb.org/t/p/w500/dB6Krk806zeqd0YNp2ngQ9zXteH.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/original/1X7vow16X7CnCoexXh4H4F2yDJv.jpg",
        "dna": {"pacing": 0.35, "tension_curve": [0.2, 0.35, 0.5, 0.65, 0.75, 0.8], "visual_style": "epic_period", "audio_mood": "mournful_ominous", "thematic_tags": ["Native American history", "greed", "racism", "FBI origins", "Osage Nation"], "runtime_min": 206},
    },
]


async def run_seed():
    logging.basicConfig(level=logging.INFO)
    log.info("Starting NEXUS catalog seed (%d titles)", len(CATALOG))

    vs = get_vector_store()
    graph = get_graph()

    await vs.ensure_collection()
    await graph.ensure_schema()

    await vs.upsert_content(CATALOG)
    await graph.upsert_content(CATALOG)

    # Create similarity edges for a few well-known pairs
    pairs = [
        ("inception-2010", "dark-s1-2017", 0.78),
        ("inception-2010", "severance-s1-2022", 0.72),
        ("blade-runner-2049", "silo-s1-2023", 0.71),
        ("blade-runner-2049", "dark-s1-2017", 0.74),
        ("succession-s4-2023", "white-lotus-s2-2022", 0.68),
        ("succession-s4-2023", "slow-horses-s1-2022", 0.65),
        ("oppenheimer-2023", "tár-2022", 0.62),
        ("parasite-2019", "the-menu-2022", 0.71),
        ("severance-s1-2022", "silo-s1-2023", 0.75),
        ("the-last-of-us-s1-2023", "station-eleven-2021", 0.73),
    ]
    for a, b, score in pairs:
        await graph.create_similarity_edge(a, b, score)

    count = await vs.count()
    stats = await graph.graph_stats()
    log.info("Seed complete. Vector store: %d docs. Graph: %s", count, stats)


if __name__ == "__main__":
    asyncio.run(run_seed())


async def run_seed_with_tmdb():
    """Seed with TMDB enrichment if API key is available, else use embedded metadata."""
    logging.basicConfig(level=logging.INFO)
    from catalog.tmdb import get_tmdb_client

    client = get_tmdb_client()
    catalog = CATALOG

    if client:
        log.info("TMDB key found — enriching %d titles with live metadata...", len(catalog))
        try:
            catalog = await client.enrich_catalog(CATALOG, concurrency=3)
            log.info("TMDB enrichment complete")
        except Exception as e:
            log.warning("TMDB enrichment failed (%s) — using embedded metadata", e)
        finally:
            await client.close()
    else:
        log.info("No TMDB key — using embedded metadata (set TMDB_API_KEY for live posters)")

    vs = get_vector_store()
    graph = get_graph()
    await vs.ensure_collection()
    await graph.ensure_schema()
    await vs.upsert_content(catalog)
    await graph.upsert_content(catalog)

    pairs = [
        ("inception-2010", "dark-s1-2017", 0.78),
        ("inception-2010", "severance-s1-2022", 0.72),
        ("blade-runner-2049", "silo-s1-2023", 0.71),
        ("blade-runner-2049", "dark-s1-2017", 0.74),
        ("succession-s4-2023", "white-lotus-s2-2022", 0.68),
        ("oppenheimer-2023", "tár-2022", 0.62),
        ("parasite-2019", "the-menu-2022", 0.71),
        ("severance-s1-2022", "silo-s1-2023", 0.75),
        ("the-last-of-us-s1-2023", "station-eleven-2021", 0.73),
    ]
    for a, b, score in pairs:
        await graph.create_similarity_edge(a, b, score)

    count = await vs.count()
    stats = await graph.graph_stats()
    log.info("Seed complete. Vectors: %d. Graph: %s", count, stats)


if __name__ == "__main__":
    asyncio.run(run_seed_with_tmdb())
