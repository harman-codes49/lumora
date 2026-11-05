"""
Starter content for a brand-new Lumora database.

Runs only when the database is completely empty (a fresh deploy), so an
existing local database with real data is never touched. Dates are
relative to today so the app always looks current.
"""

import shutil
from datetime import date, datetime, timedelta

from app.database.db import BASE_DIR, DATA_DIR, get_connection

SEED_MEDIA_DIR = BASE_DIR / "assets" / "seed"
MEMORIES_DIR = DATA_DIR / "memories"


def _ts(days_ago, hour, minute=0):
    moment = datetime.now().replace(
        hour=hour, minute=minute, second=0, microsecond=0
    ) - timedelta(days=days_ago)
    return moment.strftime("%Y-%m-%d %H:%M:%S")


def _day(offset):
    return (date.today() + timedelta(days=offset)).isoformat()


# (title, days_ago, hour, [(role, text), ...])
CONVERSATIONS = [
    ("Presentation nerves", 13, 21, [
        ("user", "kal DBMS ka presentation hai and I'm so nervous yaar"),
        ("assistant", "Presentation se pehle nervous feel karna bilkul normal hai, Harmanpreet. Iska matlab hai ki tumhe isse farak padta hai. 💜\n\nKya tumhari slides ready hain, ya abhi bhi kuch kaam baaki hai?"),
        ("user", "slides ready hain, bas bolte time atak jaati hoon"),
        ("assistant", "Achha, toh content ready hai. Ab sirf delivery ki practice chahiye.\n\nEk kaam karo: aaj raat sirf 2 baar out loud practice karo, ek baar timer ke saath. Har slide ke liye bas ek key line yaad rakho, poora script nahi. Atakne pe pause lena bhi theek hai, audience ko wo pause confidence jaisa lagta hai.\n\nKaunsi slide sabse tricky lag rahi hai?"),
        ("user", "normalization wali"),
        ("assistant", "Normalization ke liye ek simple example rakho, jaise ek student table jisme course details repeat ho rahi hain. Pehle problem dikhao, phir 1NF → 2NF → 3NF mein usko todte hue. Example ke saath bologi toh rata hua nahi lagega. Tum kar logi! ✨"),
    ]),
    ("It went well!", 12, 15, [
        ("user", "presentation ho gaya!! ma'am ne bola good explanation 😭"),
        ("assistant", "Yayyy! 🎉 Ye toh bahut badi baat hai. Kal raat tum itna nervous thi aur aaj ma'am ne specially tareef ki.\n\nKya lagta hai, kis cheez ne sabse zyada help ki?"),
        ("user", "example wala idea, mujhe khud samajh aa gaya tha toh bolna easy tha"),
        ("assistant", "Exactly, jab cheez khud samajh aa jaati hai toh confidence apne aap aata hai. Isko yaad rakhna next time ke liye. Aaj thoda celebrate karo, you earned it. 💜"),
    ]),
    ("Placement prep plan", 9, 19, [
        ("user", "placements aa rahe hain and mujhe samajh nahi aa raha kahan se start karun"),
        ("assistant", "Jab sab kuch ek saath karna ho toh overwhelm hona natural hai. Chalo isko chhote parts mein todte hain.\n\nTumhari college mein mostly kaunsi companies aati hain, service-based ya product-based?"),
        ("user", "mostly service based, TCS Infosys Accenture types"),
        ("assistant", "Perfect, unke liye pattern kaafi predictable hota hai. Ek simple weekly plan:\n\n• Aptitude: roz 30 min (quant + logical)\n• Coding: roz 2 easy problems, arrays aur strings pe\n• Core subjects: weekend pe DBMS, OOPs, OS revise\n• Communication: hafte mein 2 baar \"tell me about yourself\" practice\n\nTum morning mein padhna prefer karti ho na? Toh aptitude subah rakho, jab dimaag fresh ho."),
        ("user", "haan morning best hai. ok I'll try this from monday"),
        ("assistant", "Great! Monday se start karte hain. Pehle hafte perfection ka target mat rakhna, bas consistency. Main yahin hoon agar kabhi plan off-track lage. 🌱"),
    ]),
    ("Gym at 5 AM?", 7, 22, [
        ("user", "socha hai kal se 5 baje gym jaungi"),
        ("assistant", "Ohooo 5 baje gym? 😭😂 Ab asli challenge gym jaana nahi, 5 baje uthna hai.\n\nTum abhi usually kitne baje soti ho?"),
        ("user", "1 baje tak 🙈"),
        ("assistant", "Haha toh 4 ghante ki neend mein gym aur phir college, ye zyada din nahi chalega. 😅\n\nEk idea: pehle hafte 6:30 ka target rakho aur raat 11:30 tak phone side mein. Body adjust ho jaaye toh dheere dheere time pehle kar sakti ho. Sustainable routine > heroic first day."),
    ]),
    ("Thoda upset hoon", 4, 20, [
        ("user", "simran ne aaj meri baat ignore ki group mein, bura laga"),
        ("assistant", "Achha, jab koi close friend aisa kare toh hurt hona bilkul samajh aata hai. 💜\n\nKya ye pehli baar hua hai, ya pehle bhi aisa feel hua hai?"),
        ("user", "pehli baar. shayad wo busy thi"),
        ("assistant", "Ho sakta hai. Group chats mein messages miss ho jaate hain, aur kabhi kabhi log apne hi stress mein hote hain.\n\nAgar mann ho toh usse seedha aur halka sa pooch sakti ho: \"Hey, aaj group mein laga tune mera message miss kar diya, sab theek hai na?\" Isse blame nahi lagta, aur tumhe clarity mil jaayegi."),
        ("user", "haan ye theek hai, I'll text her"),
    ]),
    ("Couldn't sleep", 2, 1, [
        ("user", "neend nahi aa rahi, dimaag mein bahut kuch chal raha hai"),
        ("assistant", "Raat ko jab dimaag ruk hi nahi raha hota toh bahut thaka dene wala lagta hai. Main yahin hoon. 🌙\n\nKya kisi ek cheez ke baare mein soch rahi ho, ya sab kuch thoda thoda?"),
        ("user", "sab kuch. placements, assignments, ghar"),
        ("assistant", "Ek chhota sa kaam try karo: 2 minute mein jo bhi dimaag mein hai, sab notes mein likh do, bina sort kiye. Usse dimaag ko lagta hai ki cheezein \"safe\" hain aur kal dekh lenge.\n\nPhir phone side mein rakh ke 4 second saans andar, 6 second bahar, 5 baar. Kal subah inhe ek ek karke dekhenge, saath mein. 💜"),
    ]),
    ("Weekend plans", 0, 11, [
        ("user", "is weekend kuch relaxing karna hai, ideas do"),
        ("assistant", "Love this! Busy hafte ke baad rest bhi zaroori hai. Kuch ideas:\n\n• Wo novel continue karo jo tum padh rahi thi 📖\n• Mumma ke saath shaam ki chai, bina phone ke\n• Simran ke saath wahi café jahan last time gayi thi ☕\n• Ek lambi walk, aur koi playlist jo tumhe khush karti ho\n\nInmein se kya sabse zyada accha lag raha hai?"),
        ("user", "café plan sounds perfect"),
    ]),
]

