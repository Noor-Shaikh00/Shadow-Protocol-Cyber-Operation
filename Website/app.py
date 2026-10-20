
import html
import random
import sqlite3
import time
import streamlit as st

from database import (
    initialize_database,
    get_player,
    complete_puzzle,
    get_puzzle_count,
    get_connection,
)

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Shadow Protocol | Cyber Operations",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded",
)

initialize_database()

# =========================================================
# RANK SYSTEM
# =========================================================

RANKS = [
    (1200, "Ghost Protocol"),
    (800, "Phantom"),
    (500, "Shadow Agent"),
    (250, "Specialist"),
    (100, "Elite Operative"),
    (0, "Recruit"),
]


def get_rank(xp):
    for threshold, rank_name in RANKS:
        if xp >= threshold:
            return rank_name
    return "Recruit"


def sync_player_rank():
    player = get_player()
    if player:
        rank = get_rank(player["xp"])
        with get_connection() as connection:
            connection.execute(
                "UPDATE player SET rank = ? WHERE id = 1",
                (rank,),
            )
    return get_player()


# =========================================================
# MISSION CONFIGURATION
# =========================================================

MISSIONS = {
    "ghost": {
        "name": "Ghost Signal",
        "category": "SIGNAL INTELLIGENCE",
        "description": "Decode intercepted transmissions and recover hidden signals.",
        "objective": "Decrypt the transmission before the signal disappears.",
        "ids": ["P001", "P003", "P004", "P005", "P006", "P007", "P008"],
        "timer": False,
    },
    "identity": {
        "name": "Hidden Identity",
        "category": "IDENTITY ANALYSIS",
        "description": "Uncover identities using secret codes and patterns.",
        "objective": "Identify the unknown agent from the recovered evidence.",
        "ids": ["P002", "P017", "P018", "P019", "P020", "P023", "P024"],
        "timer": False,
    },
    "file": {
        "name": "Secret File",
        "category": "DIGITAL FILE RECOVERY",
        "description": "Decode binary, Morse and hexadecimal evidence.",
        "objective": "Recover the message inside a fictional encrypted file.",
        "ids": ["P010", "P013", "P015", "P016", "P021", "P030"],
        "timer": False,
    },
    "firewall": {
        "name": "Firewall Alert",
        "category": "LOGIC & SECURITY",
        "description": "Solve patterns and reasoning challenges.",
        "objective": "Clear the simulated security checkpoint.",
        "ids": ["P009", "P025", "P026"],
        "timer": True,
    },
    "detective": {
        "name": "Digital Detective",
        "category": "INVESTIGATION",
        "description": "Analyze clues, solve riddles and reconstruct hidden words.",
        "objective": "Connect the evidence and uncover the answer.",
        "ids": ["P011", "P012", "P014", "P022", "P027", "P028", "P029"],
        "timer": False,
    },
}

MISSIONS["all"] = {
    "name": "All Operations",
    "category": "FULL INVESTIGATION",
    "description": "Play the complete puzzle library in randomized order.",
    "objective": "Complete the next available challenge.",
    "ids": [f"P{i:03d}" for i in range(1, 31)],
    "timer": False,
}

# =========================================================
# SUSPECT BOARD
# =========================================================

SUSPECTS = {
    "Dr. Evelyn Cross": {
        "role": "Lead Researcher",
        "motive": "A classified research file disappeared under her supervision.",
        "alibi": "Claims she was working in the laboratory.",
        "lead": "Review the encrypted archive before drawing conclusions.",
    },
    "Marcus Vale": {
        "role": "Systems Administrator",
        "motive": "Had authorized access to the simulated server room.",
        "alibi": "Claims the access logs were incomplete.",
        "lead": "Compare the recovered code with the access records.",
    },
    "Nadia Frost": {
        "role": "Security Analyst",
        "motive": "Reported unusual activity shortly before the incident.",
        "alibi": "Claims she was monitoring the security console.",
        "lead": "Examine the firewall sequence and signal records.",
    },
}

