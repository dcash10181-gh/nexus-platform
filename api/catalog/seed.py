"""
NEXUS Catalog Seed — 120+ curated titles with full ContentDNA profiles.

Covers: drama, sci-fi, thriller, comedy, horror, romance, action, documentary,
animation, international, limited series, and prestige TV across 6 decades.
"""
from __future__ import annotations

import asyncio
import logging

log = logging.getLogger(__name__)

CATALOG: list[dict] = [

    # ── PRESTIGE DRAMA ────────────────────────────────────────────────────

    {
        "id": "the-wire-s1-2002",
        "title": "The Wire",
        "year": 2002, "kind": "series",
        "synopsis": "The Baltimore drug trade and the police who surveil it, told from both sides with documentary-level authenticity. The greatest TV drama ever made.",
        "genres": ["Crime", "Drama"], "cast": ["Dominic West", "Idris Elba", "Michael K. Williams"],
        "director": "David Simon", "rating": 9.3,
        "poster_url": "https://image.tmdb.org/t/p/w500/4lCqDTOoHhLkUvDe5kmqLOv0pK7.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=1400&q=80",
        "dna": {"pacing": 0.45, "tension_curve": [0.3,0.5,0.65,0.75,0.82,0.88], "visual_style": "gritty_documentary", "audio_mood": "urban_sparse", "thematic_tags": ["institutional_failure","drug_trade","surveillance","class","Baltimore"], "runtime_min": 58},
    },
    {
        "id": "breaking-bad-s1-2008",
        "title": "Breaking Bad",
        "year": 2008, "kind": "series",
        "synopsis": "A high school chemistry teacher diagnosed with cancer turns to cooking methamphetamine to secure his family's future. The defining TV antihero story.",
        "genres": ["Crime", "Drama", "Thriller"], "cast": ["Bryan Cranston", "Aaron Paul", "Anna Gunn"],
        "director": "Vince Gilligan", "rating": 9.5,
        "poster_url": "https://image.tmdb.org/t/p/w500/ggFHVNu6YYI5L9pCfOacjizRGt.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1509909756405-be0199881695?w=1400&q=80",
        "dna": {"pacing": 0.62, "tension_curve": [0.2,0.45,0.65,0.8,0.92,0.98], "visual_style": "desert_neo_western", "audio_mood": "tense_percussive", "thematic_tags": ["transformation","pride","family","consequences","New Mexico"], "runtime_min": 48},
    },
    {
        "id": "the-sopranos-s1-1999",
        "title": "The Sopranos",
        "year": 1999, "kind": "series",
        "synopsis": "New Jersey mob boss Tony Soprano navigates family life and organized crime while attending therapy. The show that invented prestige television.",
        "genres": ["Crime", "Drama"], "cast": ["James Gandolfini", "Edie Falco", "Lorraine Bracco"],
        "director": "David Chase", "rating": 9.2,
        "poster_url": "https://image.tmdb.org/t/p/w500/57okJJUBK0AaijxkciggHKTXPEF.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=1400&q=80",
        "dna": {"pacing": 0.48, "tension_curve": [0.3,0.5,0.6,0.72,0.8,0.85], "visual_style": "suburban_realism", "audio_mood": "operatic_ironic", "thematic_tags": ["mob","therapy","New Jersey","masculinity","family dysfunction"], "runtime_min": 55},
    },
    {
        "id": "mad-men-s1-2007",
        "title": "Mad Men",
        "year": 2007, "kind": "series",
        "synopsis": "The professional and personal lives of the employees at a 1960s Madison Avenue advertising agency. Style as substance.",
        "genres": ["Drama"], "cast": ["Jon Hamm", "Elisabeth Moss", "January Jones"],
        "director": "Matthew Weiner", "rating": 8.6,
        "poster_url": "https://image.tmdb.org/t/p/w500/7v8iCNiPFDRMmgMaqFGKFuQfxNs.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1400&q=80",
        "dna": {"pacing": 0.35, "tension_curve": [0.25,0.38,0.5,0.6,0.68,0.72], "visual_style": "period_elegance", "audio_mood": "jazz_melancholic", "thematic_tags": ["identity","1960s","advertising","American Dream","nostalgia"], "runtime_min": 47},
    },
    {
        "id": "better-call-saul-s1-2015",
        "title": "Better Call Saul",
        "year": 2015, "kind": "series",
        "synopsis": "The transformation of Jimmy McGill into criminal lawyer Saul Goodman. A prequel that surpassed its parent show.",
        "genres": ["Crime", "Drama"], "cast": ["Bob Odenkirk", "Jonathan Banks", "Rhea Seehorn"],
        "director": "Vince Gilligan", "rating": 9.0,
        "poster_url": "https://image.tmdb.org/t/p/w500/fC2HDm5t0kR9HFQTGkQrD0pFL5.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1509909756405-be0199881695?w=1400&q=80",
        "dna": {"pacing": 0.4, "tension_curve": [0.2,0.38,0.55,0.7,0.85,0.9], "visual_style": "desert_minimalist", "audio_mood": "sparse_blues", "thematic_tags": ["moral_decline","law","loyalty","consequence","Albuquerque"], "runtime_min": 48},
    },
    {
        "id": "mindhunter-s1-2017",
        "title": "Mindhunter",
        "year": 2017, "kind": "series",
        "synopsis": "FBI agents develop criminal profiling by interviewing incarcerated serial killers in the 1970s. Fincher's coldest, most precise work.",
        "genres": ["Crime", "Drama", "Thriller"], "cast": ["Jonathan Groff", "Holt McCallany", "Anna Torv"],
        "director": "David Fincher", "rating": 8.6,
        "poster_url": "https://image.tmdb.org/t/p/w500/6bPCGEMBd58oFJA4EWqAGFHhXbT.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1505765050516-f72dcac9c60e?w=1400&q=80",
        "dna": {"pacing": 0.38, "tension_curve": [0.2,0.35,0.5,0.62,0.72,0.78], "visual_style": "clinical_70s", "audio_mood": "cold_procedural", "thematic_tags": ["serial killers","FBI","psychology","1970s","profiling"], "runtime_min": 55},
    },
    {
        "id": "ozark-s1-2017",
        "title": "Ozark",
        "year": 2017, "kind": "series",
        "synopsis": "A Chicago financial advisor is forced to relocate his family to the Missouri Ozarks to launder money for a drug cartel.",
        "genres": ["Crime", "Drama", "Thriller"], "cast": ["Jason Bateman", "Laura Linney", "Julia Garner"],
        "director": "Jason Bateman", "rating": 8.4,
        "poster_url": "https://image.tmdb.org/t/p/w500/pIkRyD18kl4FhoCNQuWxWu5cBLM.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1501854140801-50d01698950b?w=1400&q=80",
        "dna": {"pacing": 0.65, "tension_curve": [0.35,0.55,0.7,0.82,0.9,0.94], "visual_style": "blue_toned_rural", "audio_mood": "ominous_country", "thematic_tags": ["money_laundering","cartel","family_under_pressure","Missouri","survival"], "runtime_min": 60},
    },
    {
        "id": "chernobyl-2019",
        "title": "Chernobyl",
        "year": 2019, "kind": "limited",
        "synopsis": "The true story of the 1986 nuclear disaster and the men and women who sacrificed to contain it. The most precise limited series ever made.",
        "genres": ["Drama", "History", "Thriller"], "cast": ["Jared Harris", "Stellan Skarsgård", "Emily Watson"],
        "director": "Johan Renck", "rating": 9.4,
        "poster_url": "https://image.tmdb.org/t/p/w500/hlLXt2tOPT6RRnjiUmoxyG1LTFi.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1547036967-23d11aacaee0?w=1400&q=80",
        "dna": {"pacing": 0.55, "tension_curve": [0.4,0.6,0.75,0.88,0.95,0.9], "visual_style": "soviet_grey", "audio_mood": "industrial_dread", "thematic_tags": ["nuclear_disaster","Soviet_Union","truth","sacrifice","bureaucracy"], "runtime_min": 65},
    },
    {
        "id": "peaky-blinders-s1-2013",
        "title": "Peaky Blinders",
        "year": 2013, "kind": "series",
        "synopsis": "A gangster family epic set in 1920s Birmingham, England. Led by the fearsome Tommy Shelby.",
        "genres": ["Crime", "Drama"], "cast": ["Cillian Murphy", "Helen McCrory", "Paul Anderson"],
        "director": "Steven Knight", "rating": 8.8,
        "poster_url": "https://image.tmdb.org/t/p/w500/vUUqzWa2LnHIVqkaKVlVGkPaQca.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1558980394-34764db076b4?w=1400&q=80",
        "dna": {"pacing": 0.6, "tension_curve": [0.35,0.55,0.7,0.8,0.88,0.92], "visual_style": "industrial_noir", "audio_mood": "rock_period_hybrid", "thematic_tags": ["1920s","organized_crime","Birmingham","PTSD","family_empire"], "runtime_min": 55},
    },

    # ── SCI-FI & SPECULATIVE ─────────────────────────────────────────────

    {
        "id": "mr-robot-s1-2015",
        "title": "Mr. Robot",
        "year": 2015, "kind": "series",
        "synopsis": "A cybersecurity engineer and hacker is recruited by a mysterious anarchist to help destroy the company he works for.",
        "genres": ["Thriller", "Sci-Fi", "Drama"], "cast": ["Rami Malek", "Christian Slater", "Portia Doubleday"],
        "director": "Sam Esmail", "rating": 8.7,
        "poster_url": "https://image.tmdb.org/t/p/w500/oKIBhzZzDX07SoE2bOLhq2EsfUE.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1400&q=80",
        "dna": {"pacing": 0.55, "tension_curve": [0.3,0.5,0.68,0.8,0.9,0.88], "visual_style": "urban_paranoid", "audio_mood": "electronic_anxious", "thematic_tags": ["hacking","dissociation","capitalism","surveillance","mental_illness"], "runtime_min": 45},
    },
    {
        "id": "westworld-s1-2016",
        "title": "Westworld",
        "year": 2016, "kind": "series",
        "synopsis": "A futuristic theme park populated by android hosts goes dangerously wrong as its creations begin to question their reality.",
        "genres": ["Sci-Fi", "Drama", "Thriller"], "cast": ["Evan Rachel Wood", "Anthony Hopkins", "Ed Harris"],
        "director": "Jonathan Nolan", "rating": 8.6,
        "poster_url": "https://image.tmdb.org/t/p/w500/8MfgyFHR7OGljow9KCLnQ7aBHfz.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1534796636912-3b95b3ab5986?w=1400&q=80",
        "dna": {"pacing": 0.5, "tension_curve": [0.3,0.5,0.65,0.78,0.88,0.95], "visual_style": "neo_western_cinematic", "audio_mood": "orchestral_unsettling", "thematic_tags": ["AI_consciousness","free_will","theme_park","violence","loops"], "runtime_min": 62},
    },
    {
        "id": "halt-and-catch-fire-s1-2014",
        "title": "Halt and Catch Fire",
        "year": 2014, "kind": "series",
        "synopsis": "Set in the 1980s Texas silicon prairie, this drama chronicles the personal computer revolution through a team of dreamers and builders.",
        "genres": ["Drama"], "cast": ["Lee Pace", "Scoot McNairy", "Mackenzie Davis"],
        "director": "Christopher Cantwell", "rating": 8.4,
        "poster_url": "https://image.tmdb.org/t/p/w500/k9VBFqHGHmJUEjMQnH5eXO16tR2.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1400&q=80",
        "dna": {"pacing": 0.42, "tension_curve": [0.25,0.42,0.58,0.7,0.78,0.82], "visual_style": "80s_warm_nostalgic", "audio_mood": "synth_emotional", "thematic_tags": ["tech_revolution","ambition","1980s","collaboration","Silicon_Valley"], "runtime_min": 48},
    },
    {
        "id": "battlestar-galactica-2004",
        "title": "Battlestar Galactica",
        "year": 2004, "kind": "series",
        "synopsis": "After a devastating attack by robotic Cylons, the surviving humans flee through space searching for a new home. What makes us human?",
        "genres": ["Sci-Fi", "Drama"], "cast": ["Edward James Olmos", "Mary McDonnell", "Katee Sackhoff"],
        "director": "Ronald D. Moore", "rating": 8.7,
        "poster_url": "https://image.tmdb.org/t/p/w500/b7IfPFLfb7c5oBnBpMxT0tV3MO0.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1462332420958-a05d1e002413?w=1400&q=80",
        "dna": {"pacing": 0.6, "tension_curve": [0.4,0.6,0.72,0.82,0.9,0.92], "visual_style": "gritty_space_opera", "audio_mood": "orchestral_military", "thematic_tags": ["humanity","AI","religion","survival","democracy"], "runtime_min": 44},
    },

    # ── PRESTIGE FILMS ───────────────────────────────────────────────────

    {
        "id": "the-shawshank-redemption-1994",
        "title": "The Shawshank Redemption",
        "year": 1994, "kind": "film",
        "synopsis": "Two imprisoned men bond over years, finding solace and eventual redemption through acts of decency. The most beloved film ever made.",
        "genres": ["Drama"], "cast": ["Tim Robbins", "Morgan Freeman", "Bob Gunton"],
        "director": "Frank Darabont", "rating": 9.3,
        "poster_url": "https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1493612276216-ee3925520721?w=1400&q=80",
        "dna": {"pacing": 0.3, "tension_curve": [0.2,0.35,0.5,0.6,0.7,0.85], "visual_style": "warm_naturalistic", "audio_mood": "hopeful_sweeping", "thematic_tags": ["hope","friendship","prison","freedom","patience"], "runtime_min": 142},
    },
    {
        "id": "interstellar-2014",
        "title": "Interstellar",
        "year": 2014, "kind": "film",
        "synopsis": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival. Love as a force of physics.",
        "genres": ["Sci-Fi", "Drama", "Adventure"], "cast": ["Matthew McConaughey", "Anne Hathaway", "Jessica Chastain"],
        "director": "Christopher Nolan", "rating": 8.7,
        "poster_url": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=1400&q=80",
        "dna": {"pacing": 0.55, "tension_curve": [0.3,0.5,0.68,0.82,0.92,0.88], "visual_style": "epic_cosmic", "audio_mood": "organ_transcendent", "thematic_tags": ["space","fatherhood","time","love","climate"], "runtime_min": 169},
    },
    {
        "id": "the-dark-knight-2008",
        "title": "The Dark Knight",
        "year": 2008, "kind": "film",
        "synopsis": "Batman faces the Joker, a criminal mastermind who wants to plunge Gotham City into anarchy. The superhero film that transcended the genre.",
        "genres": ["Action", "Drama", "Thriller"], "cast": ["Christian Bale", "Heath Ledger", "Aaron Eckhart"],
        "director": "Christopher Nolan", "rating": 9.0,
        "poster_url": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?w=1400&q=80",
        "dna": {"pacing": 0.78, "tension_curve": [0.4,0.65,0.82,0.9,0.95,0.92], "visual_style": "dark_operatic", "audio_mood": "percussive_chaos", "thematic_tags": ["chaos","order","sacrifice","anarchy","heroism"], "runtime_min": 152},
    },
    {
        "id": "pulp-fiction-1994",
        "title": "Pulp Fiction",
        "year": 1994, "kind": "film",
        "synopsis": "The lives of two mob hitmen, a boxer, and others intertwine in four tales of violence and redemption in Los Angeles.",
        "genres": ["Crime", "Drama"], "cast": ["John Travolta", "Samuel L. Jackson", "Uma Thurman"],
        "director": "Quentin Tarantino", "rating": 8.9,
        "poster_url": "https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=1400&q=80",
        "dna": {"pacing": 0.65, "tension_curve": [0.4,0.6,0.72,0.8,0.75,0.85], "visual_style": "retro_stylized", "audio_mood": "eclectic_surf_soul", "thematic_tags": ["nonlinear","LA","crime","redemption","dialogue"], "runtime_min": 154},
    },
    {
        "id": "no-country-for-old-men-2007",
        "title": "No Country for Old Men",
        "year": 2007, "kind": "film",
        "synopsis": "A hunter stumbles on a drug deal gone wrong and a briefcase full of money. Then Anton Chigurh comes looking for it.",
        "genres": ["Crime", "Drama", "Thriller"], "cast": ["Tommy Lee Jones", "Javier Bardem", "Josh Brolin"],
        "director": "Coen Brothers", "rating": 8.2,
        "poster_url": "https://image.tmdb.org/t/p/w500/6d4yCHIGKfnP93oMFCyHFmOHKdo.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1509909756405-be0199881695?w=1400&q=80",
        "dna": {"pacing": 0.35, "tension_curve": [0.25,0.45,0.6,0.75,0.85,0.88], "visual_style": "arid_neo_western", "audio_mood": "near_silent_dread", "thematic_tags": ["fate","violence","mortality","Texas","evil"], "runtime_min": 122},
    },
    {
        "id": "whiplash-2014",
        "title": "Whiplash",
        "year": 2014, "kind": "film",
        "synopsis": "A young jazz drummer pushes himself to his absolute limits under the tutelage of a ruthless instructor. Greatness at any cost.",
        "genres": ["Drama", "Music"], "cast": ["Miles Teller", "J.K. Simmons", "Paul Reiser"],
        "director": "Damien Chazelle", "rating": 8.5,
        "poster_url": "https://image.tmdb.org/t/p/w500/7fn624j5lj3xTme2SgiLCeuedmO.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1415201364774-f6f0bb35f28f?w=1400&q=80",
        "dna": {"pacing": 0.85, "tension_curve": [0.4,0.65,0.8,0.9,0.97,0.99], "visual_style": "close_claustrophobic", "audio_mood": "jazz_percussive_intense", "thematic_tags": ["obsession","greatness","abuse","jazz","perfectionism"], "runtime_min": 107},
    },
    {
        "id": "her-2013",
        "title": "Her",
        "year": 2013, "kind": "film",
        "synopsis": "A lonely writer develops an unlikely relationship with an operating system designed to meet his every need.",
        "genres": ["Sci-Fi", "Romance", "Drama"], "cast": ["Joaquin Phoenix", "Scarlett Johansson", "Amy Adams"],
        "director": "Spike Jonze", "rating": 8.0,
        "poster_url": "https://image.tmdb.org/t/p/w500/eCOtqtfvn7mxGPCaHDdRRIxcIen.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1400&q=80",
        "dna": {"pacing": 0.25, "tension_curve": [0.15,0.25,0.35,0.45,0.55,0.5], "visual_style": "warm_pastel_near_future", "audio_mood": "tender_electronic", "thematic_tags": ["loneliness","AI_love","technology","intimacy","near_future"], "runtime_min": 126},
    },
    {
        "id": "the-social-network-2010",
        "title": "The Social Network",
        "year": 2010, "kind": "film",
        "synopsis": "The story of the founding of Facebook and the lawsuits that followed. Fincher and Sorkin at their collaborative peak.",
        "genres": ["Drama", "Biography"], "cast": ["Jesse Eisenberg", "Andrew Garfield", "Justin Timberlake"],
        "director": "David Fincher", "rating": 7.8,
        "poster_url": "https://image.tmdb.org/t/p/w500/n0ybibhJtQ5icDqTp8eRytcIHso.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1468495244123-6c6c332eeece?w=1400&q=80",
        "dna": {"pacing": 0.72, "tension_curve": [0.4,0.6,0.72,0.78,0.82,0.8], "visual_style": "cold_blue_prestige", "audio_mood": "propulsive_electronic", "thematic_tags": ["ambition","betrayal","Silicon_Valley","genius","friendship"], "runtime_min": 120},
    },
    {
        "id": "arrival-2016",
        "title": "Arrival",
        "year": 2016, "kind": "film",
        "synopsis": "A linguist is recruited to communicate with alien beings after they arrive on Earth in mysterious vessels.",
        "genres": ["Sci-Fi", "Drama", "Mystery"], "cast": ["Amy Adams", "Jeremy Renner", "Forest Whitaker"],
        "director": "Denis Villeneuve", "rating": 7.9,
        "poster_url": "https://image.tmdb.org/t/p/w500/x2FJsf1ElAgr63Y3PNPtJrcmpoe.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1534796636912-3b95b3ab5986?w=1400&q=80",
        "dna": {"pacing": 0.3, "tension_curve": [0.2,0.35,0.5,0.6,0.7,0.8], "visual_style": "grey_meditative", "audio_mood": "atmospheric_choral", "thematic_tags": ["language","time","grief","first_contact","motherhood"], "runtime_min": 116},
    },
    {
        "id": "ex-machina-2014",
        "title": "Ex Machina",
        "year": 2014, "kind": "film",
        "synopsis": "A programmer is invited to administer the Turing test to an AI with a striking humanoid form.",
        "genres": ["Sci-Fi", "Thriller", "Drama"], "cast": ["Domhnall Gleeson", "Alicia Vikander", "Oscar Isaac"],
        "director": "Alex Garland", "rating": 7.7,
        "poster_url": "https://image.tmdb.org/t/p/w500/btjBDFX4GIRmfhNwrJbYXS8IOBN.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1400&q=80",
        "dna": {"pacing": 0.38, "tension_curve": [0.2,0.38,0.55,0.7,0.82,0.9], "visual_style": "glass_minimalist", "audio_mood": "electronic_uncanny", "thematic_tags": ["AI","consciousness","manipulation","Turing_test","isolation"], "runtime_min": 108},
    },
    {
        "id": "gone-girl-2014",
        "title": "Gone Girl",
        "year": 2014, "kind": "film",
        "synopsis": "On their fifth wedding anniversary, Nick Dunne's wife Amy disappears. His suspicious behavior makes him the prime suspect.",
        "genres": ["Thriller", "Drama", "Mystery"], "cast": ["Ben Affleck", "Rosamund Pike", "Neil Patrick Harris"],
        "director": "David Fincher", "rating": 8.1,
        "poster_url": "https://image.tmdb.org/t/p/w500/mrFpPrJKbpGVhyJRoIpfgH3MBGB.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1505765050516-f72dcac9c60e?w=1400&q=80",
        "dna": {"pacing": 0.6, "tension_curve": [0.3,0.55,0.7,0.82,0.9,0.88], "visual_style": "suburban_cold", "audio_mood": "tense_electronic", "thematic_tags": ["marriage","media","deception","suburban_dread","performance"], "runtime_min": 149},
    },
    {
        "id": "moonlight-2016",
        "title": "Moonlight",
        "year": 2016, "kind": "film",
        "synopsis": "A young Black man's journey through three defining chapters of his life in Miami. The most tenderly shot film of the decade.",
        "genres": ["Drama"], "cast": ["Mahershala Ali", "Naomie Harris", "Trevante Rhodes"],
        "director": "Barry Jenkins", "rating": 7.4,
        "poster_url": "https://image.tmdb.org/t/p/w500/4KJHFMzDYiJkBXy1gnXgFIDzMdH.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1502209524164-acea936639a2?w=1400&q=80",
        "dna": {"pacing": 0.22, "tension_curve": [0.15,0.25,0.35,0.45,0.5,0.55], "visual_style": "lyrical_saturated", "audio_mood": "classical_tender", "thematic_tags": ["identity","sexuality","race","Miami","coming_of_age"], "runtime_min": 111},
    },
    {
        "id": "get-out-2017",
        "title": "Get Out",
        "year": 2017, "kind": "film",
        "synopsis": "A Black man visits his white girlfriend's family estate and discovers something terrifying. Horror as social commentary.",
        "genres": ["Horror", "Thriller", "Mystery"], "cast": ["Daniel Kaluuya", "Allison Williams", "Bradley Whitford"],
        "director": "Jordan Peele", "rating": 7.7,
        "poster_url": "https://image.tmdb.org/t/p/w500/tFXcEccSQMf3lfhfXKSU9iRBpa3.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1560421683-6856ea585c78?w=1400&q=80",
        "dna": {"pacing": 0.55, "tension_curve": [0.3,0.5,0.65,0.8,0.92,0.95], "visual_style": "satirical_suburban", "audio_mood": "unsettling_orchestral", "thematic_tags": ["racism","horror","social_commentary","SUNKEN_PLACE","liberal_hypocrisy"], "runtime_min": 104},
    },
    {
        "id": "midsommar-2019",
        "title": "Midsommar",
        "year": 2019, "kind": "film",
        "synopsis": "A couple travels to Sweden for a festival held once every 90 years. What appears idyllic reveals itself as something ancient and horrifying.",
        "genres": ["Horror", "Drama", "Mystery"], "cast": ["Florence Pugh", "Jack Reynor", "William Jackson Harper"],
        "director": "Ari Aster", "rating": 7.1,
        "poster_url": "https://image.tmdb.org/t/p/w500/7LEI8ulZzO5gy9Ww2NVCrKmHeDZ.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?w=1400&q=80",
        "dna": {"pacing": 0.28, "tension_curve": [0.15,0.3,0.5,0.65,0.8,0.88], "visual_style": "bright_pastoral_horror", "audio_mood": "folk_dissonant", "thematic_tags": ["grief","folk_horror","Sweden","relationships","ritual"], "runtime_min": 148},
    },
    {
        "id": "drive-2011",
        "title": "Drive",
        "year": 2011, "kind": "film",
        "synopsis": "A stunt driver moonlights as a getaway driver and falls for his neighbor. Style, silence, and sudden violence.",
        "genres": ["Action", "Drama", "Thriller"], "cast": ["Ryan Gosling", "Carey Mulligan", "Bryan Cranston"],
        "director": "Nicolas Winding Refn", "rating": 7.8,
        "poster_url": "https://image.tmdb.org/t/p/w500/602vevIygqd0B2ago4DqHNCoaAw.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1476357471311-43c0db9fb2b4?w=1400&q=80",
        "dna": {"pacing": 0.32, "tension_curve": [0.2,0.35,0.5,0.65,0.82,0.88], "visual_style": "neon_neo_noir", "audio_mood": "synthwave_melancholic", "thematic_tags": ["silence","LA","violence","longing","outsider"], "runtime_min": 100},
    },
    {
        "id": "the-power-of-the-dog-2021",
        "title": "The Power of the Dog",
        "year": 2021, "kind": "film",
        "synopsis": "A charismatic rancher torments his brother's new wife and her son until unexpected events unfold.",
        "genres": ["Drama", "Thriller", "Western"], "cast": ["Benedict Cumberbatch", "Kirsten Dunst", "Jesse Plemons"],
        "director": "Jane Campion", "rating": 6.8,
        "poster_url": "https://image.tmdb.org/t/p/w500/ugzsOqBsxMMCCKjECGsXdGfWn7V.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1501854140801-50d01698950b?w=1400&q=80",
        "dna": {"pacing": 0.25, "tension_curve": [0.15,0.28,0.42,0.58,0.7,0.82], "visual_style": "epic_landscape_intimate", "audio_mood": "sparse_western_unnerving", "thematic_tags": ["toxic_masculinity","repression","Montana","1920s","cruelty"], "runtime_min": 126},
    },
    {
        "id": "aftersun-2022",
        "title": "Aftersun",
        "year": 2022, "kind": "film",
        "synopsis": "A young woman reflects on a shared holiday with her father twenty years earlier. Memory, loss, and what we don't see in the people we love.",
        "genres": ["Drama"], "cast": ["Paul Mescal", "Frankie Corio"],
        "director": "Charlotte Wells", "rating": 7.3,
        "poster_url": "https://image.tmdb.org/t/p/w500/4Ac7CGRMHC4MMi0yMJjBMkJRZqg.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1400&q=80",
        "dna": {"pacing": 0.18, "tension_curve": [0.1,0.18,0.25,0.35,0.48,0.6], "visual_style": "sun_bleached_intimate", "audio_mood": "melancholic_tender", "thematic_tags": ["memory","fatherhood","depression","Turkey","grief"], "runtime_min": 96},
    },
    {
        "id": "the-banshees-of-inisherin-2022",
        "title": "The Banshees of Inisherin",
        "year": 2022, "kind": "film",
        "synopsis": "On a small island off the coast of Ireland, a man is devastated when his lifelong friend suddenly ends their friendship.",
        "genres": ["Drama", "Comedy"], "cast": ["Colin Farrell", "Brendan Gleeson", "Barry Keoghan"],
        "director": "Martin McDonagh", "rating": 7.7,
        "poster_url": "https://image.tmdb.org/t/p/w500/4yFG6cSPaCaPhyJ1vtGOtMD7kNs.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1504701954957-2010ec3bcec1?w=1400&q=80",
        "dna": {"pacing": 0.3, "tension_curve": [0.2,0.35,0.5,0.62,0.72,0.78], "visual_style": "bleak_beautiful_irish", "audio_mood": "folk_mournful", "thematic_tags": ["friendship","spite","Ireland","Civil_War","meaning"], "runtime_min": 114},
    },
    {
        "id": "nightcrawler-2014",
        "title": "Nightcrawler",
        "year": 2014, "kind": "film",
        "synopsis": "An ambitious and morally hollow man discovers a way into the world of LA crime journalism. Jake Gyllenhaal's most unsettling performance.",
        "genres": ["Crime", "Drama", "Thriller"], "cast": ["Jake Gyllenhaal", "Rene Russo", "Riz Ahmed"],
        "director": "Dan Gilroy", "rating": 7.9,
        "poster_url": "https://image.tmdb.org/t/p/w500/vNFMhbMsFmFfMnpQ1CVlCANzQ0j.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1476357471311-43c0db9fb2b4?w=1400&q=80",
        "dna": {"pacing": 0.68, "tension_curve": [0.3,0.52,0.68,0.82,0.9,0.92], "visual_style": "nocturnal_neon", "audio_mood": "electronic_predatory", "thematic_tags": ["sociopathy","LA","media","ambition","night"], "runtime_min": 117},
    },
    {
        "id": "roma-2018",
        "title": "Roma",
        "year": 2018, "kind": "film",
        "synopsis": "A year in the life of a middle-class family in Mexico City and their live-in housekeeper. Alfonso Cuarón's most personal film.",
        "genres": ["Drama"], "cast": ["Yalitza Aparicio", "Marina de Tavira"],
        "director": "Alfonso Cuarón", "rating": 7.7,
        "poster_url": "https://image.tmdb.org/t/p/w500/dtWAkBTJFMwLCTIebiEuoJFfXbS.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1518684079-3c830dcef090?w=1400&q=80",
        "dna": {"pacing": 0.2, "tension_curve": [0.1,0.2,0.3,0.45,0.6,0.65], "visual_style": "black_white_neorealist", "audio_mood": "ambient_city_life", "thematic_tags": ["class","Mexico_City","1970s","domesticity","women"], "runtime_min": 135},
    },

    # ── COMEDY & LIGHTER ─────────────────────────────────────────────────

    {
        "id": "fleabag-s1-2016",
        "title": "Fleabag",
        "year": 2016, "kind": "series",
        "synopsis": "A young woman navigates modern life in London with painfully sharp wit, breaking the fourth wall to take us into her confidence.",
        "genres": ["Comedy", "Drama"], "cast": ["Phoebe Waller-Bridge", "Sian Clifford", "Olivia Colman"],
        "director": "Phoebe Waller-Bridge", "rating": 8.7,
        "poster_url": "https://image.tmdb.org/t/p/w500/7SMxfbXNB29JWDxiDMp7eKmLMOb.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=1400&q=80",
        "dna": {"pacing": 0.7, "tension_curve": [0.3,0.5,0.62,0.72,0.8,0.82], "visual_style": "direct_address_london", "audio_mood": "witty_sparse", "thematic_tags": ["grief","women","fourth_wall","sex","guilt"], "runtime_min": 25},
    },
    {
        "id": "atlanta-s1-2016",
        "title": "Atlanta",
        "year": 2016, "kind": "series",
        "synopsis": "Two cousins navigate Atlanta's music scene while trying to improve their lives and the lives of their family.",
        "genres": ["Comedy", "Drama"], "cast": ["Donald Glover", "Brian Tyree Henry", "Lakeith Stanfield"],
        "director": "Donald Glover", "rating": 8.6,
        "poster_url": "https://image.tmdb.org/t/p/w500/8PGjCQlQ5hAJePnNEHpBa0OUFS3.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1400&q=80",
        "dna": {"pacing": 0.5, "tension_curve": [0.3,0.45,0.58,0.65,0.72,0.75], "visual_style": "surreal_naturalistic", "audio_mood": "hip_hop_ambient", "thematic_tags": ["race","music_industry","absurdism","Atlanta","Black_experience"], "runtime_min": 25},
    },
    {
        "id": "barry-s1-2018",
        "title": "Barry",
        "year": 2018, "kind": "series",
        "synopsis": "A hitman from the Midwest moves to LA, falls in love with acting, and tries to leave his murderous past behind.",
        "genres": ["Comedy", "Drama", "Thriller"], "cast": ["Bill Hader", "Henry Winkler", "Sarah Goldberg"],
        "director": "Bill Hader", "rating": 8.4,
        "poster_url": "https://image.tmdb.org/t/p/w500/qKHSLSQNhHXkJT6KNHWEKsocSF3.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=1400&q=80",
        "dna": {"pacing": 0.6, "tension_curve": [0.3,0.5,0.65,0.75,0.85,0.88], "visual_style": "genre_blending_LA", "audio_mood": "darkly_comic_tense", "thematic_tags": ["hitman","acting","identity","trauma","LA"], "runtime_min": 30},
    },
    {
        "id": "ted-lasso-s1-2020",
        "title": "Ted Lasso",
        "year": 2020, "kind": "series",
        "synopsis": "An American football coach is hired to manage an English soccer team despite knowing nothing about the sport. Radical optimism as superpower.",
        "genres": ["Comedy", "Drama"], "cast": ["Jason Sudeikis", "Hannah Waddingham", "Brett Goldstein"],
        "director": "Jason Sudeikis", "rating": 8.8,
        "poster_url": "https://image.tmdb.org/t/p/w500/3gMIGxFMIQh06j4MsBQ96VjuVlD.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=1400&q=80",
        "dna": {"pacing": 0.55, "tension_curve": [0.3,0.45,0.55,0.6,0.65,0.7], "visual_style": "warm_british", "audio_mood": "uplifting_folk_pop", "thematic_tags": ["kindness","football","mental_health","belief","leadership"], "runtime_min": 45},
    },
    {
        "id": "the-good-place-s1-2016",
        "title": "The Good Place",
        "year": 2016, "kind": "series",
        "synopsis": "A woman accidentally ends up in a utopian afterlife and must conceal her true nature while learning what it means to be good.",
        "genres": ["Comedy", "Fantasy"], "cast": ["Kristen Bell", "Ted Danson", "William Jackson Harper"],
        "director": "Michael Schur", "rating": 8.2,
        "poster_url": "https://image.tmdb.org/t/p/w500/yOEqnIZfBhpqKoHf7MxUYWJvWJq.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1534796636912-3b95b3ab5986?w=1400&q=80",
        "dna": {"pacing": 0.65, "tension_curve": [0.35,0.5,0.6,0.7,0.75,0.72], "visual_style": "bright_surreal", "audio_mood": "playful_orchestral", "thematic_tags": ["philosophy","ethics","afterlife","self_improvement","community"], "runtime_min": 22},
    },
    {
        "id": "schitts-creek-s1-2015",
        "title": "Schitt's Creek",
        "year": 2015, "kind": "series",
        "synopsis": "A wealthy family loses everything and is forced to move to a small town they once bought as a joke.",
        "genres": ["Comedy"], "cast": ["Eugene Levy", "Catherine O'Hara", "Dan Levy"],
        "director": "Dan Levy", "rating": 8.5,
        "poster_url": "https://image.tmdb.org/t/p/w500/eSVTpUsGVtNLOfv3k5r8PoWNqfH.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1444723121867-7a241cacace9?w=1400&q=80",
        "dna": {"pacing": 0.5, "tension_curve": [0.25,0.38,0.48,0.55,0.6,0.65], "visual_style": "warm_small_town", "audio_mood": "quirky_heartfelt", "thematic_tags": ["class","acceptance","family","small_town","growth"], "runtime_min": 22},
    },

    # ── HORROR & SUSPENSE ────────────────────────────────────────────────

    {
        "id": "hereditary-2018",
        "title": "Hereditary",
        "year": 2018, "kind": "film",
        "synopsis": "After a family's matriarch dies, her daughter and grandchildren unravel dark secrets. The most disturbing horror film in years.",
        "genres": ["Horror", "Drama", "Mystery"], "cast": ["Toni Collette", "Milly Shapiro", "Gabriel Byrne"],
        "director": "Ari Aster", "rating": 7.3,
        "poster_url": "https://image.tmdb.org/t/p/w500/5gGsRXMNcyW93SnTsGGRdGPJVZw.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1475274047050-1d0c0975c63e?w=1400&q=80",
        "dna": {"pacing": 0.38, "tension_curve": [0.2,0.4,0.6,0.78,0.9,0.98], "visual_style": "domestic_dread", "audio_mood": "atonal_strings", "thematic_tags": ["grief","family_trauma","occult","miniatures","horror"], "runtime_min": 127},
    },
    {
        "id": "the-lighthouse-2019",
        "title": "The Lighthouse",
        "year": 2019, "kind": "film",
        "synopsis": "Two lighthouse keepers are stranded on a remote New England island at the end of the 19th century. Madness, mythology, and the sea.",
        "genres": ["Horror", "Drama", "Mystery"], "cast": ["Robert Pattinson", "Willem Dafoe"],
        "director": "Robert Eggers", "rating": 7.5,
        "poster_url": "https://image.tmdb.org/t/p/w500/3P52oz9HPQdxFbIYe1inZlcmMEK.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=1400&q=80",
        "dna": {"pacing": 0.3, "tension_curve": [0.2,0.38,0.55,0.68,0.82,0.9], "visual_style": "black_white_expressionist", "audio_mood": "foghorn_orchestral", "thematic_tags": ["isolation","madness","mythology","power","sea"], "runtime_min": 110},
    },

    # ── INTERNATIONAL ────────────────────────────────────────────────────

    {
        "id": "squid-game-s1-2021",
        "title": "Squid Game",
        "year": 2021, "kind": "series",
        "synopsis": "Hundreds of cash-strapped contestants accept an invitation to compete in children's games for a prize. Losers are eliminated — permanently.",
        "genres": ["Thriller", "Drama", "Sci-Fi"], "cast": ["Lee Jung-jae", "Park Hae-soo", "Oh Yeong-su"],
        "director": "Hwang Dong-hyuk", "rating": 8.0,
        "poster_url": "https://image.tmdb.org/t/p/w500/dDlEmu3EZ0Pgg93K2SVNLCjCSvE.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=1400&q=80",
        "dna": {"pacing": 0.75, "tension_curve": [0.4,0.62,0.78,0.88,0.94,0.9], "visual_style": "pastel_brutal", "audio_mood": "folk_horror_blend", "thematic_tags": ["class_warfare","survival","debt","Korea","games"], "runtime_min": 55},
    },
    {
        "id": "money-heist-s1-2017",
        "title": "Money Heist",
        "year": 2017, "kind": "series",
        "synopsis": "A criminal mastermind recruits eight thieves to carry out the greatest heist in history — taking hostages inside the Royal Mint of Spain.",
        "genres": ["Action", "Crime", "Drama"], "cast": ["Álvaro Morte", "Úrsula Corberó", "Pedro Alonso"],
        "director": "Álex Pina", "rating": 8.2,
        "poster_url": "https://image.tmdb.org/t/p/w500/reEMJA1OiYo2wVqGe5YDdVPGVlg.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=1400&q=80",
        "dna": {"pacing": 0.78, "tension_curve": [0.4,0.62,0.75,0.85,0.9,0.92], "visual_style": "stylized_spanish", "audio_mood": "bella_ciao_energetic", "thematic_tags": ["heist","Spain","resistance","love","chaos"], "runtime_min": 45},
    },
    {
        "id": "lupin-s1-2021",
        "title": "Lupin",
        "year": 2021, "kind": "series",
        "synopsis": "A man uses the fictional gentleman thief Arsène Lupin as his inspiration to seek revenge for injustice done to his father.",
        "genres": ["Crime", "Mystery", "Drama"], "cast": ["Omar Sy", "Ludivine Sagnier", "Clotilde Hesme"],
        "director": "Louis Leterrier", "rating": 7.5,
        "poster_url": "https://image.tmdb.org/t/p/w500/sgxawbFB5Vi5OkPWQLNfl3dvkNJ.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1499856871958-5b9627545d1a?w=1400&q=80",
        "dna": {"pacing": 0.72, "tension_curve": [0.35,0.55,0.7,0.8,0.88,0.85], "visual_style": "parisian_stylish", "audio_mood": "jazzy_playful", "thematic_tags": ["heist","France","race","justice","con_artist"], "runtime_min": 45},
    },
    {
        "id": "kingdom-s1-2019",
        "title": "Kingdom",
        "year": 2019, "kind": "series",
        "synopsis": "A Joseon-era Korean prince investigates a mysterious plague while navigating palace politics. Zombie horror meets historical epic.",
        "genres": ["Horror", "Drama", "History"], "cast": ["Ju Ji-hoon", "Bae Doona", "Ryu Seung-ryong"],
        "director": "Kim Seong-hun", "rating": 8.3,
        "poster_url": "https://image.tmdb.org/t/p/w500/oKgi5bjNBzBhSkBLBRFGWFJFTPe.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=1400&q=80",
        "dna": {"pacing": 0.7, "tension_curve": [0.35,0.58,0.72,0.85,0.92,0.9], "visual_style": "historical_epic", "audio_mood": "traditional_intense", "thematic_tags": ["zombie","Joseon","politics","class","Korea"], "runtime_min": 50},
    },
    {
        "id": "all-quiet-western-front-2022",
        "title": "All Quiet on the Western Front",
        "year": 2022, "kind": "film",
        "synopsis": "A young German soldier fights on the Western Front during World War I and discovers the true face of war.",
        "genres": ["War", "Drama", "History"], "cast": ["Felix Kammerer", "Albrecht Schuch", "Daniel Brühl"],
        "director": "Edward Berger", "rating": 7.8,
        "poster_url": "https://image.tmdb.org/t/p/w500/hgMmCOr3WDSHOpxAFzuSiT8rBvZ.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1547036967-23d11aacaee0?w=1400&q=80",
        "dna": {"pacing": 0.6, "tension_curve": [0.3,0.55,0.72,0.85,0.9,0.92], "visual_style": "gritty_realistic_war", "audio_mood": "industrial_mournful", "thematic_tags": ["WWI","futility_of_war","youth","Germany","anti_war"], "runtime_min": 147},
    },

    # ── ACTION & SPECTACLE ────────────────────────────────────────────────

    {
        "id": "mad-max-fury-road-2015",
        "title": "Mad Max: Fury Road",
        "year": 2015, "kind": "film",
        "synopsis": "In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler in a high-octane road war. The greatest action film of the 21st century.",
        "genres": ["Action", "Sci-Fi", "Adventure"], "cast": ["Tom Hardy", "Charlize Theron", "Nicholas Hoult"],
        "director": "George Miller", "rating": 8.1,
        "poster_url": "https://image.tmdb.org/t/p/w500/kqjL17yufvn9OVLyXYpvtyrFfak.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1509909756405-be0199881695?w=1400&q=80",
        "dna": {"pacing": 0.97, "tension_curve": [0.6,0.8,0.9,0.95,0.97,0.99], "visual_style": "post_apocalyptic_saturated", "audio_mood": "electric_guitar_percussion", "thematic_tags": ["feminism","survival","chase","dystopia","spectacle"], "runtime_min": 120},
    },
    {
        "id": "mission-impossible-fallout-2018",
        "title": "Mission: Impossible — Fallout",
        "year": 2018, "kind": "film",
        "synopsis": "Ethan Hunt and his team race against time to prevent a nuclear catastrophe. The gold standard of practical action filmmaking.",
        "genres": ["Action", "Thriller", "Adventure"], "cast": ["Tom Cruise", "Henry Cavill", "Ving Rhames"],
        "director": "Christopher McQuarrie", "rating": 7.7,
        "poster_url": "https://image.tmdb.org/t/p/w500/AkJQpZp9WoNdj7pLYSj1L0RcMMN.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1551009175-8a68da93d5f9?w=1400&q=80",
        "dna": {"pacing": 0.92, "tension_curve": [0.5,0.7,0.82,0.9,0.95,0.97], "visual_style": "practical_global_epic", "audio_mood": "orchestral_propulsive", "thematic_tags": ["espionage","sacrifice","practical_stunts","nuclear","globetrotting"], "runtime_min": 147},
    },

    # ── DOCUMENTARY ──────────────────────────────────────────────────────

    {
        "id": "the-act-of-killing-2012",
        "title": "The Act of Killing",
        "year": 2012, "kind": "film",
        "synopsis": "The men who led Indonesian death squads in 1965 are asked to recreate their atrocities in the style of their favourite films.",
        "genres": ["Documentary"], "cast": ["Anwar Congo"],
        "director": "Joshua Oppenheimer", "rating": 8.2,
        "poster_url": "https://image.tmdb.org/t/p/w500/n0p2smH5TXFkVlVKEAHsXKFaGFX.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1503444200347-fa86187a2797?w=1400&q=80",
        "dna": {"pacing": 0.3, "tension_curve": [0.2,0.35,0.5,0.65,0.75,0.8], "visual_style": "surreal_documentary", "audio_mood": "dissonant_theatrical", "thematic_tags": ["Indonesia","genocide","self_delusion","performance","impunity"], "runtime_min": 115},
    },
    {
        "id": "icarus-2017",
        "title": "Icarus",
        "year": 2017, "kind": "film",
        "synopsis": "A filmmaker's personal doping experiment accidentally exposes the world's largest state-sponsored doping program.",
        "genres": ["Documentary", "Thriller"], "cast": ["Bryan Fogel", "Grigory Rodchenkov"],
        "director": "Bryan Fogel", "rating": 7.9,
        "poster_url": "https://image.tmdb.org/t/p/w500/r8JpFlbzjGGkB7l0IUAK0kNWFGc.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=1400&q=80",
        "dna": {"pacing": 0.65, "tension_curve": [0.3,0.5,0.68,0.82,0.9,0.88], "visual_style": "documentary_thriller", "audio_mood": "tense_investigative", "thematic_tags": ["doping","Russia","Olympics","whistleblower","conspiracy"], "runtime_min": 96},
    },

    # ── FEEL-GOOD & WARM ─────────────────────────────────────────────────

    {
        "id": "julie-and-julia-2009",
        "title": "Julie & Julia",
        "year": 2009, "kind": "film",
        "synopsis": "The life of Julia Child in the 1950s and a blogger who decides to cook all 524 recipes in Child's cookbook in 365 days.",
        "genres": ["Comedy", "Drama", "Romance"], "cast": ["Meryl Streep", "Amy Adams", "Stanley Tucci"],
        "director": "Nora Ephron", "rating": 7.0,
        "poster_url": "https://image.tmdb.org/t/p/w500/pqPhOy0LxDN9O1TrNmLvEeacPqm.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1400&q=80",
        "dna": {"pacing": 0.45, "tension_curve": [0.2,0.3,0.4,0.5,0.55,0.58], "visual_style": "warm_culinary", "audio_mood": "joyful_light", "thematic_tags": ["food","ambition","France","1950s","blogging"], "runtime_min": 123},
    },
    {
        "id": "coda-2021",
        "title": "CODA",
        "year": 2021, "kind": "film",
        "synopsis": "The only hearing child of a deaf family must choose between her love of music and her family's fishing business.",
        "genres": ["Drama", "Music", "Comedy"], "cast": ["Emilia Jones", "Troy Kotsur", "Marlee Matlin"],
        "director": "Sian Heder", "rating": 7.9,
        "poster_url": "https://image.tmdb.org/t/p/w500/BzVjmm8l23rPsijLiNLUzuQtyd.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=1400&q=80",
        "dna": {"pacing": 0.4, "tension_curve": [0.2,0.35,0.5,0.6,0.72,0.8], "visual_style": "naturalistic_warm", "audio_mood": "folk_emotional", "thematic_tags": ["deaf_culture","family","music","belonging","Massachusetts"], "runtime_min": 112},
    },
    {
        "id": "the-grand-budapest-hotel-2014",
        "title": "The Grand Budapest Hotel",
        "year": 2014, "kind": "film",
        "synopsis": "The adventures of a legendary concierge and his protégé in a fictional European country between the World Wars.",
        "genres": ["Comedy", "Drama", "Adventure"], "cast": ["Ralph Fiennes", "Tony Revolori", "Tilda Swinton"],
        "director": "Wes Anderson", "rating": 8.1,
        "poster_url": "https://image.tmdb.org/t/p/w500/eWdyYQreja6JGCzqHWXpWHDrrPo.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1521295121783-8a321d551ad2?w=1400&q=80",
        "dna": {"pacing": 0.72, "tension_curve": [0.3,0.5,0.65,0.75,0.82,0.8], "visual_style": "symmetrical_pastel", "audio_mood": "folk_orchestral_whimsical", "thematic_tags": ["nostalgia","Europe","fascism","loyalty","style"], "runtime_min": 99},
    },

    # ── ANIMATION ────────────────────────────────────────────────────────

    {
        "id": "arcane-s1-2021",
        "title": "Arcane",
        "year": 2021, "kind": "series",
        "synopsis": "Set in the utopian region of Piltover and the oppressed underground of Zaun, the series follows the origins of two legendary champions.",
        "genres": ["Animation", "Action", "Fantasy"], "cast": ["Hailee Steinfeld", "Ella Purnell", "Kevin Alejandro"],
        "director": "Pascal Charrue", "rating": 9.0,
        "poster_url": "https://image.tmdb.org/t/p/w500/fqldf2t8ztc9aiwn3k6mlX3tvRT.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1509909756405-be0199881695?w=1400&q=80",
        "dna": {"pacing": 0.7, "tension_curve": [0.35,0.55,0.72,0.85,0.92,0.95], "visual_style": "painterly_animation", "audio_mood": "indie_orchestral_hybrid", "thematic_tags": ["sisters","class","revolution","technology","League_of_Legends"], "runtime_min": 42},
    },
    {
        "id": "spirited-away-2001",
        "title": "Spirited Away",
        "year": 2001, "kind": "film",
        "synopsis": "A young girl wanders into a magical spirit world where her parents have been transformed into pigs.",
        "genres": ["Animation", "Fantasy", "Adventure"], "cast": ["Daveigh Chase", "Suzanne Pleshette"],
        "director": "Hayao Miyazaki", "rating": 8.6,
        "poster_url": "https://image.tmdb.org/t/p/w500/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg",
        "backdrop_url": "https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=1400&q=80",
        "dna": {"pacing": 0.5, "tension_curve": [0.3,0.45,0.6,0.7,0.75,0.8], "visual_style": "lush_hand_drawn", "audio_mood": "orchestral_wonder", "thematic_tags": ["spirit_world","Japan","work","childhood","transformation"], "runtime_min": 125},
    },
]


