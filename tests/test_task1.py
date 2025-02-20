import random
from pages.chat_page import ChatPage
from faker import Faker

def test_schedule_a_tour(page, test_data):
    messages = test_data["messages"]
    visitors = test_data["visitors"]
    activities = test_data["activities"]

    chat_page = ChatPage(page)
    chat_page.navigate()
    chat_page.wait_for_initial_message(messages["initial_message"])
    chat_page.click_schedule_tour()

    chat_page.verify_message_visible(messages["tour_message"])

    # Randomly select a visitor type
    random_visitor = random.choice(visitors["visitors"])
    chat_page.select_option(random_visitor)
    chat_page.verify_label(random_visitor)

    chat_page.verify_message_visible(messages["schedule_message"])
    selected_date_time = chat_page.select_date_and_time()
    chat_page.click_next()
    chat_page.verify_date_time_msg(selected_date_time)
    chat_page.verify_message_visible(messages["activities_message"])

    # Randomly select 3 activities
    random_selected_activities = random.sample(activities["activities"], 3)
    chat_page.select_multiple_options(random_selected_activities)
    chat_page.verify_message_visible(messages["name_message"])

    faker = Faker()
    chat_page.fill_main_input(faker.name())
    chat_page.click_send_msg_btn()
    chat_page.verify_message_visible(messages["email_message"])

    # Add invalid email to test if validation message appears
    chat_page.fill_main_input('invalid@email')
    chat_page.click_send_msg_btn()
    chat_page.verify_invalid_error_message(messages["invalid_email_error_msg"])

    #Add valid mail
    chat_page.fill_main_input(faker.email())
    chat_page.click_send_msg_btn()
    chat_page.verify_message_visible(messages["phone_message"])

    # Add invalid phone to test if validation message appears
    chat_page.fill_main_input("1NV4L1DPH0NE")
    chat_page.click_send_msg_btn()
    chat_page.verify_invalid_error_message(messages["invalid_phone_error_msg"])

    chat_page.fill_main_input(faker.basic_phone_number())
    chat_page.click_send_msg_btn()
    chat_page.verify_message_visible(messages["tour_requested_message"])

def test_pricing(page, test_data):
    messages = test_data["messages"]
    care_levels = test_data["care_levels"]
    visitors_pricing = test_data["visitors_pricing"]
    timelines = test_data["timelines"]

    chat_page = ChatPage(page)
    chat_page.navigate()
    chat_page.wait_for_initial_message(messages["initial_message"])
    chat_page.click_pricing()

    chat_page.verify_message_visible(messages["care_message"])

    # Randomly select a level of care
    random_care_level = random.choice(care_levels["careLevels"])
    chat_page.select_option(random_care_level)
    chat_page.verify_label(random_care_level)

    chat_page.verify_message_visible(messages["who_is_it_for"])

    # Randomly select a visitor type
    random_visitor = random.choice(visitors_pricing["visitors"])
    chat_page.select_option(random_visitor)
    chat_page.verify_label(random_visitor)

    chat_page.verify_message_visible(messages["timeline_message"])

    # Randomly select a timeline
    random_timeline = random.choice(timelines["timelines"])
    chat_page.select_option(random_timeline)
    chat_page.verify_label(random_timeline)

    chat_page.verify_message_visible(messages["name_message"])

    faker = Faker()
    first_name = faker.first_name()
    last_name = faker.last_name()
    chat_page.fill_main_input(first_name + " " + last_name)
    chat_page.click_send_msg_btn()
    chat_page.verify_message_visible(messages["cell_phone_message"])
    chat_page.fill_main_input(faker.basic_phone_number())
    chat_page.click_send_msg_btn()
    chat_page.verify_message_visible(messages["email_message"])
    chat_page.fill_main_input(faker.email())
    chat_page.click_send_msg_btn()
    chat_page.verify_out_of_my_budget_btn_visible()

    #Refresh and verify personalized message
    page.reload()
    chat_page.wait_for_initial_message(f"{messages["initial_message_personalised"]} {first_name}?")


