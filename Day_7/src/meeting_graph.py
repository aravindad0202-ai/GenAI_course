import os
from pathlib import Path
from typing import Any, Dict, Optional

from meeting_agent.prompt_loader import PromptLoader
from .nodes import AnalysisNode, EmailSenderNode
from .transcript_processor import TranscriptProcessor


class MeetingAnalysisGraph:
    def __init__(self, prompt_path: Optional[str] = None) -> None:
        self.prompt_path = (
            prompt_path
            or str(Path(__file__).resolve().parents[1] / "agents.md")
        )
        self.prompts = PromptLoader.load_prompts(self.prompt_path)
        self.llm = self._build_llm()
        self.processor = TranscriptProcessor()
        self.analysis_node = AnalysisNode(self.llm, self.prompts, self.processor)
        self.email_node = EmailSenderNode(self.llm, self.prompts)
        self.graph = self._build_langgraph()

    def _build_llm(self) -> Any:
        model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-pro")

        try:
            from langchain.chat_models import ChatGoogleGemini

            return ChatGoogleGemini(model_name=model_name)
        except Exception:
            try:
                from langchain.chat_models import ChatOpenAI

                return ChatOpenAI(model_name=model_name)
            except Exception as exc:
                raise RuntimeError(
                    "Could not construct a Gemini-compatible LangChain chat model. "
                    "Install a supported LangChain chat provider or update GEMINI_MODEL_NAME."
                ) from exc

    def _build_langgraph(self) -> Optional[Any]:
        try:
            import langgraph

            if hasattr(langgraph, "StateGraph") and hasattr(langgraph, "StateNode"):
                return {
                    "type": "state",
                    "StateGraph": langgraph.StateGraph,
                    "StateNode": langgraph.StateNode,
                }

            if hasattr(langgraph, "Graph") and hasattr(langgraph, "Node"):
                return {
                    "type": "graph",
                    "Graph": langgraph.Graph,
                    "Node": langgraph.Node,
                }
        except Exception:
            return None

    def _run_graph(self, state: Dict[str, Any]) -> Dict[str, Any]:
        if self.graph is None:
            state = self.analysis_node.run(state)
            state = self.email_node.run(state)
            return state

        graph_type = self.graph.get("type")

        if graph_type == "state":
            StateGraph = self.graph["StateGraph"]
            StateNode = self.graph["StateNode"]

            graph = StateGraph(name="meeting_analysis")
            analysis_node = StateNode(name="analysis", fn=self.analysis_node.run)
            email_node = StateNode(name="email_sender", fn=self.email_node.run)

            if hasattr(graph, "add_node"):
                graph.add_node(analysis_node)
                graph.add_node(email_node)

            if hasattr(graph, "add_edge"):
                graph.add_edge(analysis_node, email_node)

            if hasattr(graph, "set_start_node"):
                graph.set_start_node(analysis_node)

            if hasattr(graph, "set_end_node"):
                graph.set_end_node(email_node)

            if hasattr(graph, "run"):
                graph.run(state)
                return state

        if graph_type == "graph":
            Graph = self.graph["Graph"]
            Node = self.graph["Node"]

            graph = Graph(name="meeting_analysis")
            analysis_node = Node(self.analysis_node.run, name="analysis")
            email_node = Node(self.email_node.run, name="email_sender")

            if hasattr(graph, "add_node"):
                graph.add_node(analysis_node)
                graph.add_node(email_node)

            if hasattr(graph, "add_edge"):
                graph.add_edge(analysis_node, email_node)

            if hasattr(graph, "set_start_node"):
                graph.set_start_node(analysis_node)

            if hasattr(graph, "set_end_node"):
                graph.set_end_node(email_node)

            if hasattr(graph, "run"):
                graph.run(state)
                return state

        state = self.analysis_node.run(state)
        state = self.email_node.run(state)
        return state

    def run(
        self,
        transcript_path: str,
        recipient: str,
        subject: Optional[str] = None,
        sender: Optional[str] = None,
    ) -> Dict[str, Any]:
        subject = subject or os.getenv("DEFAULT_EMAIL_SUBJECT", "Meeting Minutes")
        state: Dict[str, Any] = {
            "transcript_path": transcript_path,
            "recipient": recipient,
            "subject": subject,
            "sender": sender,
        }

        return self._run_graph(state)
