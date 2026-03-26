"""Ink-Sight application to fetch Google Calendar events."""

import argparse
import sys
from dataclasses import dataclass
from datetime import UTC, datetime

from icalevents.icalevents import events
from icalevents.icalparser import Event


@dataclass
class CalendarClient:
    """Client to interact with the iCal calendar feed."""

    url: str

    @staticmethod
    def _is_relevant_event(event: Event, current_time: datetime) -> bool:
        """Check if an event is ongoing or starts today in local time."""
        is_active = event.end > current_time
        starts_today_or_before = (
            event.start.astimezone().date() <= current_time.astimezone().date()
        )
        return is_active and starts_today_or_before

    def fetch_todays_events(self, count: int = 2) -> list[Event]:
        """Fetch today's current or next events from the calendar."""
        all_events = events(self.url)
        now = datetime.now(UTC)

        relevant_events = [
            event for event in all_events if self._is_relevant_event(event, now)
        ]
        relevant_events.sort(key=lambda e: e.start)
        return relevant_events[:count]


class CalendarCLI:
    """CLI application to display today's calendar events."""

    @staticmethod
    def create_parser() -> argparse.ArgumentParser:
        """Create and configure the command-line argument parser."""
        parser = argparse.ArgumentParser(description="Fetch Google Calendar events.")
        parser.add_argument(
            "-u",
            "--url",
            type=str,
            required=True,
            help="Secret address in iCal format.",
        )
        return parser

    @staticmethod
    def display_events(events: list[Event]) -> None:
        """Display the fetched calendar events to standard output."""
        if not events:
            sys.stdout.write("No events found for today.\n")
            return

        now = datetime.now(UTC)
        for event in events:
            start_str = event.start.astimezone().strftime("%H:%M")
            end_str = event.end.astimezone().strftime("%H:%M")
            prefix = "Current" if event.start <= now < event.end else "Next"
            msg = f"{prefix}: {event.summary} from {start_str} to {end_str}\n"
            sys.stdout.write(msg)

    def run(self) -> None:
        """Execute the CLI application."""
        args = self.create_parser().parse_args()

        try:
            client = CalendarClient(url=args.url)
            todays_events = client.fetch_todays_events()
            self.display_events(todays_events)
        except (ValueError, OSError, RuntimeError) as e:
            sys.exit(f"Error fetching calendar: {e}")


if __name__ == "__main__":
    cli = CalendarCLI()
    cli.run()
