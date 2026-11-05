import re
from datetime import date, datetime


MONTHS = {
    "january": 1,
    "jan": 1,
    "february": 2,
    "feb": 2,
    "march": 3,
    "mar": 3,
    "april": 4,
    "apr": 4,
    "may": 5,
    "june": 6,
    "jun": 6,
    "july": 7,
    "jul": 7,
    "august": 8,
    "aug": 8,
    "september": 9,
    "sep": 9,
    "sept": 9,
    "october": 10,
    "oct": 10,
    "november": 11,
    "nov": 11,
    "december": 12,
    "dec": 12,
}


# Words/phrases that strongly suggest the date
# is worth asking the user about.
IMPORTANT_DATE_KEYWORDS = [
    "birthday",
    "birth day",
    "anniversary",
    "exam",
    "examination",
    "test",
    "deadline",
    "appointment",
    "meeting",
    "interview",
    "trip",
    "travel",
    "flight",
    "vacation",
    "holiday",
    "wedding",
    "engagement",
    "farewell",
    "graduation",
    "result",
    "event",
    "function",
    "ceremony",
    "doctor",
    "hospital",
    "concert",
    "competition",
    "presentation",
    "submission",
    "due date",
    "special day",
    "special occasion",
]


def extract_important_dates(text):
    """
    Detect potentially important dates from normal conversation.

    Examples:
        My best friend's birthday is 15 October.
        Mom's birthday is October 20.
        Our anniversary is 12 December.
        My exam is on 5 March.
        I have an interview on 7 November.

    The function DOES NOT save anything to the database.
    It only returns suggestions for user confirmation.
    """

    if not isinstance(text, str):
        return []

    text = text.strip()

    if not text:
        return []

    results = []

    # ---------------------------------------------------------
    # PATTERN 1
    #
    # 15 October
    # 15th October
    # 15 October 2026
    # ---------------------------------------------------------

    pattern_day_month = re.compile(
        r"\b"
        r"(\d{1,2})"
        r"(?:st|nd|rd|th)?"
        r"\s+"
        r"(January|Jan|February|Feb|March|Mar|April|Apr|May|"
        r"June|Jun|July|Jul|August|Aug|September|Sep|Sept|"
        r"October|Oct|November|Nov|December|Dec)"
        r"(?:\s+(\d{4}))?"
        r"\b",
        re.IGNORECASE
    )

    for match in pattern_day_month.finditer(text):

        day = int(match.group(1))
        month_name = match.group(2).lower()
        year = match.group(3)

        month = MONTHS.get(month_name)

        if month is None:
            continue

        result = build_date_result(
            text=text,
            day=day,
            month=month,
            year=year,
            date_position=match.start()
        )

        if result:
            results.append(result)


    # ---------------------------------------------------------
    # PATTERN 2
    #
    # October 15
    # October 15th
    # October 15 2026
    # ---------------------------------------------------------

    pattern_month_day = re.compile(
        r"\b"
        r"(January|Jan|February|Feb|March|Mar|April|Apr|May|"
        r"June|Jun|July|Jul|August|Aug|September|Sep|Sept|"
        r"October|Oct|November|Nov|December|Dec)"
        r"\s+"
        r"(\d{1,2})"
        r"(?:st|nd|rd|th)?"
        r"(?:\s+(\d{4}))?"
        r"\b",
        re.IGNORECASE
    )

    for match in pattern_month_day.finditer(text):

        month_name = match.group(1).lower()
        day = int(match.group(2))
        year = match.group(3)

        month = MONTHS.get(month_name)

        if month is None:
            continue

        result = build_date_result(
            text=text,
            day=day,
            month=month,
            year=year,
            date_position=match.start()
        )

        if result:
            results.append(result)


    # ---------------------------------------------------------
    # REMOVE DUPLICATES
    # ---------------------------------------------------------

    unique_results = []

    seen = set()

    for item in results:

        key = (
            item["date"],
            item["title"]
        )

        if key not in seen:

            seen.add(key)

            unique_results.append(item)


    return unique_results


