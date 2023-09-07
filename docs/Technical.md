# Technical Documentation for Discord Bot

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
- [Code Structure](#code-structure)
  - [Project Layout](#project-layout)
  - [Main Modules](#main-modules)
- [Testing](#testing)
- [Deployment](#deployment)
  - [Docker Deployment](#docker-deployment)

---

## Architecture Overview

The Discord bot is designed as a modular application using Python. It uses the discord.py library for Discord API interactions and Azure Tables for data storage. The bot is organized into separate modules, each handling different sets of functionalities and loaded in via cogs. It also uses Docker for deployment.

---

## Getting Started

### Prerequisites

- Python 3.x
- Docker (Optional)

### Installation

1. Clone the repository.
2. Navigate to the project directory.
3. Run `pip install -r requirements.txt`.

### Environment Variables

The project uses a .env file to manage environment variables:

- `DISCORD_TOKEN`: Your Discord Bot Token.
- `AZURE_CONNECTION_STRING`: Azure Tables connection string.

Make a copy of the .env.template and rename it to just .env. Populate the variables with the correct values.

---

## Code Structure

### Project Layout

- `main.py`: Entry point for the Discord bot.
- `helpers.py`: Utility functions and helper code.
- `timetracker.py`: Time tracking functionalities.
- `vod.py`: Video-on-demand functionalities.
- `test_helpers.py`: Tests for helper functions.
- `requirements.txt`: Project dependencies.
- `dockerfile`: Docker configuration.
- `.env`: Environment variables.
- `CHANGELOG.md`: Log of changes made to the project.
- `README.md`: User documentation for the bot commands.

### Main Modules

#### `helpers.py`

Contains utility functions and helper code. The module is imported into other modules to reduce code repetition.

#### `timetracker.py`

Handles all time-tracking functionalities. Extends `commands.Cog` from discord.py to create a set of commands related to time tracking.

#### `vod.py`

Manages video-on-demand functionalities. Also extends `commands.Cog` from discord.py.

---

## Testing

Unit tests are available in the tests direcory. Currently the only test file is `test_helpers.py`. To run the tests, execute `pytest`.

---

## Deployment

### Docker Deployment

The project includes a `dockerfile` for Docker-based deployment.

1. Build the Docker image: `docker build -t companybot:1.0.0 .`
2. Run the Docker container: `docker run -d companybot:1.0.0`

---
