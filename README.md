# Green-Rock

Adaptive ETF Portfolio Project Dashboard.

## Running Locally

1. Set up the virtual environment: `make install`
2. Run the application: `make run`

Or via Docker:
`docker-compose up`

## Architecture

Follows decoupled hexagonal principles:
- `src/green_rock/adapters/`: Infrastructure interaction.
- `src/green_rock/domain/`: Core business logic.
- `src/green_rock/service_layer/`: Use cases.
- `src/green_rock/entrypoints/`: Streamlit app strictly.
