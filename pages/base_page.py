from playwright.sync_api import Page, expect

class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def navigate(self):
        self.page.goto("https://www.talkfurther.com/try-it")
        expect(self.page).to_have_title("Demo")