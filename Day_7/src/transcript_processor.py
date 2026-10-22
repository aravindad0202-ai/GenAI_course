from pathlib import Path


class TranscriptProcessor:
    def read_transcript(self, transcript_path: str) -> str:
        path = Path(transcript_path)
        if not path.exists():
            raise FileNotFoundError(f"Transcript path not found: {transcript_path}")

        transcript = path.read_text(encoding="utf-8").strip()
        if not transcript:
            raise ValueError(f"Transcript file is empty: {transcript_path}")

        return transcript

    def prepare_analysis_input(self, analysis_prompt: str, transcript: str) -> str:
        return f"{analysis_prompt}\n\nTranscript:\n{transcript}" 
