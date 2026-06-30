from pathlib import Path

from schema_manager import create_schema
from sync_engine import load_seed_records, sync_records
from queries import get_all_compounds, get_compounds_by_status
from export import export_dataframe_to_csv, export_summary_markdown


def run_pipeline():
    project_root = Path(__file__).resolve().parent.parent
    seed_file = project_root / "data" / "seed_data.json"
    output_dir = project_root / "data" / "outputs"

    print("=" * 60)
    print("CHEMDATA RELATIONAL VAULT")
    print("=" * 60)

    print("1. Creating database schema...")
    create_schema()
    print("   Schema ready.")

    print("2. Loading seed data...")
    records = load_seed_records(str(seed_file))
    print(f"   Loaded {len(records)} record(s).")

    print("3. Syncing records into relational vault...")
    inserted = sync_records(records)
    print(f"   Inserted {inserted} new record(s).")

    print("4. Querying stored compounds...")
    all_df = get_all_compounds()
    pass_df = get_compounds_by_status("PASS")

    print(f"   Total rows in vault: {len(all_df)}")
    print(f"   PASS rows: {len(pass_df)}")

    print("5. Exporting outputs...")
    csv_path = export_dataframe_to_csv(all_df, str(output_dir / "all_compounds.csv"))
    md_path = export_summary_markdown(all_df, str(output_dir / "summary.md"))

    print(f"   CSV export saved to: {csv_path}")
    print(f"   Markdown summary saved to: {md_path}")

    print("=" * 60)
    print("PROJECT 5 RUN COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()
