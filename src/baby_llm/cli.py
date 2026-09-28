"""Command-line interface (CLI) for Baby LLM."""

import argparse
import sys
from baby_llm.core.models import InteractionTurn
from baby_llm.core.ring_buffer import EpisodicRingBuffer
from baby_llm.dream.worker import dream_worker
from baby_llm.runtime.context_assembler import context_assembler
from baby_llm.runtime.llm_provider import llm_provider
from baby_llm.storage.graph_store import graph_store
from baby_llm.storage.wal import wal_logger
from baby_llm.success.curiosity import curiosity_engine


def interactive_chat():
    print("=" * 60)
    print("👶 Baby LLM Interactive Terminal")
    print("   Privacy-First • Local Memory • Qwen2.5-0.5B (Embedded)")
    print("   Type 'exit' to quit, '/dream' to trigger consolidation.")
    print("=" * 60)

    ring_buffer = EpisodicRingBuffer(max_size=15)

    while True:
        try:
            user_input = input("\nYou > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting Baby LLM.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "q"):
            print("Goodbye!")
            break
        if user_input == "/dream":
            print("\n🌙 Running REM Dream Consolidation...")
            res = dream_worker.run_consolidation_cycle()
            print(f"Dream Complete: {res}")
            continue

        # Fast-Path Context Assembly
        messages = context_assembler.assemble(user_input, ring_buffer)

        print("\nBaby LLM > ", end="", flush=True)
        try:
            reply = llm_provider.chat_sync(messages)
            print(reply)
            assistant_text = reply
        except Exception as e:
            assistant_text = (
                f"[Local Offline Mode] (Error: {e}). Your message has been logged to memory."
            )
            print(assistant_text)

        # Gentle Curiosity Probe check
        probe = curiosity_engine.evaluate_turn_for_probe(user_input)
        if probe:
            print(f"\n💭 {probe}")

        # Write to WAL & Ring Buffer
        turn = InteractionTurn(
            user_input=user_input,
            assistant_response=assistant_text,
        )
        wal_logger.append_turn(turn)
        ring_buffer.append(turn)


def list_memories():
    nodes = graph_store.get_active_nodes()
    print(f"\n🧠 Baby LLM Active Memories ({len(nodes)} facts):")
    print("-" * 60)
    for n in nodes:
        ymyl = " [🛡️ YMYL]" if n.ymyl_protected else ""
        print(f"• [{n.category.value.upper()}] {n.to_readable_fact()}{ymyl}")
        print(f"  Confidence: {int(n.confidence * 100)}% | Stability: {n.stability:.1f} | ID: {n.id[:8]}")
    print("-" * 60)


def main():
    parser = argparse.ArgumentParser(description="Baby LLM Companion CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("chat", help="Start interactive chat")
    subparsers.add_parser("dream", help="Trigger REM dream consolidation cycle")
    subparsers.add_parser("memories", help="List active memory nodes")
    subparsers.add_parser("mcp", help="Run Universal MCP server over stdio")
    
    serve_parser = subparsers.add_parser("serve", help="Run FastAPI local REST server")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    serve_parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind")

    args = parser.parse_args()

    if args.command == "chat" or args.command is None:
        interactive_chat()
    elif args.command == "dream":
        summary = dream_worker.run_consolidation_cycle()
        print(f"REM Dream Cycle Completed: {summary}")
    elif args.command == "memories":
        list_memories()
    elif args.command == "mcp":
        from baby_llm.mcp.server import run_mcp_server
        run_mcp_server()
    elif args.command == "serve":
        import uvicorn
        uvicorn.run("baby_llm.api.server:app", host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()
