from langchain.tools import BaseTool
from typing import Optional, Type
from pydantic import BaseModel, Field
import datetime
import urllib


class GoogleCalendarGeneratorInput(BaseModel):
    """Input for Google Calendar Generator."""

    dates: str = Field(
        ...,
        description=f"Datetime symbol for google calendar url.dates format should be like 'YYYYMMDDTHHMMSS/YYYYMMDDTHHMMSS'.Current time {datetime.date.today()}")
    title: str = Field(
        ...,
        description="Title symbol for google calendar.")
    description: str = Field(
        ...,
        description="Summary text symbol for google calendar url.")
    location: str = Field(
        ...,
        description="Calendar location symbol for google calendar url.")


class CalendarTool(BaseTool):
    name = "create_google_calendar_url"
    description = f"""
Generate Google Calendar API url from CalendarTextSplit text.
"""

    @staticmethod
    def create_gcal_url(
            title='看到這個..請重生',
            date='20230524T180000/20230524T220000',
            location='那邊',
            description=''):
        base_url = "https://www.google.com/calendar/render?action=TEMPLATE"
        event_url = f"{base_url}&text={urllib.parse.quote(title)}&dates={date}&location={urllib.parse.quote(location)}&details={urllib.parse.quote(description)}"
        return event_url+"&openExternalBrowser=1"

    def _run(self, dates: str, title: str, description: str, location: str):
        print('時間：'+dates)
        print('標題：'+title)
        print('描述：'+description)
        print('地點：'+location)
        result = self.create_gcal_url(title, dates, location, description)

        return result

    args_schema: Optional[Type[BaseModel]] = GoogleCalendarGeneratorInput
