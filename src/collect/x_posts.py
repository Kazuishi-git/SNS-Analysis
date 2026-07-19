from tweepy import Response
from datetime import datetime, UTC

from .client import XClient
from .models import Event, Tweet
from .writer import CSVWriter
from .state import StateManager

class XPostCollector:
    """ Implement the post collection workflow. """
    def __init__(self):
        self.client = XClient()
        self.writer = CSVWriter()
        self.state = StateManager()

    # 最初の _ は内部でしか使わない、外から呼び出さないことの印
    def _convert_response(
            self,
            event: Event,
            response: Response,
    ) -> list[Tweet]:
        """ Convert an X API response into Tweet object. """

        tweets: list[Tweet] = []

        if response.data is None:
            return tweets
        
        retrieved_at = datetime.now(UTC)
        
        for post in response.data:
            tweet = Tweet(
                event_id=event.event_id,
                tweet_id=str(post.id),
                author_id=str(post.author_id),
                created_at=post.created_at,
                retrieved_at=post.retrieved_at,
                text=post.text,
                likes=post.public_metrics["like_count"],
                retweets=post.public_metrics["retweet_count"],
                replies=post.public_metrics["reply_count"],
                quotes=post.public_metrics["quote_count"],
            )

            tweets.append(tweet)

    
        return tweets

# collectは司令塔、必要最低限の動きしかかさせない
    def collect(self,
                event: Event,
                ) -> None:
        
        """ Collect posts for the given event. """

        # Load previous state
        state = self.state.load()

        # Fetch tweets
        next_token = None
        
        if state:
            next_token = state.get("next_token")

        response = self.client.search_posts(
            event=event,
            next_token=next_token,
        )

        tweets = self._convert_response(response)

        # Save tweets
        self.writer.write(
            filename=f"{event.event_id}.csv",
            tweets=tweets,
        )

         # update state
         