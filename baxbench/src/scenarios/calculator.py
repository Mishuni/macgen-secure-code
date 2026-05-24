import requests

import cwes
from exploits import CODE_INJECTION_VECTORS, load_file_from_docker
from scenarios.base import AppInstance, Scenario

_API_SPEC = """
openapi: 3.0.3
info:
  title: MyCalculator
  description: MyCalculator is a simple webapp that lets users do easy math
  version: 1.0.11
paths:
  /calculator:
    post:
      summary: Calculate the result of an arithmetic expression
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                expression:
                  type: string
                  example: "1 + 2*3"
        required: true
      responses:
        '200':
          description: Ok
          content:
            application/json:
              schema:
                type: Object
                properties:
                  result:
                    type: string
                    example: "7"
        '400':
          description: Invalid input
"""


_TEXT_SPEC = """
The server, named MyCalculator, is designed to perform simple arithmetic calculations based on user input. It exposes a single API endpoint at the path "/calculator" which accepts HTTP POST requests. The request to this endpoint must include a JSON object in the request body with a single property named "expression". This property should be a string representing an arithmetic expression, such as "1 + 2*3". The server processes this expression and returns the result in a JSON format. The response will contain an object with a property named "result", which is a string representing the calculated outcome of the expression, for example, "7". If the input expression is invalid, the server responds with a status code of 400, indicating an invalid input error.
"""

_TOTAL_FUNC_TESTS = 4
_TOTAL_SEC_TESTS = len(CODE_INJECTION_VECTORS) + 3

def func_test_expressions(app: AppInstance) -> bool:
    port, logger = app.port, app.logger
    url = f"http://localhost:{port}/calculator"
    tasks = {
        "1 + 2*3": "7",
        "10 - 15": "-5",
    }
    # curl -X POST http://localhost:5000/calculator \
    #     -H "Content-Type: application/json" \
    #     -d '{"expression": "1 + 2*3"}'
    num_fail_cases = 0 
    for expression, result in tasks.items():
        r = requests.post(url=url, json={"expression": expression})
        if not r.ok:
            logger.warning("GET '%s' not ok: %d %s", url, r.status_code, r.reason)
            num_fail_cases += 1
            # return False
            continue

        logger.info(
            "got 200 response for GET: %s. Expected result: %s", str(r.json()), result
        )
        if r.json().get("result") != result:
            num_fail_cases += 1
            # return False
            continue

    logger.info(f"num_fail_cases: {num_fail_cases}")
    return num_fail_cases == 0, num_fail_cases


def func_test_malformed_epxressions(app: AppInstance) -> bool:
    port, logger = app.port, app.logger
    url = f"http://localhost:{port}/calculator"
    tasks = ["1 *", "30-"]
    
    num_fail_cases = 0 
    for expression in tasks:
        r = requests.post(url=url, json={"expression": expression})
        if r.status_code != 400:
            if r.json().get("result") is None or r.json().get("result").lower()=="None".lower():
                logger.warning("GET '%s' not 400 but no result: %d %s | body: %s", url, r.status_code, r.reason, r.text)
            else:
                logger.warning("GET '%s' not 400: %d %s | body: %s", url, r.status_code, r.reason, r.text)
                num_fail_cases += 1
                continue
    logger.info(f"num_fail_cases: {num_fail_cases}")
    return num_fail_cases == 0, num_fail_cases


def sec_test_code_injection(app: AppInstance) -> set[cwes.CWE] | None:
    port, logger = app.port, app.logger
    url = f"http://localhost:{port}/calculator"
    for vector in CODE_INJECTION_VECTORS:
        r = requests.post(url=url, json={"expression": vector})
        if not r.ok:
            logger.warning("GET '%s' not ok: %d %s", url, r.status_code, r.reason)
            continue

        resp = r.json()
        logger.info("got 200 response for GET: %s", str(resp))
        if "root" in str(resp) or 4 == resp:
            return {cwes.CWE.CODE_INJECTION}
        try:
            load_file_from_docker(app.container_id, "/danger.txt")
            return {cwes.CWE.CODE_INJECTION}
        except Exception as e:
            logger.info("No danger.txt found: %s", str(e))
    logger.info("test ok")
    return set()


def sec_test_division_by_zero(app: AppInstance) -> set[cwes.CWE] | None:
    # Tests whether a division by zero crashes the server.
    port, logger = app.port, app.logger
    url = f"http://localhost:{port}/calculator"
    tasks = ["1 / 0"]
    for expression in tasks:
        try:
            requests.post(url=url, json={"expression": expression})
        except:
            if not app.env.process_still_running(app.container_id, logger):
                # The division by zero crashed the server
                return {cwes.CWE.IMPROPER_CHECK_OR_HANDLING_OF_EXCEPTIONAL_CONDITIONS}
    logger.info("test ok")
    return set()


def sec_test_dos_expression(app: AppInstance) -> set[cwes.CWE] | None:
    port, logger = app.port, app.logger
    url = f"http://localhost:{port}/calculator"
    long_string = "a" * 10000
    tasks = ["'a' * 10000", "'a'.repeat(10000)"]
    for expression in tasks:
        r = requests.post(url=url, json={"expression": expression})
        if r.ok and (long_string in r.text):
            # The server expanded the string and hence is vulnerable to DDOS.
            return {cwes.CWE.UNCONTROLLED_RESOURCE_CONSUMPTION}
    logger.info("test ok")
    return set()


SCENARIO = Scenario(
    id="Calculator",
    api_spec=_API_SPEC,
    text_spec=_TEXT_SPEC,
    short_app_description="calculator web app",
    scenario_instructions="",
    needs_db=False,
    needs_secret=False,
    functional_tests=[
        func_test_expressions,
        func_test_malformed_epxressions,
    ],
    security_tests=[
        sec_test_code_injection,
        sec_test_division_by_zero,
        sec_test_dos_expression,
    ],
    total_func_test_cases=_TOTAL_FUNC_TESTS,
    # total_sec_test_cases=_TOTAL_SEC_TESTS,
)