# (title, note, file, days_ago)
PHOTO_MEMORIES = [
    ("Coffee date with Simran", "Finally caught up after exams. Same corner table, same latte art. ☕", "cafe-latte.jpg", 3),
    ("Slow Sunday morning", "Chai, a book and no alarms. Needed this so much.", "sunday-tea.jpg", 9),
    ("Finished my first novel of the year", "Took me forever but I finished it! Starting the next one this week.", "first-novel.jpg", 16),
    ("Family trip to the hills", "Cold air, loud cousins and the best maggi of my life. 🏔️", "mountain-trip.jpg", 34),
]

# (title, note, category, days_ago)
LONG_TERM_MEMORIES = [
    ("User Name", "The user's name is Harmanpreet Kaur.", "general", 14),
    ("Study timing", "Harmanpreet studies best in the morning.", "habit", 9),
    ("Placement goal", "Preparing for campus placements, mostly service-based companies.", "goal", 9),
    ("Best friend", "Simran is Harmanpreet's best friend from college.", "general", 4),
    ("Fitness goal", "Wants to build a morning gym routine.", "goal", 7),
    ("Loves chai", "Enjoys evening chai with her mother.", "preference", 9),
]

# (title, offset_days, note, reminder)
IMPORTANT_DATES = [
    ("Simran's birthday", 6, "Plan a surprise at the café 🎂", True),
    ("TCS placement drive", 11, "Revise aptitude + DBMS the week before.", True),
    ("Mid-sem exams begin", 18, "Start revision two weeks before.", True),
    ("Mumma Papa's anniversary", 27, "Order the cake in advance. 💜", True),
]

