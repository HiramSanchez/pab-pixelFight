from pathlib import Path

from scripts.validate_distribution import REQUIRED_FILES, validate_distribution


def create_required_bundle_files(bundle):
    for relative_path in REQUIRED_FILES:
        path = bundle / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"fixture")


def test_distribution_audit_accepts_matching_assets(tmp_path):
    project = tmp_path / "project"
    bundle = tmp_path / "bundle"
    source_asset = project / "assets/images/example.png"
    packaged_asset = bundle / "assets/images/example.png"
    source_asset.parent.mkdir(parents=True)
    packaged_asset.parent.mkdir(parents=True)
    source_asset.write_bytes(b"same")
    packaged_asset.write_bytes(b"same")
    create_required_bundle_files(bundle)

    assert validate_distribution(bundle, project) == []


def test_distribution_audit_reports_missing_and_changed_content(tmp_path):
    project = tmp_path / "project"
    bundle = tmp_path / "bundle"
    source_asset = project / "assets/images/example.png"
    packaged_asset = bundle / "assets/images/example.png"
    source_asset.parent.mkdir(parents=True)
    packaged_asset.parent.mkdir(parents=True)
    source_asset.write_bytes(b"source")
    packaged_asset.write_bytes(b"changed")

    errors = validate_distribution(bundle, project)

    assert "Missing packaged file: PixelFight.exe" in errors
    relative_asset = Path("images") / "example.png"
    assert f"Changed packaged asset: {relative_asset}" in errors
