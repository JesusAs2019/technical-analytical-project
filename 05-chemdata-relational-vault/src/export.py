from pathlib import Path


def export_dataframe_to_csv(df, path: str):
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return str(output_path.resolve())


def export_summary_markdown(df, path: str):
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    total = len(df)
    pass_count = int((df["validation_status"] == "PASS").sum()) if not df.empty else 0
    warn_count = int((df["validation_status"] == "WARN").sum()) if not df.empty else 0
    fail_count = int((df["validation_status"] == "FAIL").sum()) if not df.empty else 0

    preview = df.head(10).to_markdown(index=False) if not df.empty else "_No records available_"

    markdown = f"""# ChemData Relational Vault Summary

## Record Counts
- Total records: **{total}**
- PASS: **{pass_count}**
- WARN: **{warn_count}**
- FAIL: **{fail_count}**

## Dataset Preview
{preview}
"""

    output_path.write_text(markdown, encoding="utf-8")
    return str(output_path.resolve())
