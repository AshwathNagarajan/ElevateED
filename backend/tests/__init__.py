"""
Test suite for ElevateED backend.

This package contains all pytest tests for the FastAPI backend.

To run tests:
    pytest                          # Run all tests
    pytest -v                       # Verbose output
    pytest tests/test_auth.py       # Run specific test file
    pytest tests/test_auth.py::TestLogin   # Run specific test class
    pytest -k login                 # Run tests matching pattern

Environment:
    - Tests use SQLite in-memory database (isolated)
    - No production credentials required
    - All fixtures automatically clean up after tests
"""
