# Meeting Analysis Agent

This repository contains an agentic AI application that analyzes meeting transcripts, generates minutes of meeting (MoM), and sends the result by email.

## Features

- Uses LangChain with a Gemini LLM for transcript analysis
- Orchestrates work using LangGraph
- Separates email functionality into a dedicated tool module
- Stores prompts in `agents.md`
- Supports transcript input from a text file stub in `Transcript/`

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and update values:
   - `GEMINI_MODEL_NAME`
   - `SMTP_HOST`
   - `SMTP_PORT`
   - `SMTP_USERNAME`
   - `SMTP_PASSWORD`
   - `EMAIL_DEFAULT_SENDER`

3. Run the agent:
   ```bash
   python app.py --transcript Transcript/sample_transcript.txt --recipient recipient@example.com --subject "Meeting Minutes"
   ```

## Transcript Stub

Put the meeting transcript text file in the `Transcript` folder. The sample stub is provided at `Transcript/sample_transcript.txt`.

## Notes

- The email sending tool uses the standard library modules `smtplib` and `email`.
- Prompts are managed in `agents.md` for easy iteration and review.
