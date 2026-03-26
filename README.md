# ink-sight

Raspberry Pi assistant that syncs Google Calendar events to a Pimoroni Inky pHAT e-ink display.

## How to use

Run the application and pass your iCal secret address:

```bash
uv run main.py --url "YOUR_ICAL_SECRET_ADDRESS"
```

## How to get your iCal URL

1. Go to Google Calendar -> **Settings and sharing** -> **Integrate calendar**
2. Copy the **'Secret address in iCal format'**
