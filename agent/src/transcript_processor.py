from pathlib import Path
from src.prompt_loader import prompt
from .utils import llm
from langchain_core.messages import HumanMessage, SystemMessage

class TranscriptProcessor:
    def _read_transcript(self) -> str:
        print('-'*10,'Reading Transcript', '-'*10)
        transcript_path = r'D:\IT\AI\teaching\GenAI_course\agent\Transcript\sample_transcript.txt'
        path = Path(transcript_path)
        if not path.exists():
            raise FileNotFoundError(f"Transcript path not found: {transcript_path}")

        transcript = path.read_text(encoding="utf-8").strip()
        if not transcript:
            raise ValueError(f"Transcript file is empty: {transcript_path}")
        self.transcript = transcript
        return self.transcript

    def _prepare_MOM(self) -> str:
        print('-'*10,'Preparing MOM', '-'*10)
        analysis_input = f"{prompt.get('analysis_prompt')}\n\nTranscript:\n{self.transcript}"
        print(analysis_input)
        message = [
            SystemMessage(content=prompt.get('system_prompt')),
            HumanMessage(content=analysis_input)
        ]
        response = llm.invoke(message)
        return response.content

    def generate_MOM(self):
        self._read_transcript()
        mom = self._prepare_MOM()
        return mom[0]['text']
