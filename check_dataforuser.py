import pandas as pd

from src.utils.config import RAW_DATA_DIR, RESULT_DIR


OUTPUT_DIR = RESULT_DIR / "influencer"

user_er = pd.read_csv(OUTPUT_DIR / "user_engagement_rate.csv")

# print("\nER Distribution:")
# print(user_er["avg_er"].describe(
#     percentiles=[0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
# ))

# print("\nTop 10 Users by Average ER:")
# print(
#     user_er.sort_values("avg_er", ascending=False)
#     [[
#         "author_id",
#         "followers_count",
#         "post_count",
#         "avg_er",
#         "median_er",
#         "total_engagement",
#     ]]
#     .head(10)
#     .to_string(index=False)
# )

# 複数投稿ユーザーを抽出
repeat_users = user_er[user_er["post_count"] >= 2].copy()

# print(f"Users with 2<= posts: {len(repeat_users)}")

# print("\nTop 10 Users by Average ER (2<= posts):")
# print(
#     repeat_users.sort_values("avg_er", ascending=False)
#     [[
#         "author_id",
#         "followers_count",
#         "post_count",
#         "avg_er",
#         "median_er",
#         "total_engagement",
#     ]]
#     .head(10)
#     .to_string(index=False)
# )

# print("\nTop 10 Users by Total Engagement (2<= posts):")
# print(
#     repeat_users.sort_values("total_engagement", ascending=False)
#     [[
#         "author_id",
#         "followers_count",
#         "post_count",
#         "avg_er",
#         "median_er",
#         "total_engagement",
#     ]]
#     .head(10)
#     .to_string(index=False)
# )

# 投稿数3件以上のユーザー
consistent_users = user_er[
    user_er["post_count"] >= 3
].copy()

print(f"Users with 3<= posts: {len(consistent_users)}")

print("\nTop 10 Users by Median ER (3<= posts):")
print(
    consistent_users.sort_values(
        "median_er", ascending=False
    )[
        [
            "author_id",
            "followers_count",
            "post_count",
            "avg_er",
            "median_er",
            "total_engagement",
        ]
    ]
    .head(10)
    .to_string(index=False)
)

print("\nER Distribution (3<= posts):")
print(
    consistent_users["median_er"].describe(
        percentiles=[0.25, 0.50, 0.75, 0.90, 0.95]
    )
)