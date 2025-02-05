#!/usr/bin/env python3
import argparse
import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from aiokafka import AIOKafkaConsumer
from dotenv import load_dotenv
from log.logger import get_logger as _logger

load_dotenv()
logger = _logger("kafka_consumer")


class DataConsumer:
    def __init__(
        self,
        topic: str,
        bootstrap_servers: str,
        group_id: str,
        output_dir: Path,
        batch_size: int = 100,
        auto_offset_reset: str = "earliest",
        data_processor: Optional[Callable[[Dict], Dict]] = None,
        file_prefix: Optional[str] = None,
        file_suffix: str = ".json",
    ):
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.output_dir = Path(__file__).parent.parent / output_dir
        self.batch_size = batch_size
        self.auto_offset_reset = auto_offset_reset
        self.data_processor = data_processor
        self.file_prefix = file_prefix if file_prefix is not None else f"{self.topic}_"
        self.file_suffix = file_suffix

        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            value_deserializer=lambda x: json.loads(x.decode("utf-8")),
            group_id=self.group_id,
            auto_offset_reset=self.auto_offset_reset,
        )

    def get_output_file(self) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.file_prefix}{self.topic}_{timestamp}{self.file_suffix}"
        return self.output_dir / self.topic / filename

    async def process_message(self, message: Any) -> Dict:
        """Process a single message with optional custom processing"""
        if self.data_processor:
            return self.data_processor(message)
        return message

    async def write_batch(self, data: List[Dict], output_file: Path):
        """Write a batch of data to file"""
        logger.debug(f"Writing {len(data)} records to {output_file}")
        output_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            existing_data = []
            if output_file.exists():
                with open(output_file, "r") as f:
                    existing_data = json.load(f)
                    if not isinstance(existing_data, list):
                        existing_data = [existing_data]

            with open(output_file, "w") as f:
                json.dump(existing_data + data, f, indent=2)
            logger.info(f"Wrote {len(data)} records to {output_file}")
        except Exception as e:
            logger.error(f"Error writing to {output_file}: {e}")
            raise

    async def run(self):
        """Main consumer loop"""
        data_buffer = []
        output_file = self.get_output_file()

        try:
            await self.consumer.start()
            logger.info(f"Started consuming from topic: {self.topic}")

            async for msg in self.consumer:
                try:
                    processed_data = await self.process_message(msg.value)
                    data_buffer.append(processed_data)
                    logger.debug(f"Received: {processed_data}")

                    if len(data_buffer) >= self.batch_size:
                        await self.write_batch(data_buffer, output_file)
                        data_buffer = []
                        output_file = (
                            self.get_output_file()
                        )  # Create new file for next batch
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    continue

        except KeyboardInterrupt:
            logger.info("Shutting down consumer...")
        finally:
            if data_buffer:
                await self.write_batch(data_buffer, output_file)
            await self.consumer.stop()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generic Kafka Consumer with JSON output",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("-t", "--topic", required=True, help="Kafka topic to consume")
    parser.add_argument(
        "-b",
        "--bootstrap-servers",
        default="localhost:9092",
        help="Kafka bootstrap servers",
    )
    parser.add_argument(
        "-g",
        "--group-id",
        default=str(uuid.uuid4()),
        help="Kafka consumer group ID",
    )
    parser.add_argument(
        "-o", "--output-dir", type=str, default="work", help="Base output directory"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Number of records to accumulate before writing",
    )
    parser.add_argument(
        "--offset-reset",
        choices=["earliest", "latest"],
        default="earliest",
        help="Consumer offset reset policy",
    )
    parser.add_argument("--file-prefix", default=None, help="Prefix for output files")
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )

    return parser.parse_args()


async def main():
    args = parse_args()
    logger.setLevel(args.log_level)

    consumer = DataConsumer(
        topic=args.topic,
        bootstrap_servers=args.bootstrap_servers,
        group_id=args.group_id,
        output_dir=args.output_dir,
        batch_size=args.batch_size,
        auto_offset_reset=args.offset_reset,
        file_prefix=args.file_prefix,
    )

    await consumer.run()


if __name__ == "__main__":
    asyncio.run(main())
