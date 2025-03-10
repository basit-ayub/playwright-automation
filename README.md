
# Automated Browser Interaction Script Using Playwright

## Overview
This script uses Playwright to simulate human-like browsing behavior across multiple websites. It supports parallel browser instances, session management, and logging of interactions in JSON format.

## Requirements
- Python 3.7+
- Playwright
- asyncio

## Installation
1. Clone this repository or download the script.
2. Install dependencies using:
   ```sh
   pip install playwright
   playwright install
   ```

## Usage
Run the script using:
```sh
python script.py [options]
```
### CLI Options:
- `-w`, `--websites <num>`: Number of websites per browser instance.
- `-i`, `--instances <num>`: Number of parallel browser instances.


Example:
```sh
python script.py -w 5 -i 2
```

## Features
- Simulates human browsing (scrolling, hovering, clicking, typing).
- Stores browsing sessions to maintain state across runs.
- Logs interactions for analysis.

## Logging & Sessions
- Logs are stored in `logs/` as JSON files.
- Session data is stored in `sessions/` to persist browser state.

## Error Handling
Handles timeouts, network failures, and missing elements gracefully, logging errors when encountered.

## Notes
- Ensure Playwright is installed before running.
- Default settings visit 10 websites per instance with 3 instances in parallel.


