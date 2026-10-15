from tweepy import Response
from datetime import datetime, UTC

from .client import XClient
from .models import Event, Tweet
from .writer import CSVWriter
from .state import StateManager

from src.utils.logger import logger

from tweepy.errors import TweepyException

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
        
        if state and state.get("event_id") == event.event_id:
            next_token = state.get("next_token")

        collected_count = 0

        logger.info("Start collecting event: %s", event.event_id)

        while collected_count < event.max_tweet:

            # 上限までに取得できる残り件数
            remaining_count = event.max_tweet - collected_count

            # 1ページ分の投稿を取得して保存
            try: 
                next_token, count  = self._collect_page(
                    event,
                    next_token,
                    remaining_count
                )

            except TweepyException:
                # API関連のエラーを記録し、上位へ伝える
                logger.exception(
                    "Failed to collect posts for event: %s",
                    event.event_id
                )
                raise

            collected_count += count

            # whileの中に置くことにより、一つずつ保存：checkpoint
            self.state.save(
                {
                    "event_id": event.event_id,
                    "next_token": next_token,
                    "updated_at": datetime.now(UTC).replace(microsecond=0).isoformat()
                }
            )

            logger.info(
                "Collected %d tweets (total: %d)",
                count,
                collected_count
            )

            if collected_count >= event.max_tweet:
                logger.info("Reached max_tweet (%d)", event.max_tweet)
                break

            if next_token is None:
                logger.info("No next page. Collection finished.")
                break


    def _collect_page(
            self,
            event: Event,
            next_token: str | None,
            remaining_count: int,
    ) -> tuple[str | None, int]:
        
        """ Collect a single page of posts and return the next_token."""
        
        page_response = self.client.search_posts(
            event = event,
            next_token = next_token,
        )

        page_tweets = self._convert_response(
            event = event,
            response = page_response,
        )

        page_tweets = page_tweets[:remaining_count]

        self.writer.write(
            filename=f"{event.event_id}.csv",
            tweets = page_tweets,

        )

        # meta or {} としておくことで、response.metaがNoneのとき、{}を使うようにし、Errorにならない
        meta = page_response.meta or {}

        next_token = meta.get("next_token")

        # 何件取得したかわかるようにlenを追加(7/22)
        return next_token, len(page_tweets)
