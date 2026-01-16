import argparse
from pathlib import Path
from app.core.dependencies import get_ingestor


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", required=True, help="file or directory to ingest")
    args = ap.parse_args()

    ingestor = get_ingestor()
    p = Path(args.path)

    files = [p] if p.is_file() else [x for x in p.rglob("*") if x.is_file()]
    for f in files:
        data = f.read_bytes()
        report = ingestor.ingest_bytes(filename=f.name, data=data, content_type="application/octet-stream")
        print(f"[OK] {f} -> {report['chunks']} chunks, inserted={report['inserted']}")


if __name__ == "__main__":
    main()
