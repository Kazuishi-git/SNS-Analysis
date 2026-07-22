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

            metrics = post.public_metrics

            tweet = Tweet(
                event_id=event.event_id,
                tweet_id=str(post.id),
                author_id=str(post.author_id),
                created_at=post.created_at,
                retrieved_at=retrieved_at,
                text=post.text,
                likes=metrics["like_count"],
                retweets=metrics["retweet_count"],
                replies=metrics["reply_count"],
                quotes=metrics["quote_count"],
            )

            tweets.append(tweet)

    
        return tweets

# collectは司令塔、必要最低限の動きしかかさせない
    def collect(
            self,
            event: Event,
            ) -> None:
        
        """ Collect all posts for the given event. """

        # Load previous state
        state = self.state.load()

        # Fetch posts from X API
        next_token = None
        
        if state:
            next_token = state.get("next_token")

        """ _collect_page が・・・

        response = self.client.search_posts(
            event=event,
            next_token=next_token,
        )

        # _convert_responseの引数を変更したので、変更(7/22)
        tweets = self._convert_response(
            filename=f"{event.event_id}.csv",
            tweets=tweets,
            )

        # update state
        meta = response.meta or {}

        next_token = meta.get("next_token")

        ・・・これらを代わりにやってくれるようになった(7/22)"""

        while True :
            next_token = self._collect_page(
                event,
                next_token,
            )

            # whileの中に置くことにより、一つずつ保存：checkpoint
            self.state.save(
                {
                    "event_id": event.event_id,
                    "next_token": next_token,
                }
            )

            if next_token is None:
                break


    def _collect_page(
            self,
            event: Event,
            next_token: str | None,
    ) -> str | None:
        
        """ Collect a single page of posts and return the next_token."""
        
        page_response = self.client.search_posts(
            event = event,
            next_token = next_token,
        )

        page_tweets = self._convert_response(
            event = event,
            response = page_response,
        )
        self.writer.write(
            filename=f"{event.event_id}.csv",
            tweets = page_tweets,

        )

        # meta or {} としておくことで、response.metaがNoneのとき、{}を使うようにし、Errorにならない
        meta = page_response.meta or {}

        next_token = meta.get("next_token")

        return next_token
