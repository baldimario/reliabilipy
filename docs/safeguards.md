# Safeguards (Design by Contract)

Runtime assertions to enforce preconditions, invariants, and postconditions.

## API

- `assert_invariant(condition, message=None, fallback=None)`
- `require(precondition, message=None)`
- `ensure(postcondition, message=None)`

`InvariantViolation` is raised when conditions fail.

## Usage

```python
from reliabilipy import assert_invariant, require, ensure

@require(lambda: user.is_authenticated)
@ensure(lambda res: res is not None)
def get_data():
    ...

assert_invariant(lambda: queue.size() < 1000, "Queue too large")
```