# =========================================================
# SESSION STATE
# =========================================================

DEFAULTS = {
    "game_screen": "home",
    "selected_mission": "all",
    "current_puzzle_id": None,
    "current_round": 1,
    "hint_used": False,
    "feedback": None,
    "timer_started": None,
    "selected_zone": "Server Room",
    "selected_suspect": "Dr. Evelyn Cross",
    "pinned_evidence": [],
    "ending": None,
    "last_awarded_xp": 0,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


def safe(value):
    return html.escape(str(value or ""))


# =========================================================
# DATABASE HELPERS
# =========================================================

def get_puzzle_by_id(puzzle_id):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM puzzles WHERE puzzle_id = ?",
            (puzzle_id,),
        ).fetchone()

    return dict(row) if row else None


def get_mission_puzzles(mission_key):
    mission = MISSIONS.get(mission_key, MISSIONS["all"])
    ids = mission["ids"]

    if not ids:
        return []

    placeholders = ",".join("?" for _ in ids)

    with get_connection() as connection:
        rows = connection.execute(
            f"SELECT * FROM puzzles WHERE puzzle_id IN ({placeholders})",
            ids,
        ).fetchall()

    puzzle_map = {row["puzzle_id"]: dict(row) for row in rows}

    # Preserve mission configuration order for predictable displays.
    return [
        puzzle_map[puzzle_id]
        for puzzle_id in ids
        if puzzle_id in puzzle_map
    ]


def get_completed_ids(mission_key, round_number):
    ids = MISSIONS.get(mission_key, MISSIONS["all"])["ids"]

    if not ids:
        return set()

    placeholders = ",".join("?" for _ in ids)

    with get_connection() as connection:
        rows = connection.execute(
            f"""
            SELECT puzzle_id
            FROM puzzle_completions
            WHERE round_number = ?
              AND puzzle_id IN ({placeholders})
            """,
            [round_number, *ids],
        ).fetchall()

    return {row["puzzle_id"] for row in rows}


def choose_next_puzzle(mission_key):
    puzzles = get_mission_puzzles(mission_key)

    if not puzzles:
        return None

    round_number = max(1, int(st.session_state.current_round))

    # Continue into a new cycle only when the current mission's
    # entire puzzle pool has been completed for that round.
    for _ in range(100):
        completed = get_completed_ids(mission_key, round_number)
        remaining = [
            puzzle for puzzle in puzzles
            if puzzle["puzzle_id"] not in completed
        ]

        if remaining:
            return random.choice(remaining), round_number

        round_number += 1

    return None


def start_next_puzzle():
    result = choose_next_puzzle(st.session_state.selected_mission)

    if result is None:
        st.session_state.game_screen = "mission_empty"
        return

    puzzle, round_number = result

    st.session_state.current_puzzle_id = puzzle["puzzle_id"]
    st.session_state.current_round = round_number
    st.session_state.hint_used = False
    st.session_state.feedback = None
    st.session_state.timer_started = (
        time.time()
        if MISSIONS[st.session_state.selected_mission]["timer"]
        else None
    )
    st.session_state.game_screen = "playing"


def start_mission(mission_key):
    st.session_state.selected_mission = mission_key
    st.session_state.current_round = 1
    st.session_state.current_puzzle_id = None
    st.session_state.hint_used = False
    st.session_state.feedback = None
    st.session_state.timer_started = None
    st.session_state.ending = None
    start_next_puzzle()


def reset_to_home():
    st.session_state.game_screen = "home"
    st.session_state.current_puzzle_id = None
    st.session_state.hint_used = False
    st.session_state.feedback = None
    st.session_state.timer_started = None
    st.session_state.ending = None


def answer_is_correct(answer, expected):
    return answer.strip().casefold() == str(expected).strip().casefold()


