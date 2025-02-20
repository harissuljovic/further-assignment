## Test automation assignment - Further

### Installation

1. Install python3 https://www.python.org/downloads/

2. Install playwright `pip3 install pytest-playwright`
3. Install the required browsers with `playwright install`

3. For parallel running install pytest-xdist 

`pip3 install pytest-xdist`

4. For test reporting install pytest-html
`pip3 install pytest-html
`

### How to run Functional E2E Tests

From project root execute:
`pytest tests/test_task1.py`

To run i.e. 2 tests in parallel execute:
`pytest -n 2 tests/test_task1.py `

To run tests in parallel and generate HTML report run:

`pytest -n 2 tests/test_task1.py --maxfail=2 --disable-warnings -q --tb=short --html=report.html`



