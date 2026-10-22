import re
from pathlib import Path
from typing import Dict

_SECTION_REGEX = re.compile(
    r"^##\s+(?P<section>[A-Za-z0-9_]+)\s*$\n(?P<content>.*?)(?=^##\s+[A-Za-z0-9_]+\s*$|\Z)",
    flags=re.MULTILINE | re.DOTALL,
)


class PromptLoader:
    @staticmethod
    def load_prompts(source_path: str) -> Dict[str, str]:
        prompt_path = Path(source_path)
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file does not exist: {source_path}")

        raw_text = prompt_path.read_text(encoding="utf-8")
        prompts: Dict[str, str] = {}

        for match in _SECTION_REGEX.finditer(raw_text):
            section_name = match.group("section").strip()
            section_content = match.group("content").strip()
            prompts[section_name] = section_content

        if not prompts:
            raise ValueError(f"No prompt sections were found in {source_path}")

        return prompts