def get_archive():
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT
                c.id,
                c.puzzle_id,
                c.round_number,
                c.completed_at,
                p.title,
                p.category,
                p.difficulty,
                p.xp_reward
            FROM puzzle_completions AS c
            JOIN puzzles AS p ON p.puzzle_id = c.puzzle_id
            ORDER BY c.id DESC
        """).fetchall()

    return [dict(row) for row in rows]


def get_completed_puzzle_ids():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT DISTINCT puzzle_id FROM puzzle_completions"
        ).fetchall()

    return {row["puzzle_id"] for row in rows}


def get_ending(xp):
    if xp >= 1200:
        return (
            "GHOST PROTOCOL",
            "You uncovered the complete fictional operation. "
            "Your investigation earned the highest clearance.",
        )
    if xp >= 500:
        return (
            "THE SHADOW SURVIVES",
            "You recovered critical evidence, but some questions remain.",
        )
    return (
        "THE CASE REMAINS OPEN",
        "You made progress. Return to the evidence and continue investigating.",
    )


# =========================================================
# STYLING
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Inter:wght@400;500;600;700;800&display=swap');

.stApp {
    background:
        radial-gradient(ellipse at 10% 0%, #10251f 0%, transparent 35%),
        #070b0d;
    color: #e5f2ed;
    font-family: 'Inter', sans-serif;
}
[data-testid="stSidebar"] {
    background: #0b1113;
    border-right: 1px solid #20372e;
}
.block-container {
    max-width: 1200px;
    padding-top: 1.7rem;
    padding-bottom: 3rem;
}
h1, h2, h3 { color: #e7fff2 !important; }
.eyebrow {
    font-family: 'Share Tech Mono', monospace;
    color: #57f59a;
    letter-spacing: 2px;
    font-size: 12px;
}
.hero {
    padding: 26px;
    border: 1px solid #244535;
    border-radius: 16px;
    background: linear-gradient(120deg, #101e19, #0a1012 70%);
    margin-bottom: 20px;
}
.panel {
    padding: 18px;
    border: 1px solid #233a30;
    border-radius: 14px;
    background: #0c1313;
    margin-bottom: 12px;
}
.terminal {
    background: #050908;
    border: 1px solid #24513d;
    border-radius: 12px;
    padding: 20px;
    font-family: 'Share Tech Mono', monospace;
    color: #57f59a;
    line-height: 1.9;
    overflow-wrap: anywhere;
}
.map-zone {
    border: 1px solid #2a4a39;
    background: #101b17;
    border-radius: 10px;
    padding: 12px;
    text-align: center;
    margin-bottom: 8px;
}
div.stButton > button, div.stFormSubmitButton > button {
    background: #123d29;
    color: #8bffb8;
    border: 1px solid #2a8251;
    border-radius: 8px;
    font-weight: 700;
    min-height: 43px;
    width: 100%;
    transition: 0.2s ease;
}
div.stButton > button:hover, div.stFormSubmitButton > button:hover {
    background: #1c593a;
    color: white;
    border-color: #58f59a;
}
div[data-testid="stMetric"] {
    background: #0c1412;
    border: 1px solid #233a30;
    padding: 12px;
    border-radius: 12px;
}
div[data-testid="stProgressBar"] > div > div {
    background-color: #42e88b;
}
[data-testid="stForm"] {
    border: 1px solid #233a30;
    border-radius: 12px;
    padding: 16px;
}
footer {visibility: hidden;}
@media (max-width: 700px) {
    .block-container { padding: 1rem 0.8rem 2rem; }
    .hero { padding: 17px; }
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# HEADER AND SIDEBAR
# =========================================================

player = sync_player_rank()
total_puzzles = get_puzzle_count()

with st.sidebar:
    st.markdown('<p class="eyebrow">SHADOW // NETWORK</p>', unsafe_allow_html=True)
    st.title("SHADOW")
    st.caption("PROTOCOL OPERATIONS")
    st.divider()

    st.markdown("### AGENT PROFILE")
    st.write("**Codename:** Agent")
    st.write(f"**Rank:** {player['rank']}")
    st.progress(min(player["xp"] / 1200, 1.0))
    st.caption(f"{player['xp']} XP / 1200 XP")

    st.markdown("#### Rank Progression")
    next_rank = next(
        ((threshold, name) for threshold, name in reversed(RANKS)
         if threshold > player["xp"]),
        None,
    )

    if player["xp"] >= 1200:
        st.success("Maximum rank achieved.")
    else:
        higher_ranks = [
            (threshold, name)
            for threshold, name in RANKS
            if threshold > player["xp"]
        ]
        if higher_ranks:
            target_threshold, target_name = min(higher_ranks)
            st.caption(
                f"Next rank: {target_name} — "
                f"{max(0, target_threshold - player['xp'])} XP remaining"
            )

    st.divider()
    st.markdown("### SYSTEM STATUS")
    st.success("Simulation Online")
    st.caption("Fictional puzzles only. No external systems are accessed.")

    st.divider()
    page = st.radio(
        "NAVIGATION",
        ["Command Center", "Crime Scene", "Suspect Board",
         "Evidence Inventory", "Mission Archive", "About"],
        key="navigation_page",
    )

st.markdown("""
<div class="hero">
    <div class="eyebrow">CYBER OPERATIONS DIVISION</div>
    <h1 style="font-size:clamp(30px,5vw,44px); margin:12px 0;">
        SHADOW PROTOCOL
    </h1>
    <p style="color:#a8beb3; font-size:16px;">
        Think strategically. Decode the unknown. Complete the mission.
    </p>
