from pathlib import Path

from ingestion import load_records, save_report
from validator import ChemValidator
from viewer import generate_3d_html


def run_pipeline(input_file: str, output_report: str, viewer_compound_id: str = None):
    records = load_records(input_file)
    validator = ChemValidator()

    validated_results = []
    molecule_lookup = {}

    for record in records:
        result, mol = validator.validate_record(record)
        validated_results.append(result.model_dump())

        if result.validation_status == "PASS":
            molecule_lookup[result.compound_id] = {
                "compound_name": result.compound_name,
                "smiles": result.smiles
            }

    save_report(validated_results, output_report)

    total = len(validated_results)
    passed = sum(1 for r in validated_results if r["validation_status"] == "PASS")
    failed = total - passed

    print("=" * 60)
    print("CHEMDATA VALIDATION ENGINE")
    print("=" * 60)
    print(f"Input records: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Report saved to: {output_report}")

    if viewer_compound_id:
        if viewer_compound_id not in molecule_lookup:
            print(f"\nViewer warning: compound_id '{viewer_compound_id}' not found or not valid.")

        else:
            viewer_data = molecule_lookup[viewer_compound_id]
            output_html = Path("data/reports") / f"{viewer_compound_id}_viewer.html"

            html_path = generate_3d_html(
                smiles=viewer_data["smiles"],
                compound_name=viewer_data["compound_name"],
                output_file=str(output_html),
                compound_code=viewer_compound_id
            )

            print(f"3D viewer generated: {html_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ChemData Validation Engine")
    parser.add_argument(
        "--input",
        default="data/sample_compounds.json",
        help="Path to input JSON or CSV file"
    )
    parser.add_argument(
        "--output",
        default="data/reports/validation_report.json",
        help="Path to output validation report"
    )
    parser.add_argument(
        "--viewer-compound-id",
        default=None,
        help="Compound ID to generate 3D viewer for"
    )

    args = parser.parse_args()

    run_pipeline(
        input_file=args.input,
        output_report=args.output,
        viewer_compound_id=args.viewer_compound_id
    )
