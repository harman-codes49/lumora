import streamlit as st


def load_lumora_css():
    st.markdown(
        """
        <style>

        /* ==========================================
           LUMORA COLOR PALETTE
        ========================================== */

        :root {
            --lumora-purple: #6B5B95;
            --lumora-dark: #403A54;
            --lumora-light: #EDE5F8;
            --lumora-soft: #F7F1FB;
            --lumora-pink: #F5E3EE;
            --lumora-green: #DFEBDD;
            --lumora-white: #FFFDFB;
            --lumora-border: #E8DFF0;
            --lumora-muted: #777189;
        }


        /* ==========================================
           MAIN APPLICATION
        ========================================== */

        .stApp {
            background:
                radial-gradient(
                    circle at 5% 5%,
                    #F1E8FA 0%,
                    transparent 28%
                ),
                radial-gradient(
                    circle at 95% 15%,
                    #F8EAF2 0%,
                    transparent 25%
                ),
                #FFFDFB;

            color: var(--lumora-dark);
        }


        /* ==========================================
           MAIN CONTENT WIDTH
        ========================================== */

        .block-container {
            max-width: 1400px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }


        /* ==========================================
           REMOVE STREAMLIT HEADER
        ========================================== */

        [data-testid="stHeader"] {
            background: transparent;
        }


        /* ==========================================
           SIDEBAR
        ========================================== */

        section[data-testid="stSidebar"] {
            background:
                linear-gradient(
                    180deg,
                    #F7F0FC 0%,
                    #FFFDFB 100%
                );

            border-right: 1px solid var(--lumora-border);
        }

        section[data-testid="stSidebar"] > div {
            padding-top: 2rem;
        }


        /* ==========================================
           SIDEBAR BRAND
        ========================================== */

        .sidebar-brand {
            text-align: center;
            padding: 10px 5px 25px 5px;
        }

        .sidebar-brand-name {
            font-family: Georgia, serif;
            font-size: 30px;
            color: var(--lumora-dark);
            letter-spacing: -0.5px;
        }

        .sidebar-brand-tagline {
            font-size: 11px;
            color: var(--lumora-muted);
            margin-top: 5px;
        }


        /* ==========================================
           WELCOME HEADER
        ========================================== */

        .welcome-title {
            font-family: Georgia, serif;
            font-size: 38px;
            color: var(--lumora-dark);
            margin-bottom: 5px;
        }

        .welcome-subtitle {
            color: var(--lumora-muted);
            font-size: 15px;
        }


        /* ==========================================
           HERO CARD
        ========================================== */

        .hero-card {
            background:
                linear-gradient(
                    135deg,
                    #EEE3FA 0%,
                    #F8EAF3 100%
                );

            border: 1px solid #E3D6EF;
            border-radius: 28px;

            padding: 35px;

            min-height: 220px;

            box-shadow:
                0 12px 35px
                rgba(91, 70, 120, 0.08);
        }

        .hero-title {
            font-family: Georgia, serif;
            font-size: 31px;
            color: var(--lumora-dark);
            margin-bottom: 10px;
        }

        .hero-description {
            color: #625B72;
            font-size: 15px;
            line-height: 1.7;
            max-width: 600px;
        }


        /* ==========================================
           GENERAL CARD
        ========================================== */

        .lumora-card {
            background: rgba(255, 253, 251, 0.92);

            border: 1px solid var(--lumora-border);

            border-radius: 22px;

            padding: 24px;

            box-shadow:
                0 8px 28px
                rgba(88, 68, 120, 0.06);
        }


        /* ==========================================
           FEATURE CARDS
        ========================================== */

        .feature-card {
            background: #FFFFFF;

            border: 1px solid var(--lumora-border);

            border-radius: 20px;

            padding: 22px;

            min-height: 135px;

            box-shadow:
                0 7px 24px
                rgba(88, 68, 120, 0.05);

            transition: all 0.2s ease;
        }

        .feature-card:hover {
            transform: translateY(-3px);

            box-shadow:
                0 12px 30px
                rgba(88, 68, 120, 0.10);
        }

        .feature-icon {
            font-size: 25px;
            margin-bottom: 10px;
        }

        .feature-title {
            color: var(--lumora-dark);
            font-size: 15px;
            font-weight: 600;
        }

        .feature-description {
            color: var(--lumora-muted);
            font-size: 12px;
            margin-top: 6px;
            line-height: 1.5;
        }


        /* ==========================================
           BUTTONS
        ========================================== */

        .stButton > button {
            border-radius: 18px;

            border: 1px solid #D9C8EA;

            background: #E8D9F5;

            color: #4A4165;

            font-weight: 600;

            min-height: 42px;

            transition: all 0.2s ease;
        }

        .stButton > button:hover {
            background: #DCC8EE;

            border-color: #CBB5E1;

            transform: translateY(-1px);
        }


        /* ==========================================
           INPUTS
        ========================================== */

        .stTextInput input,
        .stTextArea textarea {
            border-radius: 16px !important;

            border: 1px solid #E1D7E9 !important;

            background: #FFFEFD !important;

            color: var(--lumora-dark) !important;
        }


        /* ==========================================
           SECTION TITLES
        ========================================== */

        .section-title {
            font-family: Georgia, serif;

            font-size: 23px;

            color: var(--lumora-dark);

            margin-bottom: 4px;
        }

        .section-subtitle {
            color: var(--lumora-muted);

            font-size: 13px;

            margin-bottom: 15px;
        }


        /* ==========================================
           MOOD CARDS
        ========================================== */

        .mood-card {
            background: #FFFFFF;

            border: 1px solid var(--lumora-border);

            border-radius: 18px;

            padding: 15px;

            text-align: center;
        }

        .mood-icon {
            font-size: 24px;
        }

        .mood-label {
            color: var(--lumora-muted);

            font-size: 12px;

            margin-top: 5px;
        }


        /* ==========================================
           STREAMLIT FOOTER
        ========================================== */

        footer {
            visibility: hidden;
        }


        /* ==========================================
           MOBILE
        ========================================== */

        @media (max-width: 768px) {

            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .welcome-title {
                font-size: 30px;
            }

            .hero-card {
                padding: 25px;
            }

            .hero-title {
                font-size: 25px;
            }

        }

        </style>
        """,
        unsafe_allow_html=True
    )