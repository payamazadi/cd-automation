from datetime import date, datetime

from dotenv import load_dotenv


class Base():
    def __init__(self):
        load_dotenv()
        self.current_date = date.today().strftime("%Y-%m-%d")
        self.current_date_friendly = date.today().strftime("%A %B %d, %Y")
        self.current_time = datetime.now().strftime("%I:%M %p")