from datetime import date

from app.database.models import get_important_dates


def get_todays_reminders():
    """
    Return important dates that match today's date.

    For recurring dates such as birthdays and anniversaries,
    the month and day are compared regardless of the stored year.
    """

    today = date.today()

    important_dates = get_important_dates()

    reminders = []

    for item in important_dates:

        # Only remind when reminders are enabled.
        if not item["reminder_enabled"]:
            continue

        stored_date = str(item["date"])

        try:
            year, month, day = map(
                int,
                stored_date.split("-")
            )

        except (ValueError, AttributeError):
            continue

        # Match month and day.
        #
        # This allows:
        # 2025-10-04
        # 2026-10-04
        # 2027-10-04
        #
        # to all represent the same recurring occasion.
        if month == today.month and day == today.day:

            reminders.append({
                "id": item["id"],
                "title": item["title"],
                "date": stored_date,
                "note": item["note"],
            })

    return reminders