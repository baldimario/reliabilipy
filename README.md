# reliabilipy

A comprehensive Python library for building reliable software with retries, circuit breakers, state management, and more.

## Features

- 🔄 **Retry with Backoff**: Configurable retry mechanisms with exponential/linear backoff and jitter
- 💾 **State Persistence**: Automatic state management with file or Redis backend
- 🔌 **Circuit Breaker**: Prevent cascading failures in distributed systems
- ⏱ **Timeouts and Fallbacks**: Handle slow operations gracefully
- 🧪 **Assertions and Safeguards**: Runtime invariant checking
- 🔥 **Failure Injection**: Tools for chaos engineering and reliability testing
- 🧠 **Metrics and Observability**: Built-in monitoring and Prometheus integration

## Installation

```bash
pip install reliabilipy
```

## Quick Start

### Retry with Backoff

```python
from reliabilipy import retry

@retry(
    exceptions=(IOError,),
    backoff='exponential',
    max_retries=5,
    jitter=True
)
def fetch_data():
    # Your potentially flaky network code here
    pass
```

### State Management

```python
from reliabilipy import StateManager

# File-based state management
state = StateManager(backend='file', namespace='myapp')
state.set("last_processed_id", 123)
last_id = state.get("last_processed_id")

# Redis-based state management
redis_state = StateManager(
    backend='redis',
    namespace='myapp',
    redis_url='redis://localhost:6379'
)
```

### Circuit Breaker

```python
from reliabilipy import circuit_breaker

@circuit_breaker(
    failure_threshold=5,
    recovery_timeout=60,
    exceptions=(ConnectionError,)
)
def call_external_api():
    # Your API call here
    pass
```

### Timeouts and Fallbacks

```python
from reliabilipy import with_timeout

@with_timeout(timeout=5, fallback=lambda: "default_value")
def slow_operation():
    # Your potentially slow code here
    pass
```

### Assertions and Safeguards

```python
from reliabilipy import assert_invariant, require, ensure

@require(lambda: user.is_authenticated)
@ensure(lambda result: len(result) > 0)
def get_user_data():
    # Your code here
    pass

assert_invariant(
    lambda: system.active_connections < 1000,
    "Too many active connections"
)
```

### Failure Injection

```python
from reliabilipy import inject_failure, inject_latency

@inject_failure(rate=0.1, exception=RuntimeError)
def flaky_service():
    # Your code here
    pass

@inject_latency(min_delay=0.1, max_delay=1.0)
def slow_service():
    # Your code here
    pass
```

### Metrics and Observability

```python
from reliabilipy import observe, MetricsCollector

metrics = MetricsCollector(namespace="myapp")

@observe(name="process_data", metrics=metrics)
def process_data():
    # Your code here
    pass
```

## Web Framework Integration

```python
from reliabilipy import ReliabilityMetricsMiddleware

# FastAPI example
app = FastAPI()
app.add_middleware(ReliabilityMetricsMiddleware)
```

## Examples

The `examples/` directory contains several real-world examples demonstrating how to use reliabilipy. To run the examples, first install the required dependencies:

```bash
poetry install
poetry run pip install requests  # Required for web_scraper.py and api_client.py
```

### Web Scraper (`examples/web_scraper.py`)
A resilient web scraper that demonstrates:
- Exponential backoff retry on network failures
- Circuit breaker to prevent hammering failing services
- Automatic handling of transient HTTP errors

```bash
poetry run python examples/web_scraper.py
```

Example output:
```
Successfully fetched page: 1234 bytes
# or if the service is down:
Circuit breaker is open: Service unavailable
```

### Data Pipeline (`examples/data_pipeline.py`)
A robust data processing pipeline showing:
- State persistence to resume after failures
- Batch processing with checkpoints
- Metrics collection for monitoring
- Automatic state recovery

```bash
poetry run python examples/data_pipeline.py
```

Watch the pipeline process data with automatic state management:
```
Resuming from position: 0
Processed batch: 0-10
Processed batch: 10-20
...
```

### Microservice (`examples/microservice.py`)
A chaos engineering example demonstrating:
- Random failure injection for resilience testing
- Invariant checking for business rules
- Latency simulation
- Automatic error recovery

```bash
poetry run python examples/microservice.py
```

See how the service handles different failure scenarios:
```
Created users successfully
Retrieved user: User(id=1, name="Alice", balance=0.0)
Transfer succeeded
Alice's balance: 50.0
Bob's balance: 50.0
```

### API Client (`examples/api_client.py`)
A production-ready API client showcasing:
- Timeout handling with smart fallbacks
- In-memory caching
- Circuit breaker protection
- Prometheus metrics integration
- Multiple error handling strategies

```bash
poetry run python examples/api_client.py
```

Watch it handle various API scenarios:
```
Current weather: {'temperature': 20, 'condition': 'sunny', 'source': 'api'}
# If API is slow:
Current weather: {'temperature': 20, 'condition': 'unknown', 'source': 'fallback'}
# With cache:
Current weather: {'temperature': 20, 'condition': 'sunny', 'source': 'cache'}

Three day forecast:
Day 0: sunny (api)
Day 1: cloudy (api)
Day 2: rain (cache)
```

Each example includes comprehensive error handling and demonstrates multiple reliabilipy features working together. You can modify the configuration values (like timeouts, retry counts, etc.) in the examples to see how the system behaves under different conditions.

## Monitoring with Prometheus

To view the metrics collected by reliabilipy, you can set up Prometheus locally using Docker:

1. Create a Prometheus configuration file `prometheus.yml`:
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'reliabilipy'
    static_configs:
      - targets: ['host.docker.internal:8000']
```

2. Start Prometheus with Docker:
```bash
# Run Prometheus container
docker run -d \
    --name prometheus \
    --network host \
    -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
    prom/prometheus
```

3. Start your Python application with metrics endpoint:
```python
from prometheus_client import start_http_server

# Start metrics server before your application
start_http_server(8000)

# Your application code here...
```

or simply run the `api_client.py` example

```python
poetry run python examples/api_client.py
```

Then on prometheus look for api_client

4. View metrics in Prometheus UI:
- Open http://localhost:9090 in your browser
- Go to "Graph" tab
- Search for metrics like:
  - `api_client_function_duration_seconds` - Function execution times
  - `api_client_retry_attempts_total` - Number of retry attempts
  - `api_client_circuit_state` - Circuit breaker states

Available metrics include:
- Function duration histograms
- Retry attempt counters
- Circuit breaker state gauges
- State operation counters
- Error counters

All metrics are automatically labeled with function names and other relevant information.

## Testing

To install the package and run tests:

```bash
# Install the package with dependencies
poetry install

# Run tests with coverage report
poetry run pytest --cov=reliabilipy

# Run tests verbosely
poetry run pytest -v
```


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
