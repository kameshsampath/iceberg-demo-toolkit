#!/usr/bin/env python
import argparse
import asyncio
import json

from aiokafka import AIOKafkaProducer
from dotenv import load_dotenv
from log.logger import get_logger as _logger
from producer.venicle_telematics import VehicleTelematicsGenerator

load_dotenv()

logger = _logger("vehicle_telematics_producer")


class AsyncTelemetryProducer:
    def __init__(
        self,
        bootstrap_servers: str,
        topic: str,
        max_batch_size: int,
        delay: int,
        generator_config: dict,
    ):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda x: json.dumps(x).encode("utf-8"),
            max_batch_size=max_batch_size,
        )
        self.topic = topic
        self.delay = delay
        self.generator = VehicleTelematicsGenerator(**generator_config)

    async def send_telemetry(self, telemetry_data):
        await self.producer.send_and_wait(self.topic, telemetry_data)
        logger.info(f"Sent telemetry for vehicle {telemetry_data['vehicle_id']}")

    async def run(self):
        await self.producer.start()
        try:
            while True:
                telemetry = self.generator.generate_telemetry()
                await self.send_telemetry(telemetry)
                await asyncio.sleep(self.delay)
        finally:
            await self.producer.stop()


def parse_args():
    parser = argparse.ArgumentParser(description="Vehicle Telemetry Data Generator")

    # Kafka settings
    kafka_group = parser.add_argument_group("Kafka Settings")
    kafka_group.add_argument("--bootstrap-servers", default="localhost:9092")
    kafka_group.add_argument("--topic", default="vehicle-telemetry")
    kafka_group.add_argument("--max-batch-size", type=int, default=16384)
    kafka_group.add_argument("--delay", type=float, default=1.0)

    # Generator settings
    gen_group = parser.add_argument_group("Generator Settings")
    gen_group.add_argument("--num-vehicles", type=int, default=50)
    gen_group.add_argument("--min-lat", type=float, default=25.0)
    gen_group.add_argument("--max-lat", type=float, default=48.0)
    gen_group.add_argument("--min-lon", type=float, default=-123.0)
    gen_group.add_argument("--max-lon", type=float, default=-71.0)
    gen_group.add_argument("--start-year", type=int, default=2018)
    gen_group.add_argument("--end-year", type=int, default=2025)

    # Logging
    parser.add_argument(
        "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO"
    )

    return parser.parse_args()


async def main():
    args = parse_args()

    global logger
    logger.setLevel(args.log_level)

    generator_config = {
        "num_vehicles": args.num_vehicles,
        "min_lat": args.min_lat,
        "max_lat": args.max_lat,
        "min_lon": args.min_lon,
        "max_lon": args.max_lon,
        "year_range": list(range(args.start_year, args.end_year + 1)),
    }

    producer = AsyncTelemetryProducer(
        bootstrap_servers=args.bootstrap_servers,
        topic=args.topic,
        max_batch_size=args.max_batch_size,
        delay=args.delay,
        generator_config=generator_config,
    )

    try:
        await producer.run()
    except KeyboardInterrupt:
        print("Stopping producer...")


if __name__ == "__main__":
    asyncio.run(main())
