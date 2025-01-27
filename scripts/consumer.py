#!/usr/bin/env python3
import argparse
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path

from aiokafka import AIOKafkaConsumer
from dotenv import load_dotenv
from log.logger import get_logger as _logger

load_dotenv()
logger = _logger("vehicle_telemetry_consumer")
logger.setLevel("DEBUG")


async def consume_telemetry(
    topic: str,
    bootstrap_servers: str,
    group_id: str,
    output_file: str,
    batch_size: int = 100,
    auto_offset_reset: str = "earliest",
):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        group_id=group_id,
        auto_offset_reset=auto_offset_reset,
    )

    telemetry_data = []
    try:
        await consumer.start()
        logger.info(f"Started consuming from topic: {topic}")

        async for msg in consumer:
            data = msg.value
            telemetry_data.append(data)

            logger.debug(f"Received: {json.dumps(data)}")
            logger.info(
                f"Received: Vehicle: {data['vehicle_id']}, "
                f"Time: {data['timestamp']}, "
                f"Speed: {data['speed']} km/h, "
                f"Location: ({data['location']['latitude']}, {data['location']['longitude']}), "
                f"Battery: {data['battery_voltage']}V"
            )

            if len(telemetry_data) >= batch_size:
                await write_batch(telemetry_data, output_file)
                telemetry_data = []

    except KeyboardInterrupt:
        logger.info("Shutting down consumer...")
    finally:
        if telemetry_data:
            await write_batch(telemetry_data, output_file)
        await consumer.stop()


async def write_batch(data: list, output_file: str):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    try:
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                existing_data = json.load(f)
                if isinstance(existing_data, list):
                    data = existing_data + data

        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Wrote {len(data)} records to {output_file}")
    except Exception as e:
        logger.error(f"Error writing to {output_file}: {e}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Consume vehicle telemetry data and write to JSON",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-t",
        "--topic",
        type=str,
        default="vehicle-telemetry",
        help="Kafka topic to consume",
    )
    parser.add_argument(
        "-b",
        "--bootstrap-servers",
        type=str,
        default="localhost:9092",
        help="Kafka bootstrap servers",
    )
    parser.add_argument(
        "-g",
        "--group-id",
        type=str,
        default="vehicle-telemetry-cli2",
        help="Kafka consumer group ID",
    )
    parser.add_argument(
        "-o",
        "--offset-reset",
        type=str,
        default="earliest",
        help="Kafka Offset reset policy",
    )
    parser.add_argument(
        "-f",
        "--output-file",
        type=str,
        default=f"telemetry_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        help="Output JSON file path",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Number of records to accumulate before writing",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(
        consume_telemetry(
            topic=args.topic,
            bootstrap_servers=args.bootstrap_servers,
            group_id=args.group_id,
            output_file=Path("work").joinpath(args.output_file),
            batch_size=args.batch_size,
            auto_offset_reset=args.offset_reset,
        )
    )
