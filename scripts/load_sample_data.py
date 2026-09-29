from pathlib import Path

from fastapi.testclient import TestClient

from securerag.main import create_app


def main() -> None:
    root = Path(__file__).parents[1]
    with TestClient(create_app()) as client:
        receipts = []
        for path in sorted((root / "sample_data").glob("*.txt")):
            response = client.post(
                "/v1/documents",
                json={
                    "title": path.stem.replace("_", " ").title(),
                    "source": str(path),
                    "text": path.read_text(),
                },
            )
            response.raise_for_status()
            receipts.append(response.json())
        print(f"Indexed {len(receipts)} sample documents in the demonstration process.")
        demo = client.post(
            "/v1/query", json={"question": "How quickly should incidents be reported?"}
        )
        demo.raise_for_status()
        print(demo.json())


if __name__ == "__main__":
    main()
