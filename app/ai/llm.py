import os
import time
import random

from dotenv import load_dotenv
from google import genai
from google.genai import types


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    # Streamlit Cloud: key set under Manage app → Settings → Secrets
    try:
        import streamlit as st
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        api_key = None

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is missing. Add it to your .env file, "
        "or to Secrets in Streamlit Cloud (Manage app → Settings → Secrets)."
    )


# =========================================================
# GEMINI CLIENT
# =========================================================

client = genai.Client(
    api_key=api_key
)


# =========================================================
# MODELS
# =========================================================

# Main model
MODEL_NAME = "gemini-3.1-flash-lite"

# Backup model
FALLBACK_MODEL = "gemini-3.5-flash-lite"


# =========================================================
# RETRY SETTINGS
# =========================================================

MAX_RETRIES = 3

RETRY_DELAYS = [1, 2, 4]


# =========================================================
# HELPER
# =========================================================

def _is_retryable_error(error):
    """
    Check whether the Gemini error is likely temporary.

    We retry:
    - 429
    - 500
    - 502
    - 503
    - 504
    - temporary overload/network errors
    """

    error_text = str(error).lower()

    retryable_errors = [
        "429",
        "500",
        "502",
        "503",
        "504",
        "resource_exhausted",
        "service_unavailable",
        "unavailable",
        "overloaded",
        "temporarily",
        "timeout",
        "deadline",
    ]

    return any(
        error_code in error_text
        for error_code in retryable_errors
    )


# =========================================================
# GENERATE COMPLETE RESPONSE
# =========================================================

def generate_response(
    user_message,
    system_prompt
):
    """
    Generate a complete Lumora response.

    Uses:
    1. Main Gemini model
    2. Automatic retries
    3. Backup Gemini model
    """

    config = types.GenerateContentConfig(
        system_instruction=system_prompt
    )

    # -----------------------------------------------------
    # TRY MAIN MODEL
    # -----------------------------------------------------

    for attempt in range(MAX_RETRIES):

        try:

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=user_message,
                config=config
            )

            if response.text:
                return response.text

            raise RuntimeError(
                "Gemini returned an empty response."
            )

        except Exception as e:

            print(
                f"Lumora Gemini error "
                f"(main model, attempt {attempt + 1}): {e}"
            )

            if not _is_retryable_error(e):
                break

            if attempt < MAX_RETRIES - 1:

                delay = RETRY_DELAYS[attempt]

                # Small random jitter prevents repeated
                # requests from happening at exactly
                # the same time.
                delay += random.uniform(0, 0.5)

                print(
                    f"Retrying Gemini in "
                    f"{delay:.1f} seconds..."
                )

                time.sleep(delay)


    # -----------------------------------------------------
    # FALLBACK MODEL
    # -----------------------------------------------------

    print(
        "Main Gemini model unavailable. "
        "Trying fallback model..."
    )

    try:

        response = client.models.generate_content(
            model=FALLBACK_MODEL,
            contents=user_message,
            config=config
        )

        if response.text:
            return response.text

    except Exception as e:

        print(
            f"Lumora fallback Gemini error: {e}"
        )


    # -----------------------------------------------------
    # FINAL FAILURE
    # -----------------------------------------------------

    return (
        "I'm having a little trouble connecting right now. "
        "Please try sending your message again in a moment. 💜"
    )


# =========================================================
# STREAMING RESPONSE
# =========================================================

def generate_response_stream(
    user_message,
    system_prompt
):
    """
    Generate Lumora's response.

    The function keeps the same interface used by
    chat.py:

        for chunk in generate_response_stream(...):

    Internally it:
    - retries temporary Gemini errors
    - waits between retries
    - switches to a backup model
    - finally returns a friendly message
    """

    config = types.GenerateContentConfig(
        system_instruction=system_prompt
    )

    # =====================================================
    # MAIN MODEL
    # =====================================================

    for attempt in range(MAX_RETRIES):

        try:

            print(
                f"Lumora Gemini request "
                f"(main model, attempt {attempt + 1})"
            )

            response_stream = (
                client.models.generate_content_stream(
                    model=MODEL_NAME,
                    contents=user_message,
                    config=config
                )
            )

            # -------------------------------------------------
            # IMPORTANT:
            # Consume the complete stream inside the try block.
            # This allows us to catch a 503 that occurs while
            # the stream is being generated.
            # -------------------------------------------------

            chunks = []

            for chunk in response_stream:

                if chunk.text:
                    chunks.append(chunk.text)

            # -------------------------------------------------
            # Successful response
            # -------------------------------------------------

            if chunks:

                for chunk_text in chunks:
                    yield chunk_text

                return

            raise RuntimeError(
                "Gemini returned an empty response."
            )

        except Exception as e:

            print(
                f"Lumora streaming API error "
                f"(main model, attempt {attempt + 1}): {e}"
            )

            # Non-temporary errors should not be retried
            #endlessly.

            if not _is_retryable_error(e):
                break

            if attempt < MAX_RETRIES - 1:

                delay = RETRY_DELAYS[attempt]

                delay += random.uniform(0, 0.5)

                print(
                    f"Lumora retrying in "
                    f"{delay:.1f} seconds..."
                )

                time.sleep(delay)


    # =====================================================
    # FALLBACK MODEL
    # =====================================================

    print(
        "Main Gemini model failed. "
        "Trying fallback model..."
    )

    try:

        response_stream = (
            client.models.generate_content_stream(
                model=FALLBACK_MODEL,
                contents=user_message,
                config=config
            )
        )

        chunks = []

        for chunk in response_stream:

            if chunk.text:
                chunks.append(chunk.text)

        if chunks:

            for chunk_text in chunks:
                yield chunk_text

            return

    except Exception as e:

        print(
            f"Lumora fallback streaming error: {e}"
        )


    # =====================================================
    # FINAL DEMO-SAFE FALLBACK
    # =====================================================

    yield (
        "I'm having a little trouble connecting right now. "
        "Please try sending your message again in a moment. 💜"
    )