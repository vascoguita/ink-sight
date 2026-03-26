"""Ink-Sight application to fetch Google Calendar events."""

import argparse
import sys
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from icalevents.icalevents import events
from icalevents.icalparser import Event


@dataclass
class CalendarClient:
    """Client to interact with the iCal calendar feed."""

    url: str

    def _fetch_events(self) -> list[Event]:
        """Fetch events dynamically for the current narrow window."""
        now = datetime.now(UTC)
        start = now - timedelta(days=1)
        end = now + timedelta(days=1)
        return events(self.url, start=start, end=end, fix_apple=True, sort=True)

    def fetch_current_event(self) -> Event | None:
        """Fetch the currently ongoing event."""
        all_events = self._fetch_events()
        now = datetime.now(UTC)
        for event in all_events:
            if event.start is None or event.end is None:
                continue
            if event.start <= now < event.end:
                return event
        return None

    def fetch_next_event(self) -> Event | None:
        """Fetch the next upcoming event today."""
        all_events = self._fetch_events()
        now = datetime.now(UTC)
        for event in all_events:
            if event.start is None or event.end is None:
                continue
            if (
                event.start > now
                and event.start.astimezone().date() == now.astimezone().date()
            ):
                return event
        return None


class CalendarCLI:
    """CLI application to display today's calendar events."""

    def __init__(self) -> None:
        """Initialize the CLI application with an argument parser."""
        self.parser = argparse.ArgumentParser(
            description="Fetch Google Calendar events."
        )
        self.parser.add_argument(
            "-u",
            "--url",
            type=str,
            required=True,
            help="Secret address in iCal format.",
        )

    def run(self) -> None:
        """Execute the CLI application."""
        args = self.parser.parse_args()

        try:
            client = CalendarClient(url=args.url)
            current_event = client.fetch_current_event()
            next_event = client.fetch_next_event()

            if not current_event and not next_event:
                sys.stdout.write("No events found for today.\n")
                return

            if current_event and current_event.start and current_event.end:
                start_str = current_event.start.astimezone().strftime("%H:%M")
                end_str = current_event.end.astimezone().strftime("%H:%M")
                sys.stdout.write(
                    f"Current: {current_event.summary} from {start_str} to {end_str}\n"
                )

                total = max(
                    1.0, (current_event.end - current_event.start).total_seconds()
                )
                elapsed = (datetime.now(UTC) - current_event.start).total_seconds()
                filled = max(0, min(20, int(20 * elapsed / total)))

                filled_bar = "█" * filled
                empty_bar = "░" * (20 - filled)
                sys.stdout.write(f"[{filled_bar}{empty_bar}]\n")

            if next_event and next_event.start and next_event.end:
                start_str = next_event.start.astimezone().strftime("%H:%M")
                end_str = next_event.end.astimezone().strftime("%H:%M")
                sys.stdout.write(
                    f"Next: {next_event.summary} from {start_str} to {end_str}\n"
                )

        except (ValueError, OSError, RuntimeError) as e:
            sys.exit(f"Error fetching calendar: {e}")


if __name__ == "__main__":
    cli = CalendarCLI()
    cli.run()