</div>
""", unsafe_allow_html=True)


# =========================================================
# COMMAND CENTER
# =========================================================

if page == "Command Center":
    player = sync_player_rank()

    col1, col2, col3 = st.columns(3)
    col1.metric("AGENT RANK", player["rank"])
    col2.metric("TOTAL XP", player["xp"])
    col3.metric("PUZZLES CLEARED", player["completed_missions"])

    if st.session_state.game_screen == "home":
        st.subheader("Operation Selection")
        st.write("Choose a mission to enter its investigation puzzle pool.")

        mission_keys = ["ghost", "identity", "file", "firewall", "detective"]

        for start in range(0, len(mission_keys), 2):
            cols = st.columns(2)

            for col, mission_key in zip(cols, mission_keys[start:start + 2]):
                mission = MISSIONS[mission_key]

                with col:
                    st.markdown(
                        f"""
                        <div class="panel">
                            <div class="eyebrow">{safe(mission['category'])}</div>
                            <h3>{safe(mission['name'])}</h3>
                            <p>{safe(mission['description'])}</p>
                            <p style="color:#8ca99a;font-size:13px;">
                                {len(mission['ids'])} configured challenges
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    if st.button(
                        f"START {mission['name'].upper()}",
                        key=f"start_{mission_key}",
                        use_container_width=True,
                    ):
                        start_mission(mission_key)
                        st.rerun()

        st.divider()
        st.markdown("### FULL PUZZLE LIBRARY")
        st.write(
            f"{total_puzzles} puzzles are available in the database. "
            "Complete the library in randomized order."
        )

        if st.button("START ALL OPERATIONS", key="start_all"):
            start_mission("all")
            st.rerun()

        st.markdown("### CASE STATUS")
        st.markdown(
            """
            <div class="panel">
                <div class="eyebrow">PRIMARY INVESTIGATION</div>
                <h3>The Missing Archive</h3>
                <p>
                    A fictional intelligence archive has disappeared.
                    Decode recovered transmissions, compare suspect accounts,
                    and collect enough evidence to determine the outcome.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    elif st.session_state.game_screen == "playing":
        puzzle = get_puzzle_by_id(st.session_state.current_puzzle_id)

        if not puzzle:
            st.error("This puzzle could not be loaded from the database.")
            if st.button("RETURN TO COMMAND CENTER"):
                reset_to_home()
                st.rerun()
        else:
            mission = MISSIONS[st.session_state.selected_mission]
            completed_ids = get_completed_ids(
                st.session_state.selected_mission,
                st.session_state.current_round,
            )
            mission_total = len(get_mission_puzzles(st.session_state.selected_mission))
            progress_count = min(len(completed_ids), mission_total)

            st.markdown(
                f'<div class="eyebrow">{safe(mission["name"])} '
                f'// ROUND {st.session_state.current_round}</div>',
                unsafe_allow_html=True,
            )
            st.title(puzzle["title"])

            st.progress(
                progress_count / mission_total if mission_total else 0,
                text=f"Current cycle: {progress_count}/{mission_total} puzzles completed",
            )

            meta1, meta2, meta3 = st.columns(3)
            meta1.metric("DIFFICULTY", puzzle["difficulty"])
            meta2.metric("XP REWARD", puzzle["xp_reward"])
            meta3.metric("HINT", "Used" if st.session_state.hint_used else "Available")

            st.markdown(
                f"""
                <div class="panel">
                    <div class="eyebrow">MISSION BRIEFING</div>
                    <p>{safe(puzzle['story'])}</p>
                    <b>OBJECTIVE</b>
                    <p>{safe(puzzle['clue'])}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div class="terminal">
                    <div class="eyebrow">INCOMING DATA // {safe(puzzle['category'])}</div>
                    <h2 style="color:#57f59a !important;overflow-wrap:anywhere;">
                        {safe(puzzle['message'])}
                    </h2>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Timed firewall challenges: 120 seconds.
            if mission["timer"]:
                if st.session_state.timer_started is None:
                    st.session_state.timer_started = time.time()

                elapsed = int(time.time() - st.session_state.timer_started)
                remaining_seconds = max(0, 120 - elapsed)
                st.markdown("### TIMED SECURITY CHECKPOINT")
                st.progress(remaining_seconds / 120)
                st.write(f"Time remaining: **{remaining_seconds} seconds**")

                if remaining_seconds == 0:
                    st.error("Time expired. Restart this challenge to try again.")
                    if st.button("RESTART TIMED CHALLENGE", key="restart_timer"):
                        st.session_state.timer_started = time.time()
                        st.session_state.feedback = None
                        st.rerun()

                if st.button("REFRESH TIMER", key="refresh_timer"):
                    st.rerun()

            hint_col, info_col = st.columns([1, 3])

            with hint_col:
                if st.button("REQUEST HINT", key="request_hint"):
                    st.session_state.hint_used = True
                    st.rerun()

            if st.session_state.hint_used:
                st.info(f"Investigation hint: {puzzle['hint']}")

            if st.session_state.feedback:
                kind, message = st.session_state.feedback
                if kind == "error":
                    st.error(message)

            timer_expired = (
                mission["timer"]
                and st.session_state.timer_started is not None
                and time.time() - st.session_state.timer_started >= 120
            )

            with st.form(
                f"answer_form_{puzzle['puzzle_id']}_{st.session_state.current_round}",
                clear_on_submit=True,
            ):
                answer = st.text_input(
                    "ENTER YOUR ANSWER",
                    placeholder="Type your decoded answer...",
                    disabled=timer_expired,
                )
                submitted = st.form_submit_button(
                    "SUBMIT ANSWER",
                    use_container_width=True,
                    disabled=timer_expired,
                )

            if submitted:
                if not answer.strip():
                    st.session_state.feedback = (
                        "error", "Enter an answer before submitting."
                    )
                    st.rerun()

                elif answer_is_correct(answer, puzzle["answer"]):
                    awarded = complete_puzzle(
                        puzzle["puzzle_id"],
                        st.session_state.current_round,
                    )

                    player = sync_player_rank()
                    st.session_state.last_awarded_xp = (
                        puzzle["xp_reward"] if awarded else 0
                    )
                    st.session_state.feedback = (
                        "success",
                        f"ACCESS GRANTED — {puzzle['xp_reward']} XP earned."
                        if awarded else
                        "Correct answer. This challenge has already been rewarded.",
                    )
                    st.session_state.game_screen = "won"
                    st.rerun()

                else:
                    st.session_state.feedback = (
                        "error",
                        "ACCESS DENIED. Recheck the clue and try again.",
                    )
                    st.rerun()

            st.divider()
            left, right = st.columns(2)

            with left:
                if st.button("CHANGE MISSION", key="change_mission"):
                    reset_to_home()
                    st.rerun()

            with right:
                if st.button("END SESSION", key="exit_playing"):
                    player = sync_player_rank()
                    st.session_state.ending = get_ending(player["xp"])
                    st.session_state.game_screen = "exit"
                    st.rerun()

    elif st.session_state.game_screen == "won":
        st.markdown("""
        <div class="hero">
            <div class="eyebrow">MISSION STATUS // SUCCESS</div>
            <h1>CHALLENGE COMPLETED</h1>
            <p>The evidence has been processed successfully.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.feedback:
            st.success(st.session_state.feedback[1])

        player = sync_player_rank()
        col1, col2 = st.columns(2)
        col1.metric("TOTAL XP", player["xp"])
        col2.metric("CURRENT RANK", player["rank"])

        st.caption(
            f"Last successful reward: {st.session_state.last_awarded_xp} XP"
        )

        next_col, choose_col = st.columns(2)

        with next_col:
            if st.button("NEXT CHALLENGE", key="next_puzzle"):
                start_next_puzzle()
                st.rerun()

        with choose_col:
            if st.button("CHOOSE ANOTHER MISSION", key="choose_another"):
                reset_to_home()
                st.rerun()

        if st.button("END SESSION", key="exit_won"):
            st.session_state.ending = get_ending(player["xp"])
            st.session_state.game_screen = "exit"
            st.rerun()

    elif st.session_state.game_screen == "mission_empty":
        mission = MISSIONS[st.session_state.selected_mission]
        st.title("MISSION CYCLE COMPLETE")
        st.write(
            f"You have completed the current cycle for **{mission['name']}**."
        )
        st.write("Start the next cycle or return to the operation selection.")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("START NEXT CYCLE", key="next_cycle"):
                start_next_puzzle()
                st.rerun()

        with col2:
            if st.button("RETURN TO COMMAND CENTER", key="other_mission"):
                reset_to_home()
                st.rerun()

    elif st.session_state.game_screen == "exit":
        player = sync_player_rank()
        ending_title, ending_description = (
            st.session_state.ending or get_ending(player["xp"])
        )

        st.markdown(
            f"""
            <div class="hero">
                <div class="eyebrow">SESSION TERMINATED</div>
                <h1>THANK YOU FOR PLAYING</h1>
                <h3>{safe(ending_title)}</h3>
                <p>{safe(ending_description)}</p>
                <p>Your progress is stored in the local SQLite database.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("RETURN TO COMMAND CENTER", key="play_again_exit"):
            reset_to_home()
            st.rerun()


# =========================================================
# CRIME SCENE
# =========================================================

elif page == "Crime Scene":
    st.subheader("Crime Scene Investigation")
    st.write(
        "Select a location to review its fictional case notes. "
        "Use these notes alongside the puzzle evidence."
    )

    zones = {
        "Server Room": {
            "status": "Access log anomaly",
            "details": "A simulated access record contains a gap in its timeline.",
            "lead": "Compare the timeline with the recovered archive.",
        },
        "Research Lab": {
            "status": "Missing archive",
            "details": "A classified research archive was reported missing.",
            "lead": "Decode the archive message in Secret File.",
        },
        "Security Console": {
            "status": "Unusual sequence",
            "details": "The fictional security console recorded an unusual pattern.",
            "lead": "Try the Firewall Alert logic challenges.",
        },
        "Radio Station": {
            "status": "Intercepted transmission",
            "details": "An unidentified transmission was recorded before the incident.",
            "lead": "Decode the signal in Ghost Signal.",
        },
    }

    map_col, detail_col = st.columns([1.1, 1])

    with map_col:
        st.markdown(
            """
            <div class="panel">
                <div class="eyebrow">FACILITY MAP // SIMULATED</div>
                <p style="color:#8ca99a;">
                    Select a zone below to inspect its notes.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for zone in zones:
            if st.button(
                f"INSPECT: {zone.upper()}",
                key=f"zone_{zone}",
            ):
                st.session_state.selected_zone = zone

    with detail_col:
        zone = st.session_state.selected_zone
        details = zones[zone]

        st.markdown(
            f"""
            <div class="panel">
                <div class="eyebrow">SELECTED LOCATION</div>
                <h3>{safe(zone)}</h3>
                <p><b>Status:</b> {safe(details['status'])}</p>
                <p>{safe(details['details'])}</p>
                <p style="color:#57f59a;">
                    LEAD: {safe(details['lead'])}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("OPEN RELATED MISSION", key="open_related"):
            related = {
                "Server Room": "detective",
                "Research Lab": "file",
                "Security Console": "firewall",
                "Radio Station": "ghost",
            }
            start_mission(related[zone])
            st.session_state.navigation_page = "Command Center"
            st.rerun()


# =========================================================
# SUSPECT RELATIONSHIP BOARD
# =========================================================

elif page == "Suspect Board":
    st.subheader("Suspect Relationship Board")
    st.write(
        "These suspects are fictional characters. Review their statements "
        "and compare them with evidence you uncover during missions."
    )

    suspect_names = list(SUSPECTS.keys())
    selected = st.selectbox(
        "SELECT A SUSPECT",
        suspect_names,
        key="suspect_selector",
    )
    st.session_state.selected_suspect = selected

    suspect = SUSPECTS[selected]

    st.markdown(
        f"""
        <div class="panel">
            <div class="eyebrow">PERSON OF INTEREST</div>
            <h2>{safe(selected)}</h2>
            <p><b>Role:</b> {safe(suspect['role'])}</p>
            <p><b>Possible motive:</b> {safe(suspect['motive'])}</p>
            <p><b>Claimed alibi:</b> {safe(suspect['alibi'])}</p>
            <p><b>Investigation lead:</b> {safe(suspect['lead'])}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Relationship Overview")
    st.markdown("""
    <div class="panel">
        <p><b>Dr. Evelyn Cross</b> — Research archive owner</p>
        <p style="color:#57f59a;">↕ Research access relationship</p>
        <p><b>Marcus Vale</b> — Systems access administrator</p>
        <p style="color:#57f59a;">↕ Security monitoring relationship</p>
        <p><b>Nadia Frost</b> — Security analyst</p>
        <hr>
        <p style="color:#a8beb3;">
            Relationships are investigative leads, not proof of guilt.
            Resolve the fictional case using the available evidence.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("INVESTIGATE THIS CASE", key="suspect_to_detective"):
        start_mission("detective")
        st.session_state.navigation_page = "Command Center"
        st.rerun()


# =========================================================
# EVIDENCE INVENTORY
# =========================================================

elif page == "Evidence Inventory":
    st.subheader("Evidence Inventory")
    st.write(
        "Evidence is unlocked by solving puzzles. Pin useful records "
        "to keep track of your investigation."
    )

    completed_ids = get_completed_puzzle_ids()

    with get_connection() as connection:
        if completed_ids:
            placeholders = ",".join("?" for _ in completed_ids)
            rows = connection.execute(
                f"""
                SELECT puzzle_id, title, category, difficulty,
                       message, clue, story, xp_reward
                FROM puzzles
                WHERE puzzle_id IN ({placeholders})
                ORDER BY title
                """,
                list(completed_ids),
            ).fetchall()
        else:
            rows = []

    evidence = [dict(row) for row in rows]

    st.metric("EVIDENCE RECORDS UNLOCKED", len(evidence))

    if not evidence:
        st.info("No evidence unlocked yet. Complete a puzzle to collect your first record.")
    else:
        evidence_names = [
            f"{item['title']} ({item['puzzle_id']})"
            for item in evidence
        ]

        selected_evidence = st.selectbox(
            "SELECT EVIDENCE",
            evidence_names,
            key="evidence_selector",
        )

        selected_index = evidence_names.index(selected_evidence)
        item = evidence[selected_index]

        st.markdown(
            f"""
            <div class="panel">
                <div class="eyebrow">EVIDENCE RECORD // {safe(item['puzzle_id'])}</div>
                <h3>{safe(item['title'])}</h3>
                <p><b>Category:</b> {safe(item['category'])}</p>
                <p><b>Difficulty:</b> {safe(item['difficulty'])}</p>
                <p><b>Recovered data:</b> {safe(item['message'])}</p>
                <p><b>Case note:</b> {safe(item['story'])}</p>
                <p><b>Original clue:</b> {safe(item['clue'])}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        pinned = item["puzzle_id"] in st.session_state.pinned_evidence

        if not pinned:
            if st.button("PIN EVIDENCE TO CASE", key="pin_evidence"):
                st.session_state.pinned_evidence.append(item["puzzle_id"])
                st.rerun()
        else:
            st.success("This record is pinned to your case board.")
            if st.button("UNPIN EVIDENCE", key="unpin_evidence"):
                st.session_state.pinned_evidence.remove(item["puzzle_id"])
                st.rerun()

        st.markdown("### Pinned Evidence")
        if st.session_state.pinned_evidence:
            for puzzle_id in st.session_state.pinned_evidence:
                pinned_item = get_puzzle_by_id(puzzle_id)
                if pinned_item:
                    st.write(f"• {pinned_item['title']} — {puzzle_id}")
        else:
            st.caption("No evidence pinned yet.")


# =========================================================
# MISSION ARCHIVE
# =========================================================

elif page == "Mission Archive":
    player = sync_player_rank()
    archive = get_archive()

    st.subheader("Mission Archive")
    st.write("Completed challenges and timestamps are recorded in SQLite.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Recorded Completions", player["completed_missions"])
    col2.metric("Total XP", player["xp"])
    col3.metric("Current Rank", player["rank"])

    if archive:
        st.markdown("### COMPLETED OPERATIONS")

        for item in archive:
            st.markdown(
                f"""
                <div class="panel">
                    <b>{safe(item['title'])}</b>
                    <p class="eyebrow">
                        {safe(item['puzzle_id'])} //
                        {safe(item['category'])} //
                        {safe(item['difficulty'])}
                    </p>
                    <p style="color:#a8beb3;">
                        Round {item['round_number']} ·
                        {safe(item['completed_at'])}
                    </p>
                    <p style="color:#57f59a;">
                        Reward: {item['xp_reward']} XP
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No completed puzzles yet. Select a mission to begin.")


# =========================================================
# ABOUT
# =========================================================

elif page == "About":
    st.subheader("About Shadow Protocol")

    st.markdown("""
    **Shadow Protocol** is a fictional cyber investigation and puzzle game.

    Features include:
    - Five focused missions and a complete puzzle library
    - Cipher decoding, binary, Morse, hexadecimal and logic challenges
    - Evidence inventory and interactive crime-scene locations
    - Fictional suspect relationship board
    - Timed Firewall Alert challenges
    - XP, six agent ranks, and multiple endings
    - SQLite-based puzzle completion history

    All scenarios are fictional. The game does not scan networks,
    access external systems, or perform real-world security operations.

    **Technology:** Python, Streamlit, SQLite.
    **AI services:** None.
    **External AI runtime:** None.
    """)


# =========================================================
# FOOTER
# =========================================================

st.divider()
st.markdown(
    """
    <div style="text-align:center;padding:14px 0 8px 0;">
        <div class="eyebrow">SHADOW PROTOCOL // SIMULATION ENVIRONMENT</div>
        <p style="color:#8ca99a;font-size:13px;margin-top:10px;">
            Engineered to Perfection by Noor Shaikh
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
