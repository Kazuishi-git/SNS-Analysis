"""Project logger configuration"""
# printよりも将来的にloggerの方がINFO,ERROR,WARNINGなどの重要度ごとのログを作れるため良い

import logging

logger = logging.getLogger("SNS-Analysis")
logger.setLevel(logging.INFO)

# if とすることで、同じloggerが何度初期化されてもHandlerが重複して追加されない
if not logger.handlers:

    handler = logging.StreamHandler()

    formatter = logging.Formatter(
        "[%(levelname)s] %(message)s"
    )

    handler.setFormatter(formatter)

    logger.addHandler(handler)