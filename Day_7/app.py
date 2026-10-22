import os
from argparse import ArgumentParser
from dotenv import load_dotenv
from src.meeting_graph import MeetingAnalysisGraph


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Run the Meeting Analysis Agent")
    parser.add_argument("--transcript", required=True, help="Path to meeting transcript text file")
    parser.add_argument("--recipient", required=True, help="Email address to send the meeting minutes to")
    parser.add_argument("--subject", default=None, help="Email subject line")
    parser.add_argument("--sender", default=None, help="Optional sender email address")
    return parser


def main() -> None:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args()

    graph = MeetingAnalysisGraph()
    result = graph.run(
        transcript_path=args.transcript,
        recipient=args.recipient,
        subject=args.subject,
        sender=args.sender,
    )

    print("\n=== Generated Minutes of Meeting ===\n")
    print(result.get("mom", ""))
    print("\nEmail sent successfully.")


if __name__ == "__main__":
    main()
