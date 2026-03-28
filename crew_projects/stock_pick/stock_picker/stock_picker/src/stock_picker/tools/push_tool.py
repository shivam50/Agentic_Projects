from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os
import requests


class PushNotificationInput(BaseModel):
    """Message to be sent to the user."""
    message: str = Field(..., description="DThe message to be sent to the user")

class PushNotificationTool(BaseTool):
    name: str = "Send a push notification"
    description: str = (
        "This tool is used to send a push notification to the user"
    )
    args_schema: Type[BaseModel] = PushNotificationInput

    def _run(self, message: str) -> str:
        # Implementation goes here
        pushover_user = os.getenv("PUSHOBER_USER")
        pushover_token = os.getenv("PUSHOVER_TOKEN")
        pushover_url = ""
