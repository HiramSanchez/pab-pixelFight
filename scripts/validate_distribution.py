import argparse
import hashlib
from pathlib import Path


REQUIRED_FILES = (
    "PixelFight.exe",
    "README.md",
    "CHANGELOG.md",
    "THIRD_PARTY_NOTICES.md",
    "VERSION",
)


def file_digest(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_distribution(bundle_root, project_root):
    bundle_root = Path(bundle_root)
    project_root = Path(project_root)
    errors = []

    for relative_path in REQUIRED_FILES:
        if not (bundle_root / relative_path).is_file():
            errors.append(f"Missing packaged file: {relative_path}")

    source_assets = project_root / "assets"
    packaged_assets = bundle_root / "assets"
    for source_path in source_assets.rglob("*"):
        if not source_path.is_file():
            continue
        relative_path = source_path.relative_to(source_assets)
        packaged_path = packaged_assets / relative_path
        if not packaged_path.is_file():
            errors.append(f"Missing packaged asset: {relative_path}")
        elif file_digest(source_path) != file_digest(packaged_path):
            errors.append(f"Changed packaged asset: {relative_path}")

    return errors


def main():
    parser = argparse.ArgumentParser(
        description="Verify a Windows Pixel Fight bundle."
    )
    parser.add_argument("bundle", type=Path)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    args = parser.parse_args()

    errors = validate_distribution(args.bundle, args.project_root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)

    print("Distribution validation: PASS")


if __name__ == "__main__":
    main()