def build_date_result(
    text,
    day,
    month,
    year,
    date_position
):
    """
    Validate the date and decide whether it looks important.
    """

    # ---------------------------------------------------------
    # Check whether this sentence actually indicates
    # an important date.
    # ---------------------------------------------------------

    sentence = get_date_sentence(
        text,
        date_position
    )

    sentence_lower = sentence.lower()

    is_important = any(
        keyword in sentence_lower
        for keyword in IMPORTANT_DATE_KEYWORDS
    )

    if not is_important:
        return None


    # ---------------------------------------------------------
    # Determine whether an explicit year was provided.
    # ---------------------------------------------------------

    if year:

        year = int(year)

        try:

            parsed_date = date(
                year,
                month,
                day
            )

        except ValueError:

            return None

    else:

        # -----------------------------------------------------
        # No year was provided.
        #
        # For recurring dates such as birthdays and
        # anniversaries, use the next occurrence.
        # -----------------------------------------------------

        today = date.today()

        try:

            parsed_date = date(
                today.year,
                month,
                day
            )

        except ValueError:

            return None


        # If this year's occurrence has already passed,
        # use next year.
        if parsed_date < today:

            try:

                parsed_date = date(
                    today.year + 1,
                    month,
                    day
                )

            except ValueError:

                return None


    # ---------------------------------------------------------
    # Generate a meaningful title.
    # ---------------------------------------------------------

    title = extract_date_title(
        text,
        date_position
    )


    # ---------------------------------------------------------
    # Determine whether this looks recurring.
    # ---------------------------------------------------------

    recurring_keywords = [
        "birthday",
        "anniversary",
        "every year",
        "yearly",
        "annual",
    ]

    is_recurring = any(
        keyword in sentence_lower
        for keyword in recurring_keywords
    )


    note = "Automatically detected from conversation."

    if is_recurring:

        note = (
            "Automatically detected from conversation. "
            "This date may repeat every year."
        )


    return {
        "date": str(parsed_date),
        "title": title,
        "note": note
    }


def get_date_sentence(text, date_position):
    """
    Get the sentence containing the detected date.
    """

    before_date = text[:date_position]
    after_date = text[date_position:]

    # Find the nearest sentence boundary before the date.
    before_parts = re.split(
        r"[.!?]",
        before_date
    )

    before_sentence = before_parts[-1].strip()


    # Find the nearest sentence boundary after the date.
    after_match = re.search(
        r"[.!?]",
        after_date
    )

    if after_match:

        after_sentence = after_date[
            :after_match.start()
        ].strip()

    else:

        after_sentence = after_date.strip()


    if before_sentence and after_sentence:

        return (
            before_sentence
            + " "
            + after_sentence
        )

    if before_sentence:

        return before_sentence

    return after_sentence


def extract_date_title(text, date_position):
    """
    Try to understand what the date is about.

    Examples:

        "My best friend's birthday is 15 October."
        → "Best friend's birthday"

        "My parents anniversary is on 4 October."
        → "Parents anniversary"

        "I have an exam on 12 December."
        → "I have an exam"
    """

    sentence = get_date_sentence(
        text,
        date_position
    ).strip()


    if not sentence:

        return "Important Date"


    # ---------------------------------------------------------
    # Remove the actual date from the title.
    # ---------------------------------------------------------

    sentence = re.sub(
        r"\b\d{1,2}(?:st|nd|rd|th)?\b",
        "",
        sentence,
        flags=re.IGNORECASE
    )

    sentence = re.sub(
        r"\b(?:January|Jan|February|Feb|March|Mar|April|Apr|"
        r"May|June|Jun|July|Jul|August|Aug|September|Sep|"
        r"Sept|October|Oct|November|Nov|December|Dec)\b",
        "",
        sentence,
        flags=re.IGNORECASE
    )


    # ---------------------------------------------------------
    # Remove common connecting words.
    # ---------------------------------------------------------

    sentence = re.sub(
        r"\b(is|on|at|for|the|my|our|his|her|their|"
        r"a|an|and|of)\b",
        " ",
        sentence,
        flags=re.IGNORECASE
    )


    # ---------------------------------------------------------
    # Remove common date-related filler.
    # ---------------------------------------------------------

    sentence = re.sub(
        r"\b(?:happens|falls|coming|comes)\b",
        " ",
        sentence,
        flags=re.IGNORECASE
    )


    # ---------------------------------------------------------
    # Clean extra spaces.
    # ---------------------------------------------------------

    sentence = re.sub(
        r"\s+",
        " ",
        sentence
    ).strip()


    if not sentence:

        return "Important Date"


    # ---------------------------------------------------------
    # Keep title reasonably short.
    # ---------------------------------------------------------

    if len(sentence) > 70:

        sentence = sentence[:70].strip()


    # ---------------------------------------------------------
    # Capitalize first letter.
    # ---------------------------------------------------------

    return (
        sentence[0].upper()
        + sentence[1:]
    )