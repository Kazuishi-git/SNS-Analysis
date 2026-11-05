from src.collect.client import XClient


def main() -> None:
    # 取得されなかった理由の解明
    """ Check why some users were not collected."""

    client = XClient()

    user_ids = [
        "1708178285081792512",
        "1824558013639995392",
        "1998768935836241920",
        "2030334553261592576",
        "2056295166651314176",
        "2074671330016808960",
        "2077008953142398976",
        "2093272261184888832",
        "846184620",
    ]

    response = client.get_users(user_ids)

    returned_ids = set()

    if response.data:
        for user in response.data:
            returned_ids.add(str(user.id))

            print(f"User ID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Public metrics: {user.public_metrics}")
            print("-" * 30)

    missing_ids = set(user_ids) - returned_ids

    print(f"\nRequested: {len(user_ids)}")
    print(f"Returned: {len(returned_ids)}")
    print(f"Not returned: {len(missing_ids)}")

    if missing_ids:
        print("\nNot returned IDs:")
        for user_id in sorted(missing_ids):
            print(user_id)


if __name__ == "__main__":
    main()
