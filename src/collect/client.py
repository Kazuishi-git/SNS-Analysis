from tweepy import Response, Client
from src.utils.config import BEARER_TOKEN
from .models import Event

class XClient:

    DEFAULT_TWEET_FIELDS = (
        "created_at",
        "author_id",
        "public_metrics",
        "text",
    )

    DEFAULT_USER_FIELDS = (
        "public_metrics",
    )

    DEFAULT_MAX_RESULT = 100

    def __init__(self) -> None:
        self.client = Client(
            bearer_token = BEARER_TOKEN,
            wait_on_rate_limit = True,
        )

    def search_posts(
        self,
        event : Event,
        next_token : str | None = None,
    ) -> Response:
        response = self.client.search_all_tweets(
            query=event.query,
            start_time=event.start_time,
            end_time=event.end_time,
            tweet_fields=self.DEFAULT_TWEET_FIELDS,
            max_results=self.DEFAULT_MAX_RESULT,
            next_token=next_token,
        )

    def get_users(
            self,
            user_ids: list[str],
    ) -> Response:

        """ Fetch user information for the given user IDs. """

        response = self.client.get_users(
            ids = user_ids,
            user_fields = self.DEFAULT_USER_FIELDS,
        )

        return response