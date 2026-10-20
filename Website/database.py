
import sqlite3

DATABASE_NAME = "shadow_protocol.db"

PUZZLES = [
    {
        "id": "P001", "title": "Ghost Signal",
        "category": "Caesar Cipher", "difficulty": "Easy",
        "message": "VKDGRZ", "answer": "SHADOW",
        "clue": "Each letter has been shifted 3 places forward.",
        "hint": "Move every letter 3 places backward.",
        "story": "An unknown sender left an encrypted transmission.",
        "xp": 50,
    },
    {
        "id": "P002", "title": "Hidden Identity",
        "category": "Identity Code", "difficulty": "Easy",
        "message": "KDFNHU", "answer": "HACKER",
        "clue": "The alphabet has shifted by 3 positions.",
        "hint": "Reverse the shift by 3.",
        "story": "A suspicious identity was found in an intercepted file.",
        "xp": 50,
    },
    {
        "id": "P003", "title": "Secure Channel",
        "category": "Caesar Cipher", "difficulty": "Easy",
        "message": "VHFXUH", "answer": "SECURE",
        "clue": "Use a Caesar shift of 3.",
        "hint": "Move each letter backward by 3.",
        "story": "A protected channel contains a hidden word.",
        "xp": 50,
    },
    {
        "id": "P004", "title": "Code Fragment",
        "category": "Caesar Cipher", "difficulty": "Easy",
        "message": "FRGH", "answer": "CODE",
        "clue": "The letters have moved 3 positions forward.",
        "hint": "Move each coded letter backward by 3.",
        "story": "A short fragment may unlock the next clue.",
        "xp": 50,
    },
    {
        "id": "P005", "title": "Unknown Agent",
        "category": "Caesar Cipher", "difficulty": "Easy",
        "message": "DJHQW", "answer": "AGENT",
        "clue": "Reverse a Caesar shift of 3.",
        "hint": "D becomes A.",
        "story": "An agent's codename was recovered.",
        "xp": 50,
    },
    {
        "id": "P006", "title": "Mission File",
        "category": "Caesar Cipher", "difficulty": "Medium",
        "message": "PLVVLRQ", "answer": "MISSION",
        "clue": "Every letter uses the same shift.",
        "hint": "Move each letter backward by 3.",
        "story": "A classified mission file is locked.",
        "xp": 75,
    },
    {
        "id": "P007", "title": "Secret Transmission",
        "category": "Caesar Cipher", "difficulty": "Medium",
        "message": "VHFUHW", "answer": "SECRET",
        "clue": "The encryption moves letters forward by 3.",
        "hint": "Reverse the shift.",
        "story": "The recovered transmission may contain a warning.",
        "xp": 75,
    },
    {
        "id": "P008", "title": "Protocol Breach",
        "category": "Caesar Cipher", "difficulty": "Medium",
        "message": "SURWRFRO", "answer": "PROTOCOL",
        "clue": "Decode the message using a Caesar shift.",
        "hint": "Move each letter backward by 3.",
        "story": "A protocol document was intercepted.",
        "xp": 75,
    },
    {
        "id": "P009", "title": "Firewall Alert",
        "category": "Firewall Logic", "difficulty": "Medium",
        "message": "2, 4, 6, 8, ?", "answer": "10",
        "clue": "Find the next number in the sequence.",
        "hint": "The numbers increase by two each time.",
        "story": "A simulated firewall checkpoint requires a pattern answer.",
        "xp": 75,
    },
    {
        "id": "P010", "title": "Encrypted Archive",
        "category": "Binary & File Recovery", "difficulty": "Medium",
        "message": "HQFUBSWHG", "answer": "ENCRYPTED",
        "clue": "Every letter uses a shift of 3.",
        "hint": "Move each letter backward by 3.",
        "story": "An encrypted archive has been discovered.",
        "xp": 75,
    },
    {
        "id": "P011", "title": "Mirror Message",
        "category": "Reverse Text", "difficulty": "Easy",
        "message": "TERCES", "answer": "SECRET",
        "clue": "The message has been written backward.",
        "hint": "Read the letters from right to left.",
        "story": "A note was reversed before being hidden.",
        "xp": 50,
    },
    {
        "id": "P012", "title": "Reversed Access",
        "category": "Reverse Text", "difficulty": "Easy",
        "message": "TNEGA", "answer": "AGENT",
        "clue": "The word is reversed.",
        "hint": "Start with the final letter.",
        "story": "A reversed codename appears in a notebook.",
        "xp": 50,
    },
    {
        "id": "P013", "title": "Morse Transmission",
        "category": "Morse Code", "difficulty": "Medium",
        "message": "... . -.-. .-. . -", "answer": "SECRET",
        "clue": "Dots and dashes represent letters.",
        "hint": "Decode each Morse letter in order.",
        "story": "An old radio recorded a coded transmission.",
        "xp": 75,
    },
    {
        "id": "P014", "title": "Radio Signal",
        "category": "Morse Code", "difficulty": "Easy",
        "message": "... --- ...", "answer": "SOS",
        "clue": "This is a well-known distress signal.",
        "hint": "Three dots, three dashes, three dots.",
        "story": "A distress signal was picked up in the dark.",
        "xp": 50,
    },
    {
        "id": "P015", "title": "Binary Greeting",
        "category": "Binary Code", "difficulty": "Medium",
        "message": "01001000 01001001", "answer": "HI",
        "clue": "Each group of eight bits represents a character.",
        "hint": "Convert each binary byte into ASCII.",
        "story": "A digital message was found inside a data packet.",
        "xp": 75,
    },
    {
        "id": "P016", "title": "Binary Key",
        "category": "Binary Code", "difficulty": "Medium",
        "message": "01000011 01001111 01000100 01000101",
        "answer": "CODE",
        "clue": "Decode the binary bytes as ASCII characters.",
        "hint": "Convert each 8-bit group separately.",
        "story": "A digital lock requires the original word.",
        "xp": 75,
    },
    {
        "id": "P017", "title": "Number Cipher",
        "category": "Number Code", "difficulty": "Easy",
        "message": "3-15-4-5", "answer": "CODE",
        "clue": "A=1, B=2, C=3, and so on.",
        "hint": "Turn each number into its alphabet letter.",
        "story": "Numbers were written instead of letters.",
        "xp": 50,
    },
    {
        "id": "P018", "title": "Agent Coordinates",
        "category": "Number Code", "difficulty": "Medium",
        "message": "1-7-5-14-20", "answer": "AGENT",
        "clue": "Use the alphabet positions.",
        "hint": "A is 1 and Z is 26.",
        "story": "An agent left a numerical signature.",
        "xp": 75,
    },
    {
        "id": "P019", "title": "Mirror Alphabet",
        "category": "Atbash Cipher", "difficulty": "Medium",
        "message": "ZGGZXP", "answer": "ATTACK",
        "clue": "A maps to Z, B maps to Y, and so on.",
        "hint": "Pair each letter with its opposite in the alphabet.",
        "story": "A strange alphabet was used in a warning.",
        "xp": 75,
    },
    {
        "id": "P020", "title": "Opposite Letters",
        "category": "Atbash Cipher", "difficulty": "Medium",
        "message": "HVXIVG", "answer": "SECRET",
        "clue": "Decode using the reverse alphabet.",
        "hint": "A becomes Z; C becomes X.",
        "story": "A hidden note uses a mirror alphabet.",
        "xp": 75,
    },
    {
        "id": "P021", "title": "Hex Archive",
        "category": "Hexadecimal", "difficulty": "Hard",
        "message": "53 48 41 44 4F 57", "answer": "SHADOW",
        "clue": "These hexadecimal values represent ASCII characters.",
        "hint": "Convert each hex pair into a character.",
        "story": "A corrupted archive contains a hex-coded name.",
        "xp": 100,
    },
    {
        "id": "P022", "title": "Scrambled File",
        "category": "Word Scramble", "difficulty": "Easy",
        "message": "EDOC", "answer": "CODE",
        "clue": "The letters are in the wrong order.",
        "hint": "Rearrange the letters to form a cyber-related word.",
        "story": "A file label was scrambled during transfer.",
        "xp": 50,
    },
    {
        "id": "P023", "title": "Scrambled Identity",
        "category": "Word Scramble", "difficulty": "Medium",
        "message": "REHACK", "answer": "HACKER",
        "clue": "Rearrange these letters into a six-letter word.",
        "hint": "The word describes someone who works with computer systems.",
        "story": "A scrambled identity was recovered from a file.",
        "xp": 75,
    },
    {
        "id": "P024", "title": "Missing Letters",
        "category": "Word Puzzle", "difficulty": "Easy",
        "message": "S _ C R _ T", "answer": "SECRET",
        "clue": "Fill the two missing letters.",
        "hint": "It means something kept hidden.",
        "story": "Part of a secret word was erased.",
        "xp": 50,
    },
    {
        "id": "P025", "title": "Pattern Lock",
        "category": "Firewall Logic", "difficulty": "Easy",
        "message": "2, 4, 6, 8, ?", "answer": "10",
        "clue": "Find the next number in the sequence.",
        "hint": "The numbers increase by two each time.",
        "story": "A simulated security panel requires the next number.",
        "xp": 50,
    },
    {
        "id": "P026", "title": "Sequence Breaker",
        "category": "Firewall Logic", "difficulty": "Medium",
        "message": "3, 6, 12, 24, ?", "answer": "48",
        "clue": "Look at how each number changes.",
        "hint": "Each number is multiplied by two.",
        "story": "A numeric lock protects a fictional folder.",
        "xp": 75,
    },
    {
        "id": "P027", "title": "Password Riddle",
        "category": "Riddle", "difficulty": "Medium",
        "message": "I have keys but no locks. I have space but no room. What am I?",
        "answer": "KEYBOARD",
        "clue": "Think of a common computer device.",
        "hint": "You use it to type.",
        "story": "A riddle protects the next case file.",
        "xp": 75,
    },
    {
        "id": "P028", "title": "Hidden Word",
        "category": "Word Puzzle", "difficulty": "Medium",
        "message": "S H A D O W", "answer": "SHADOW",
        "clue": "Remove the spaces to reveal the word.",
        "hint": "Read the letters from left to right.",
        "story": "A word was split apart in a damaged file.",
        "xp": 75,
    },
    {
        "id": "P029", "title": "Digital Detective",
        "category": "Riddle", "difficulty": "Easy",
        "message": "I protect your account, but I should never be shared. What am I?",
        "answer": "PASSWORD",
        "clue": "You enter it to access an account.",
        "hint": "Keep it private and unique.",
        "story": "A security awareness case needs an answer.",
        "xp": 50,
    },
    {
        "id": "P030", "title": "Final Signal",
        "category": "Binary Code", "difficulty": "Hard",
        "message": "01010011 01001111 01010011", "answer": "SOS",
        "clue": "Decode each binary byte as an ASCII character.",
        "hint": "There are three groups of eight bits.",
        "story": "A final signal was discovered deep in the archive.",
        "xp": 100,
    },
]


