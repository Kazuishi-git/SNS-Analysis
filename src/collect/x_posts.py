from .client import XClient
from .models import Event
from .writer import CSVWriter
from .state import StateManager

class XPostCollector:
    """ Implement the post collection workflow. """
    def __init__(self):
        self.client = XClient()
        self.writer = CSVWriter()
        self.state = StateManager()


def collect(self,
            event: Event,
            ) -> None:
    
    """ Collect posts for the given event. """

    # Load previous state
    

    # Fetch tweets

    # Save tweets

    # Update state

    pass
