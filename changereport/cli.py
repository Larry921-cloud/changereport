"""CLI entry point for the ITIL 4 Change Enablement Report Generator."""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="ITIL 4 Change Enablement Report Generator - "
                    "Analyze change management data and produce PDF reports."
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default=None,
        help="Path to change data file (.txt, .xls, .xlsx)",
    )
    parser.add_argument(
        "-o", "--output",
        default="change_report.pdf",
        help="Output PDF path (default: change_report.pdf)",
    )
    parser.add_argument(
        "--title",
        default="ITIL 4 Change Enablement Report",
        help="Report title",
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="Launch the web GUI instead of CLI processing",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port for web server (default: 5000)",
    )
    args = parser.parse_args()

    # Web mode
    if args.web:
        from changereport.webapp import run_web
        run_web(port=args.port)
        return

    # CLI mode requires input file
    if args.input_file is None:
        parser.print_help()
        print("\nError: Either provide an input file or use --web to launch the GUI.",
              file=sys.stderr)
        sys.exit(1)

    # Validate input
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    from changereport.parser import load_change_data
    from changereport.analysis import compute_all_analysis
    from changereport.charts import generate_all_charts
    from changereport.report import generate_report

    print(f"Reading {input_path}...")
    df = load_change_data(str(input_path))
    print(f"Loaded {len(df)} change records.")

    print("Analyzing data...")
    analysis = compute_all_analysis(df)

    print("Generating charts...")
    charts = generate_all_charts(df, analysis)

    print(f"Building PDF report: {args.output}...")
    generate_report(df, args.output, charts, analysis, title=args.title)

    print(f"Done! Report saved to: {args.output}")


if __name__ == "__main__":
    main()
