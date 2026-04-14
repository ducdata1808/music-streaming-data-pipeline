# DBT Setup Guide

DBT (Data Build Tool) applies ELT transformations over the data managed by ClickHouse to create data marts.

## 1. Initialization

Install DBT (handled via `requirements.txt`). Check installation:
```bash
dbt --version
```

If setting up for the first time, run `dbt init <project_name>` (e.g., `dbt`).

## 2. Configuration (`profiles.yml`)

Ensure your profile is set up to interact with ClickHouse locally:
```yaml
music_events_transform:
  outputs:
    dev:
      type: clickhouse
      host: localhost
      port: 8123
      user: default
      password: ""
      database: music_analytics
      secure: False
  target: dev
```

## 3. Development Workflow

### Directories:
- **`models/staging/`**: Clean raw ClickHouse data tables.
- **`models/marts/`**: Final aggregations and business logic models.

### Basic Commands
Use `--profiles-dir .` if your `profiles.yml` is inside your project folder instead of your home `~/.dbt/` folder.

```bash
# Move to DBT folder
cd ~/eventsim_project/dbt

# Check connection
dbt debug --profiles-dir .

# Compile models
dbt compile --profiles-dir .

# Run the transformations
dbt run --profiles-dir .

# Test models (optional constraints checks)
dbt test --profiles-dir .
```

After dbt completes successfully, check tables directly from ClickHouse:
```sql
SHOW TABLES IN music_analytics;
SELECT * FROM stg_events LIMIT 5;
```
