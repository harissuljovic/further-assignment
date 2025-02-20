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
        page = context.new_page()

        # Ensure video is saved after test completion or failure
        def save_video_on_failure():
            if request.node.rep_call.failed:
                video_path = context.video().path()
                print(f"Test failed, saving video: {video_path}")

        request.addfinalizer(save_video_on_failure)

        yield page
        browser.close()


@pytest.fixture(scope="session")
def test_data():
    base_path = Path(__file__).parent / "fixtures"
    data = {}

    for file in base_path.glob("*.json"):
        data[file.stem] = json.load(open(file, "r"))

    return data



