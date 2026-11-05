import re


# =========================================================
# SAFETY LEVELS
# =========================================================

SAFE = "safe"
CAUTION = "caution"
HIGH_RISK = "high_risk"


# =========================================================
# HIGH-RISK PATTERNS
# =========================================================

SELF_HARM_PATTERNS = [
    r"\bkill myself\b",
    r"\bend my life\b",
    r"\btake my own life\b",
    r"\bsuicide\b",
    r"\bsuicidal\b",
    r"\bwant to die\b",
    r"\bi want to die\b",
    r"\bi wish i was dead\b",
    r"\bi wish i were dead\b",
    r"\bbetter off dead\b",
    r"\bno reason to live\b",
    r"\bdon't want to live\b",
    r"\bdo not want to live\b",
    r"\bhurt myself\b",
    r"\bharm myself\b",
    r"\bself harm\b",
    r"\bself-harm\b",
    r"\bmarna chahti\b",
    r"\bmarna chahta\b",
    r"\bkhud ko maar\b",
    r"\bkhud ko harm\b",
]


HARM_TO_OTHERS_PATTERNS = [
    r"\bkill (him|her|them)\b",
    r"\bkill someone\b",
    r"\bhurt (him|her|them)\b",
    r"\bhurt someone\b",
    r"\bharm (him|her|them)\b",
    r"\bharm someone\b",
    r"\battack (him|her|them)\b",
    r"\battack someone\b",
    r"\bwant to hurt\b",
    r"\bwant to kill\b",
    r"\bmaar dunga\b",
    r"\bmaar dungi\b",
    r"\bmaar dena\b",
]


IMMEDIATE_DANGER_PATTERNS = [
    r"\bin immediate danger\b",
    r"\bimmediately in danger\b",
    r"\bunsafe right now\b",
    r"\bnot safe right now\b",
    r"\bsomeone is attacking me\b",
    r"\bsomeone is hurting me\b",
    r"\bsomeone is threatening me\b",
    r"\bbeing attacked\b",
    r"\bbeing threatened\b",
    r"\bghar mein unsafe\b",
    r"\babhi danger mein\b",
    r"\babhi unsafe\b",
]


ABUSE_PATTERNS = [
    r"\bdomestic abuse\b",
    r"\bbeing abused\b",
    r"\bhe abuses me\b",
    r"\bshe abuses me\b",
    r"\bmy partner abuses me\b",
    r"\bmy husband abuses me\b",
    r"\bmy wife abuses me\b",
    r"\bhe hits me\b",
    r"\bshe hits me\b",
    r"\bthey hit me\b",
    r"\bhe beats me\b",
    r"\bshe beats me\b",
    r"\bthey beat me\b",
]


# =========================================================
# SAFETY RESPONSES
# =========================================================

HIGH_RISK_RESPONSE = """
I'm really sorry you're dealing with something this intense.

Your immediate safety matters more than continuing this conversation.

If you may hurt yourself, hurt someone else, or you are in immediate danger,
please move to a safer place and contact a trusted person who can stay with
you. You can also contact your local emergency service or a local crisis
support service.

If possible, don't stay alone with the situation right now.

I can stay focused on helping you think through the next safe step, but
Lumora cannot provide emergency intervention itself.
"""


ABUSE_RESPONSE = """
I'm sorry you're dealing with this.

If someone is hurting, threatening, or controlling you, your safety comes
first. If you are in immediate danger, move to a safer place if you can and
contact a trusted person or your local emergency service.

You do not have to handle an unsafe situation completely alone.

If you're safe right now, we can talk through what happened and consider
practical next steps without assuming things we don't know.
"""


CAUTION_RESPONSE = """
It sounds like things may be getting quite intense.

Before doing anything that could put you or someone else at risk, take a
moment and create some distance from the situation if you can. Consider
reaching out to someone you trust.

If there is immediate danger, contact your local emergency service or
appropriate crisis support.
"""


# =========================================================
# TEXT NORMALIZATION
# =========================================================

def normalize_text(text):
    """
    Normalize user input before safety pattern matching.
    """

    if not isinstance(text, str):
        return ""

    text = text.lower().strip()

    # Normalize repeated whitespace
    text = re.sub(r"\s+", " ", text)

    return text


# =========================================================
# PATTERN CHECKING
# =========================================================

def contains_pattern(text, patterns):
    """
    Return True if any safety pattern matches the text.
    """

    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return True

    return False


# =========================================================
# SAFETY CLASSIFICATION
# =========================================================

def check_safety(text):
    """
    Classify a message into:

        safe
        caution
        high_risk

    Returns a dictionary so the calling application can decide
    how to handle the response.
    """

    normalized_text = normalize_text(text)

    if not normalized_text:
        return {
            "level": SAFE,
            "category": None,
            "message": None,
        }


    # -----------------------------------------------------
    # Immediate danger
    # -----------------------------------------------------

    if contains_pattern(
        normalized_text,
        IMMEDIATE_DANGER_PATTERNS
    ):
        return {
            "level": HIGH_RISK,
            "category": "immediate_danger",
            "message": HIGH_RISK_RESPONSE,
        }


    # -----------------------------------------------------
    # Self-harm / suicide
    # -----------------------------------------------------

    if contains_pattern(
        normalized_text,
        SELF_HARM_PATTERNS
    ):
        return {
            "level": HIGH_RISK,
            "category": "self_harm",
            "message": HIGH_RISK_RESPONSE,
        }


    # -----------------------------------------------------
    # Harm to others
    # -----------------------------------------------------

    if contains_pattern(
        normalized_text,
        HARM_TO_OTHERS_PATTERNS
    ):
        return {
            "level": HIGH_RISK,
            "category": "harm_to_others",
            "message": HIGH_RISK_RESPONSE,
        }


    # -----------------------------------------------------
    # Abuse
    # -----------------------------------------------------

    if contains_pattern(
        normalized_text,
        ABUSE_PATTERNS
    ):
        return {
            "level": CAUTION,
            "category": "abuse",
            "message": ABUSE_RESPONSE,
        }


    # -----------------------------------------------------
    # General caution
    # -----------------------------------------------------

    caution_words = [
        "i can't cope",
        "i cannot cope",
        "completely hopeless",
        "feel completely hopeless",
        "i feel trapped",
        "i feel helpless",
        "nothing matters anymore",
        "life feels pointless",
        "bahut hopeless",
        "bahut helpless",
        "sab khatam lag raha",
    ]

    if any(
        phrase in normalized_text
        for phrase in caution_words
    ):
        return {
            "level": CAUTION,
            "category": "emotional_distress",
            "message": CAUTION_RESPONSE,
        }


    # -----------------------------------------------------
    # Normal conversation
    # -----------------------------------------------------

    return {
        "level": SAFE,
        "category": None,
        "message": None,
    }


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def is_high_risk(text):
    """
    Quickly check whether a message is high risk.
    """

    result = check_safety(text)

    return result["level"] == HIGH_RISK


def is_caution(text):
    """
    Quickly check whether a message requires caution.
    """

    result = check_safety(text)

    return result["level"] == CAUTION