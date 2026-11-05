from app.database.db import get_connection


# =========================================================
# CONVERSATIONS
# =========================================================

def create_conversation(title="New Conversation"):
    """
    Create a new conversation and return its ID.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO conversations (title)
        VALUES (?)
        """,
        (title,)
    )

    conversation_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return conversation_id


def get_conversations():
    """
    Return all conversations.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM conversations
        ORDER BY updated_at DESC
        """
    )

    conversations = cursor.fetchall()

    connection.close()

    return conversations


# =========================================================
# MESSAGES
# =========================================================

def save_message(
    conversation_id,
    role,
    content
):
    """
    Save a user or assistant message.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO messages
        (
            conversation_id,
            role,
            content
        )
        VALUES (?, ?, ?)
        """,
        (
            conversation_id,
            role,
            content
        )
    )

    cursor.execute(
        """
        UPDATE conversations
        SET updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (conversation_id,)
    )

    connection.commit()
    connection.close()


def get_messages(conversation_id):
    """
    Return all messages belonging to a conversation.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM messages
        WHERE conversation_id = ?
        ORDER BY created_at ASC
        """,
        (conversation_id,)
    )

    messages = cursor.fetchall()

    connection.close()

    return messages


# =========================================================
# MEMORIES
# =========================================================

def save_memory(
    title,
    note="",
    media_path="",
    memory_date="",
    memory_type="media"
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO memories
        (title, note, media_path, memory_date, memory_type)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            title,
            note,
            media_path,
            memory_date,
            memory_type
        )
    )

    memory_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return memory_id


def get_memories():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM memories
        WHERE memory_type = 'media'
        ORDER BY created_at DESC
        """
    )

    memories = cursor.fetchall()

    connection.close()

    return memories


# =========================================================
# IMPORTANT DATES
# =========================================================

def save_important_date(
    title,
    date,
    note="",
    reminder_enabled=True
):
    """
    Save an important date.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO important_dates
        (
            title,
            date,
            note,
            reminder_enabled
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            title,
            date,
            note,
            int(reminder_enabled)
        )
    )

    date_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return date_id


def get_important_dates():
    """
    Return all important dates.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM important_dates
        ORDER BY date ASC
        """
    )

    dates = cursor.fetchall()

    connection.close()

    return dates
# =========================================================
# UPDATE CONVERSATION TITLE
# =========================================================

def update_conversation_title(conversation_id, title):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE conversations
        SET title = ?
        WHERE id = ?
        """,
        (title, conversation_id)
    )

    connection.commit()
    connection.close()

# =========================================================
# LONG-TERM MEMORY
# =========================================================

def save_long_term_memory(
    title,
    content,
    category="general"
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO memories
        (
            title,
            note,
            media_path,
            memory_date,
            memory_type,
            category
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            title,
            content,
            "",
            "",
            "long_term",
            category
        )
    )

    memory_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return memory_id


def get_long_term_memories():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM memories
        WHERE memory_type = 'long_term'
        ORDER BY created_at DESC
        """
    )

    memories = cursor.fetchall()

    connection.close()

    return memories


def update_long_term_memory(
    memory_id,
    title,
    content
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE memories
        SET title = ?,
            note = ?
        WHERE id = ?
          AND memory_type = 'long_term'
        """,
        (
            title,
            content,
            memory_id
        )
    )

    connection.commit()
    connection.close()


def delete_long_term_memory(memory_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM memories
        WHERE id = ?
          AND memory_type = 'long_term'
        """,
        (memory_id,)
    )

    connection.commit()
    connection.close()


def delete_all_long_term_memories():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM memories
        WHERE memory_type = 'long_term'
        """
    )

    connection.commit()
    connection.close()


# =========================================================
# IMPORTANT DATE MANAGEMENT
# =========================================================

def update_important_date(
    date_id,
    title,
    date,
    note="",
    reminder_enabled=True
):
    """
    Update an important date.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE important_dates
        SET title = ?,
            date = ?,
            note = ?,
            reminder_enabled = ?
        WHERE id = ?
        """,
        (
            title,
            date,
            note,
            int(reminder_enabled),
            date_id
        )
    )

    connection.commit()
    connection.close()


def delete_important_date(date_id):
    """
    Permanently delete an important date.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM important_dates
        WHERE id = ?
        """,
        (date_id,)
    )

    connection.commit()
    connection.close()

# =========================================================
# MEMORY MANAGEMENT
# =========================================================

def update_memory(
    memory_id,
    title,
    note,
    memory_date
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE memories
        SET title = ?,
            note = ?,
            memory_date = ?
        WHERE id = ?
        """,
        (
            title,
            note,
            memory_date,
            memory_id
        )
    )

    connection.commit()
    connection.close()


def delete_memory(memory_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM memories
        WHERE id = ?
        """,
        (memory_id,)
    )

    connection.commit()
    connection.close()        

# =========================================================
# MEDIA MEMORY MANAGEMENT
# =========================================================

def update_memory(
    memory_id,
    title,
    note,
    memory_date
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE memories
        SET title = ?,
            note = ?,
            memory_date = ?
        WHERE id = ?
          AND memory_type = 'media'
        """,
        (
            title,
            note,
            memory_date,
            memory_id
        )
    )

    connection.commit()
    connection.close()


def delete_memory(memory_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM memories
        WHERE id = ?
          AND memory_type = 'media'
        """,
        (memory_id,)
    )

    connection.commit()
    connection.close()

# =========================================================
# CHECK EXISTING LONG-TERM MEMORY
# =========================================================

def long_term_memory_exists(title, content):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM memories
        WHERE memory_type = 'long_term'
          AND (
              title = ?
              OR note = ?
          )
        LIMIT 1
        """,
        (
            title,
            content
        )
    )

    result = cursor.fetchone()

    connection.close()

    return result is not None    

# =========================================================
# CONVERSATION MANAGEMENT
# =========================================================

def delete_conversation(conversation_id):

    connection = get_connection()
    cursor = connection.cursor()

    # Delete messages belonging to this conversation
    cursor.execute(
        """
        DELETE FROM messages
        WHERE conversation_id = ?
        """,
        (conversation_id,)
    )

    # Delete the conversation itself
    cursor.execute(
        """
        DELETE FROM conversations
        WHERE id = ?
        """,
        (conversation_id,)
    )

    connection.commit()
    connection.close()