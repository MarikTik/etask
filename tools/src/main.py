from parser import Parser
from comm.protocol import packet_header
# -----------------------------
# CLI entry point
# -----------------------------


def main() -> None:
    parser = Parser()
    print(parser.parse())


if __name__ == "__main__":
    main()
