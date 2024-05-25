import redis
import time
import datetime
import json

EXPIRY_TIME = 3600


class RedisClient:
    def __init__(self):
        self.redis_client = redis.StrictRedis(
            host="localhost", port=6379, db=0, decode_responses=True
        )
        self.redis_client.flushall()

    def store_messages(self, messages):
        current_time = time.time()
        for topic, topic_messages in messages.items():
            for message in topic_messages:
                message_data = {
                    "topic": message["topic_long"],
                    "topic_long": message["topic"],
                    "topic_readable": message["topic_readable"],
                    "size": message["size"],
                    "timestamp": datetime.datetime.now().isoformat(),
                }
                serialized_message = json.dumps(message_data)
                self.redis_client.zadd("messages", {serialized_message: current_time})

    def get_messages(self):
        current_time = time.time()
        # Remove expired messages
        self.redis_client.zremrangebyscore("messages", 0, current_time - EXPIRY_TIME)
        messages = self.redis_client.zrangebyscore(
            "messages", current_time - EXPIRY_TIME, current_time
        )
        decoded_messages = {}
        for msg in messages:
            try:
                decoded_msg = json.loads(msg)
                topic = decoded_msg.get(
                    "topic_long"
                )  # Assuming 'topic' is present in the message
                if topic not in decoded_messages:
                    decoded_messages[topic] = []
                decoded_messages[topic].append(decoded_msg)
            except json.JSONDecodeError as e:
                print(f"Error decoding message: {msg}. Error: {e}")
        return decoded_messages
