from typing import Any, Dict

from langchain.schema import HumanMessage, SystemMessage

from meeting_agent.email_tool import EmailSender
from .transcript_processor import TranscriptProcessor


class AnalysisNode:
    def __init__(self, llm: Any, prompts: Dict[str, str], processor: TranscriptProcessor) -> None:
        self.llm = llm
        self.prompts = prompts
        self.processor = processor

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        transcript = self.processor.read_transcript(state["transcript_path"])
        analysis_prompt = self.prompts.get("analysis_prompt", "")
        system_prompt = self.prompts.get("system_prompt", "")

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=self.processor.prepare_analysis_input(analysis_prompt, transcript)),
        ]

        state["mom"] = self._generate(messages) 
        return state

    def _generate(self, messages: Any) -> str:
        if hasattr(self.llm, "generate"):
            result = self.llm.generate([messages])
            return self._extract_text(result)

        response = self.llm(messages)
        return self._extract_text(response)

    def _extract_text(self, result: Any) -> str:
        if hasattr(result, "generations") and result.generations:
            generation = result.generations[0][0]
            return getattr(generation, "text", str(generation)).strip()

        return getattr(result, "content", str(result)).strip()


class EmailSenderNode:
    def __init__(self, llm: Any, prompts: Dict[str, str]) -> None:
        self.llm = llm
        self.prompts = prompts
        self.email_sender = EmailSender()

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        mom = state.get("mom", "")
        recipient = state["recipient"]
        subject = state["subject"]
        sender = state.get("sender")
        email_prompt = self.prompts.get("email_prompt", "")

        messages = [
            SystemMessage(content=email_prompt),
            HumanMessage(
                content=(
                    f"Draft a professional email to {recipient} with subject '{subject}'.\n\n"
                    "Use the meeting minutes below as the email body.\n\n"
                    f"Meeting Minutes:\n{mom}"
                )
            ),
        ]

        email_body = self._generate(messages)
        state["email_body"] = email_body
        self.email_sender.send_email(recipient, subject, email_body, sender)
        state["sent"] = True
        return state

    def _generate(self, messages: Any) -> str:
        if hasattr(self.llm, "generate"):
            result = self.llm.generate([messages])
            return self._extract_text(result)

        response = self.llm(messages)
        return self._extract_text(response)

    def _extract_text(self, result: Any) -> str:
        if hasattr(result, "generations") and result.generations:
            generation = result.generations[0][0]
            return getattr(generation, "text", str(generation)).strip()

        return getattr(result, "content", str(result)).strip()
