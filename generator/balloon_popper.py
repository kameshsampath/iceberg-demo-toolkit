#!/usr/bin/env python
import argparse
import asyncio
import json
import random
from datetime import datetime, timezone

from aiokafka import AIOKafkaProducer
from dotenv import load_dotenv
from log.logger import get_logger as _logger

load_dotenv()

logger = _logger("balloon_game_producer")


class BalloonGameGenerator:
    # Game configuration
    CARTOON_CHARACTERS = {
        "SpongeBob": ["yellow", "blue"],
        "Mickey": ["red", "black"],
        "Pikachu": ["yellow", "red"],
        "Bugs_Bunny": ["grey", "orange"],
        "Homer_Simpson": ["blue", "yellow"],
        "Scooby_Doo": ["brown", "green"],
        "Doraemon": ["blue", "white"],
        "Tom": ["grey", "blue"],
        "Jerry": ["brown", "yellow"],
    }

    BALLOON_SCORES = {
        "red": 100,
        "blue": 75,
        "green": 60,
        "yellow": 50,
        "purple": 40,
        "orange": 30,
        "grey": 45,
        "brown": 35,
        "black": 80,
        "white": 70,
    }

    def __init__(self, bonus_probability: float = 0.7):
        self.bonus_probability = bonus_probability

    def generate_pop(self):
        character = random.choice(list(self.CARTOON_CHARACTERS.keys()))

        if random.random() < self.bonus_probability:
            color = random.choice(self.CARTOON_CHARACTERS[character])
        else:
            color = random.choice(list(self.BALLOON_SCORES.keys()))

        return {
            "player": character,
            "balloon_color": color,
            "score": self.BALLOON_SCORES[color],
            "favorite_color_bonus": color in self.CARTOON_CHARACTERS[character],
            "event_ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }


class AsyncBalloonProducer:
    def __init__(
        self,
        bootstrap_servers: str,
        topic: str,
        max_batch_size: int,
        delay: float,
        generator_config: dict,
    ):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda x: json.dumps(x).encode("utf-8"),
            max_batch_size=max_batch_size,
        )
        self.topic = topic
        self.delay = delay
        self.generator = BalloonGameGenerator(**generator_config)

    async def send_pop(self, pop_data):
        await self.producer.send_and_wait(self.topic, pop_data)
        bonus_text = (
            " (Favorite color bonus!)" if pop_data["favorite_color_bonus"] else ""
        )
        logger.info(
            f"Player {pop_data['player']} popped a {pop_data['balloon_color']} "
            f"balloon for {pop_data['score']} points!{bonus_text}"
        )

    async def run(self):
        await self.producer.start()
        try:
            while True:
                pop_data = self.generator.generate_pop()
                await self.send_pop(pop_data)
                await asyncio.sleep(self.delay)
        finally:
            await self.producer.stop()


def parse_args():
    parser = argparse.ArgumentParser(description="Balloon Game Data Generator")

    # Kafka settings
    kafka_group = parser.add_argument_group("Kafka Settings")
    kafka_group.add_argument("--bootstrap-servers", default="localhost:9092")
    kafka_group.add_argument("--topic", default="balloon-game")
    kafka_group.add_argument("--max-batch-size", type=int, default=16384)
    kafka_group.add_argument("--delay", type=float, default=1.0)

    # Generator settings
    gen_group = parser.add_argument_group("Generator Settings")
    gen_group.add_argument(
        "--bonus-probability",
        type=float,
        default=0.7,
        help="Probability of getting favorite color (0-1)",
    )

    # Logging
    parser.add_argument(
        "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO"
    )

    return parser.parse_args()


async def main():
    args = parse_args()

    global logger
    logger.setLevel(args.log_level)

    generator_config = {"bonus_probability": args.bonus_probability}

    producer = AsyncBalloonProducer(
        bootstrap_servers=args.bootstrap_servers,
        topic=args.topic,
        max_batch_size=args.max_batch_size,
        delay=args.delay,
        generator_config=generator_config,
    )

    try:
        logger.info("Starting balloon game producer...")
        await producer.run()
    except KeyboardInterrupt:
        logger.info("Stopping balloon game producer...")
    except Exception as e:
        logger.error(f"Error in balloon game producer: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
