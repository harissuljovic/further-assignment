import pytest
from playwright.sync_api import sync_playwright
from pathlib import Path
import json

@pytest.fixture(scope="function")
def page(request):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            record_video_dir="videos/"
        )
        # Set default timeout to 60 seconds
        context.set_default_timeout(60000)
        page = context.new_page()
        page.set_default_timeout(60000)
        try:
            yield page
            # Test passed
        finally:
            # Test failed, save the video
            if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
                try:
                    video_path = page.video.path()
                    print(f"Test failed, saving video: {video_path}")
                except Exception as e:
                    print(f"Error saving video: {e}")
            browser.close()

@pytest.fixture(scope="session")
def test_data():
    base_path = Path(__file__).parent / "fixtures"
    data = {}

    for file in base_path.glob("*.json"):
        data[file.stem] = json.load(open(file, "r"))

    return data