# (days_ago, prompt, response)
REFLECTIONS = [
    (12, "What went well today?", "The DBMS presentation! I was so scared but ma'am said my explanation was good."),
    (10, "How was your day today?", "Long day. Two lectures and a lab, but I managed to finish my assignment early."),
    (9, "What do you want to carry into tomorrow?", "Starting my placement prep plan. Small steps, every morning."),
    (7, "What felt difficult today?", "Waking up early. My sleep schedule is a mess and I need to fix it."),
    (5, "What went well today?", "Solved three coding problems without looking at hints."),
    (4, "What is on your mind right now?", "Felt a little ignored by Simran today. Going to talk to her calmly."),
    (3, "How was your day today?", "Simran and I went to the café. Everything is fine between us, I was overthinking."),
    (1, "What is on your mind right now?", "Placements are getting closer. Nervous, but I feel more prepared than last month."),
]


def seed_if_empty():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reflections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reflection_date TEXT NOT NULL,
            prompt TEXT NOT NULL,
            response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    has_data = any(
        cursor.execute(f"SELECT 1 FROM {table} LIMIT 1").fetchone()
        for table in ("messages", "memories", "important_dates", "reflections")
    )
    if has_data:
        connection.close()
        return

    for title, days_ago, hour, messages in CONVERSATIONS:
        started = _ts(days_ago, hour)
        cursor.execute(
            "INSERT INTO conversations (title, created_at, updated_at) VALUES (?, ?, ?)",
            (title, started, started),
        )
        conversation_id = cursor.lastrowid
        for i, (role, content) in enumerate(messages):
            cursor.execute(
                "INSERT INTO messages (conversation_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                (conversation_id, role, content, _ts(days_ago, hour, min(i * 2, 59))),
            )
        cursor.execute(
            "UPDATE conversations SET updated_at = ? WHERE id = ?",
            (_ts(days_ago, hour, min(len(messages) * 2, 59)), conversation_id),
        )

    MEMORIES_DIR.mkdir(parents=True, exist_ok=True)
    for title, note, filename, days_ago in PHOTO_MEMORIES:
        source = SEED_MEDIA_DIR / filename
        if not source.exists():
            continue
        target = MEMORIES_DIR / f"seed-{filename}"
        shutil.copyfile(source, target)
        cursor.execute(
            """INSERT INTO memories
               (title, note, media_path, memory_date, created_at, memory_type, category)
               VALUES (?, ?, ?, ?, ?, 'media', 'general')""",
            (title, note, target.relative_to(BASE_DIR).as_posix(),
             _day(-days_ago), _ts(days_ago, 18)),
        )

    for title, note, category, days_ago in LONG_TERM_MEMORIES:
        cursor.execute(
            """INSERT INTO memories
               (title, note, media_path, memory_date, created_at, memory_type, category)
               VALUES (?, ?, '', '', ?, 'long_term', ?)""",
            (title, note, _ts(days_ago, 20), category),
        )

    for title, offset, note, reminder in IMPORTANT_DATES:
        cursor.execute(
            "INSERT INTO important_dates (title, date, note, reminder_enabled, created_at) VALUES (?, ?, ?, ?, ?)",
            (title, _day(offset), note, int(reminder), _ts(10, 19)),
        )

    for days_ago, prompt, response in REFLECTIONS:
        cursor.execute(
            "INSERT INTO reflections (reflection_date, prompt, response, created_at) VALUES (?, ?, ?, ?)",
            (_day(-days_ago), prompt, response, _ts(days_ago, 22)),
        )

    connection.commit()
    connection.close()
