from pages.base_page import BasePage
from playwright.sync_api import Page, expect
from datetime import datetime, timedelta

class ChatPage(BasePage):

    def __init__(self, page: Page):
        super().__init__(page)
        self.schedule_a_tour_btn = 'label:has-text("Schedule A Tour")'
        self.pricing_btn = 'label:has-text("Pricing")'
        self.option_btn = "label.option-button"
        self.day_in_month = "div.Calendar .day-in-month"
        self.next_button = page.locator("button.vsa-button.SubmitButton.floating", has_text="Next")
        self.date_and_time_msg = page.locator("div.bubble-conatiner").nth(3)
        self.confirm_btn = page.locator("button.vsa-button.SubmitButton.floating", has_text="Confirm selections")
        self.main_input = page.locator('input[placeholder="Type here..."][class="input"]')
        self.send_btn = page.locator('button[type="submit"].send-icon')
        self.out_of_my_budget_btn = page.locator('label.option-button.primary >> text="Out Of My Budget"')
        self.invalid_email_error = page.locator('button[type="submit"][form*="form-"][class*="disabled"]')
        self.error_message_locator = page.locator('div.UserInput.floating.light.error >> .error-message')

    def wait_for_initial_message(self, expected_message: str):
        initial_message_locator = self.page.locator(f"div.MessageBubble.light >> text={expected_message}")
        expect(initial_message_locator).to_be_visible(timeout=10000)

    def click_schedule_tour(self):
        self.page.click(self.schedule_a_tour_btn)

    def verify_message_visible(self, message: str):
        expect(self.page.locator(f"div.bubble-conatiner >> text={message}")).to_be_visible(timeout=10000)

    def select_option(self, option_text: str):
        option_label = self.page.locator(self.option_btn, has_text=option_text)
        option_label.click()

    def verify_label(self, label_text: str):
        expect(self.page.locator(f'label:has-text("{label_text}")')).to_have_class('option-button primary selected')

    def select_date_and_time(self) -> str:
        offset = 1
        selected_date = None

        while True:
            candidate_date = datetime.now() + timedelta(days=offset)
            # Skip if candidate_date is Saturday (5) or Sunday (6) - weekends are disabled in date picker
            if candidate_date.weekday() >= 5:
                offset += 1
                continue

            day_str = str(candidate_date.day)
            day_locator = self.page.locator(self.day_in_month, has_text=day_str)
            try:
                # Wait for the day element to become visible
                day_locator.wait_for(state="visible", timeout=5000)
                day_locator.click()
                selected_date = candidate_date
                break  # Exit loop once a valid day is clicked
            except Exception as e:
                # If the day is not clickable try the next day
                offset += 1

        # Wait for time slots to appear
        self.page.wait_for_selector("div.time", state="visible", timeout=5000)

        # Get all available time slots and select the first one
        available_times = self.page.locator("div.time:not(.unavailable)")
        if available_times.count() == 0:
            raise ValueError("No available time slots found")

        first_available_time = available_times.first
        selected_time = first_available_time.inner_text()
        first_available_time.click()

        # Format the selected date and time
        selected_date_time = f"{selected_date.strftime('%-m/%-d/%Y')} at {selected_time}"
        return selected_date_time

    def click_next(self):
       self.next_button.click()

    def verify_date_time_msg(self, date_time: str):
        expect(self.date_and_time_msg).to_be_visible()
        expect(self.date_and_time_msg).to_have_text(date_time)

    def select_multiple_options(self, options: list):
        for option in options:
            self.select_option(option)
        selected_count = len(options)
        expect(self.confirm_btn).to_have_text(f"Confirm selections ({selected_count})")
        self.confirm_btn.click()

    def fill_main_input(self, text: str):
        self.main_input.fill(text)

    def click_send_msg_btn(self):
        self.send_btn.click()

    def click_pricing(self):
        self.page.click(self.pricing_btn)

    def verify_out_of_my_budget_btn_visible(self):
        expect(self.out_of_my_budget_btn).to_be_visible(timeout=10000)

    def verify_invalid_error_message(self, expected_message: str):
        expect(self.error_message_locator).to_have_text(expected_message, timeout=5000)



