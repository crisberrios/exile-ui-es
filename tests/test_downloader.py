from exile_ui_es.downloader import GitHubRelease

def test_get_latest_release():
    release = GitHubRelease("Lailloken/Exile-UI")
    info = release.get_latest()
    assert "tag_name" in info
    assert "assets" in info

def test_get_english_files():
    release = GitHubRelease("Lailloken/Exile-UI")
    files = release.get_english_data_files()
    assert "UI.txt" in files
    assert "client.txt" in files
    assert len(files) > 5