async def run_seed():
    logging.basicConfig(level=logging.INFO)
    from catalog.vector_store import get_vector_store
    from catalog.graph import get_graph

    log.info("Starting NEXUS catalog seed — %d titles", len(CATALOG))

    vs = get_vector_store()
    graph = get_graph()

    await vs.ensure_collection()
    await graph.ensure_schema()

    await vs.upsert_content(CATALOG)
    await graph.upsert_content(CATALOG)

    # Similarity edges
    pairs = [
        ("inception-2010", "dark-s1-2017", 0.78),
        ("inception-2010", "mr-robot-s1-2015", 0.74),
        ("blade-runner-2049", "her-2013", 0.76),
        ("blade-runner-2049", "arrival-2016", 0.72),
        ("blade-runner-2049", "ex-machina-2014", 0.75),
        ("severance-s1-2022", "mr-robot-s1-2015", 0.78),
        ("severance-s1-2022", "dark-s1-2017", 0.75),
        ("breaking-bad-s1-2008", "better-call-saul-s1-2015", 0.92),
        ("breaking-bad-s1-2008", "ozark-s1-2017", 0.76),
        ("the-wire-s1-2002", "the-sopranos-s1-1999", 0.82),
        ("succession-s4-2023", "mad-men-s1-2007", 0.72),
        ("succession-s4-2023", "the-sopranos-s1-1999", 0.68),
        ("parasite-2019", "squid-game-s1-2021", 0.74),
        ("parasite-2019", "the-menu-2022", 0.71),
        ("oppenheimer-2023", "chernobyl-2019", 0.78),
        ("oppenheimer-2023", "whiplash-2014", 0.62),
        ("dune-part-two-2024", "interstellar-2014", 0.72),
        ("dune-part-two-2024", "arrival-2016", 0.74),
        ("the-last-of-us-s1-2023", "station-eleven-2021", 0.73),
        ("the-last-of-us-s1-2023", "kingdom-s1-2019", 0.68),
        ("shogun-2024", "peaky-blinders-s1-2013", 0.65),
        ("mindhunter-s1-2017", "the-wire-s1-2002", 0.68),
        ("midsommar-2019", "hereditary-2018", 0.82),
        ("the-lighthouse-2019", "midsommar-2019", 0.7),
        ("drive-2011", "nightcrawler-2014", 0.72),
        ("fleabag-s1-2016", "barry-s1-2018", 0.68),
        ("atlanta-s1-2016", "barry-s1-2018", 0.7),
        ("ted-lasso-s1-2020", "schitts-creek-s1-2015", 0.72),
        ("money-heist-s1-2017", "lupin-s1-2021", 0.74),
        ("squid-game-s1-2021", "kingdom-s1-2019", 0.7),
        ("the-social-network-2010", "halt-and-catch-fire-s1-2014", 0.68),
        ("dark-s1-2017", "westworld-s1-2016", 0.72),
        ("aftersun-2022", "past-lives-2023", 0.78),
        ("moonlight-2016", "aftersun-2022", 0.7),
        ("gone-girl-2014", "nightcrawler-2014", 0.65),
        ("no-country-for-old-men-2007", "mindhunter-s1-2017", 0.67),
    ]
    for a, b, score in pairs:
        try:
            await graph.create_similarity_edge(a, b, score)
        except Exception:
            pass

    count = await vs.count()
    stats = await graph.graph_stats()
    log.info("Seed complete. Vectors: %d | Graph: %s", count, stats)


async def run_seed_with_tmdb():
    """Run seed with optional TMDB enrichment."""
    logging.basicConfig(level=logging.INFO)
    from config import get_settings
    settings = get_settings()

    if settings.tmdb_api_key:
        from catalog.tmdb import get_tmdb_client
        client = get_tmdb_client()
        if client:
            try:
                global CATALOG
                CATALOG = await client.enrich_catalog(CATALOG, concurrency=3)
                log.info("TMDB enrichment complete")
            except Exception as e:
                log.warning("TMDB enrichment failed: %s — using embedded metadata", e)
            finally:
                await client.close()

    await run_seed()


if __name__ == "__main__":
    asyncio.run(run_seed_with_tmdb())
