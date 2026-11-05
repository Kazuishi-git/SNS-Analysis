from src.collect.client import XClient


def main() -> None:
    """ Test X API user information retrieval."""

    client = XClient()

    # テスト用ユーザーID、user_metrics.csvの上位三件
    user_ids = [
        "1631259691245535233",
        "2087565650487324672",
        "881130366978867200",
    ]

    response = client.get_users(user_ids)

    if response.data is None:
        print("No users returned.")
        return

    for user in response.data:
        metrics = user.public_metrics

        print(f"User ID: {user.id}")
        print(f"Followers: {metrics['followers_count']}")
        print(f"Following: {metrics['following_count']}")
        print(f"Tweets: {metrics['tweet_count']}")
        print(f"Listed: {metrics['listed_count']}")
        print("-" * 30)


if __name__ == "__main__":
    main()