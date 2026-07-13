import requests
import zipfile
import io
from pathlib import Path

GITHUB_API = "https://api.github.com"

class GitHubRelease:
    def __init__(self, repo: str):
        self.repo = repo
        self.session = requests.Session()
        self.session.headers["Accept"] = "application/vnd.github.v3+json"

    def get_latest(self) -> dict:
        url = f"{GITHUB_API}/repos/{self.repo}/releases/latest"
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()

    def download_zip(self, tag_name: str, dest: Path):
        """Download source zip of a tag and extract it."""
        url = f"https://github.com/{self.repo}/archive/refs/tags/{tag_name}.zip"
        resp = self.session.get(url)
        resp.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            zf.extractall(dest)

    def get_english_data_files(self) -> dict[str, str]:
        """Get all English translation files from the latest release."""
        import tempfile

        release = self.get_latest()
        tag = release["tag_name"]

        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)
            self.download_zip(tag, dest)
            # Find the extracted directory
            extracted = next(dest.iterdir())
            english_dir = extracted / "data" / "english"
            
            files = {}
            for f in english_dir.iterdir():
                if f.is_file():
                    files[f.name] = f.read_text(encoding="utf-8")
            return files