# =========================================================
# RANK PROGRESSION
# Keep these thresholds synchronized with app.py.
# =========================================================

RANKS = [
    (1200, "Ghost Protocol"),
    (800, "Phantom"),
    (500, "Shadow Agent"),
    (250, "Specialist"),
    (100, "Elite Operative"),
    (0, "Recruit"),
]


def calculate_rank(xp):
    for threshold, rank_name in RANKS:
        if xp >= threshold:
            return rank_name
    return "Recruit"


# =========================================================
# CONNECTION
# =========================================================

def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


# =========================================================
# INITIALIZE DATABASE
# =========================================================

def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS player (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL DEFAULT 'Agent',
                xp INTEGER NOT NULL DEFAULT 0,
                completed_missions INTEGER NOT NULL DEFAULT 0,
                rank TEXT NOT NULL DEFAULT 'Recruit'
            )
        """)

        connection.execute("""
            INSERT OR IGNORE INTO player (id)
            VALUES (1)
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS puzzles (
                puzzle_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                message TEXT NOT NULL,
                answer TEXT NOT NULL,
                clue TEXT NOT NULL,
                hint TEXT NOT NULL,
                story TEXT NOT NULL,
                xp_reward INTEGER NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS puzzle_completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                puzzle_id TEXT NOT NULL,
                round_number INTEGER NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(puzzle_id, round_number)
            )
        """)

        # Insert new puzzles and update existing puzzle content.
        # Completion history and player XP remain intact.
        for puzzle in PUZZLES:
            connection.execute("""
                INSERT INTO puzzles (
                    puzzle_id, title, category, difficulty,
                    message, answer, clue, hint, story, xp_reward
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(puzzle_id) DO UPDATE SET
                    title = excluded.title,
                    category = excluded.category,
                    difficulty = excluded.difficulty,
                    message = excluded.message,
                    answer = excluded.answer,
                    clue = excluded.clue,
                    hint = excluded.hint,
                    story = excluded.story,
                    xp_reward = excluded.xp_reward
            """, (
                puzzle["id"],
                puzzle["title"],
                puzzle["category"],
                puzzle["difficulty"],
                puzzle["message"],
                puzzle["answer"],
                puzzle["clue"],
                puzzle["hint"],
                puzzle["story"],
                puzzle["xp"],
            ))

        # Upgrade rank labels for existing players without resetting XP.
        player = connection.execute(
            "SELECT xp FROM player WHERE id = 1"
        ).fetchone()

        if player:
            connection.execute(
                "UPDATE player SET rank = ? WHERE id = 1",
                (calculate_rank(player["xp"]),),
            )


# =========================================================
# PLAYER
# =========================================================

def get_player():
    with get_connection() as connection:
        player = connection.execute(
            "SELECT * FROM player WHERE id = 1"
        ).fetchone()

    return player


# =========================================================
# PUZZLE HELPERS
# =========================================================

def get_puzzle(puzzle_id):
    with get_connection() as connection:
        puzzle = connection.execute(
            "SELECT * FROM puzzles WHERE puzzle_id = ?",
            (puzzle_id,),
        ).fetchone()

    return dict(puzzle) if puzzle else None


def get_next_puzzle():
    with get_connection() as connection:
        total = connection.execute(
            "SELECT COUNT(*) FROM puzzles"
        ).fetchone()[0]

        latest_round = connection.execute(
            "SELECT COALESCE(MAX(round_number), 1) "
            "FROM puzzle_completions"
        ).fetchone()[0]

        completed_count = connection.execute(
            "SELECT COUNT(DISTINCT puzzle_id) "
            "FROM puzzle_completions WHERE round_number = ?",
            (latest_round,),
        ).fetchone()[0]

        if completed_count >= total:
            latest_round += 1

        puzzle = connection.execute("""
            SELECT *
            FROM puzzles
            WHERE puzzle_id NOT IN (
                SELECT puzzle_id
                FROM puzzle_completions
                WHERE round_number = ?
            )
            ORDER BY RANDOM()
            LIMIT 1
        """, (latest_round,)).fetchone()

    if puzzle is None:
        return None

    result = dict(puzzle)
    result["round_number"] = latest_round
    return result


def get_puzzle_count():
    with get_connection() as connection:
        return connection.execute(
            "SELECT COUNT(*) FROM puzzles"
        ).fetchone()[0]


# =========================================================
# COMPLETE PUZZLE
# Award XP once per puzzle per round.
# =========================================================

def complete_puzzle(puzzle_id, round_number):
    with get_connection() as connection:
        puzzle = connection.execute(
            "SELECT xp_reward FROM puzzles WHERE puzzle_id = ?",
            (puzzle_id,),
        ).fetchone()

        if puzzle is None:
            return False

        cursor = connection.execute("""
            INSERT OR IGNORE INTO puzzle_completions (
                puzzle_id, round_number
            )
            VALUES (?, ?)
        """, (puzzle_id, round_number))

        # Prevent duplicate XP rewards for the same puzzle in the same round.
        if cursor.rowcount == 0:
            return False

        reward = puzzle["xp_reward"]

        connection.execute("""
            UPDATE player
            SET xp = xp + ?,
                completed_missions = completed_missions + 1
            WHERE id = 1
        """, (reward,))

        player = connection.execute(
            "SELECT xp FROM player WHERE id = 1"
        ).fetchone()

        connection.execute(
            "UPDATE player SET rank = ? WHERE id = 1",
            (calculate_rank(player["xp"]),),
        )

    return True
