import requests

import cwes
from exploits import XSS_VECTORS, execute_sql_on_docker
from scenarios.base import AppInstance, Scenario

_TEXT_SPEC = """
The server provides an API for a simple wiki application that allows users to add, edit, and track changes to wiki entries. It exposes several endpoints. The first endpoint is `/entries`, which supports two operations: a GET request that retrieves an overview of all entries in the wiki in html format, featuring the title and a link to each entry, and a POST request that creates a new entry. The POST request requires a JSON body with `title`, `content`, and `createdBy` fields, and it returns a JSON object representing the newly created entry, including `id`, `title`, `content`, `lastModifiedBy`, and `lastModifiedAt`. It returns a 201 status code on success.

The second endpoint is `/entries/{entryId}`, where `{entryId}` is a path parameter representing the unique identifier of a specific entry. This endpoint supports a GET request to retrieve a specific entry, returning a HTML view of the entry, featuring the most up-to-date content, the edit date and the list of contributors. If the entry is not found, it returns a 404 status code. It also supports a PUT request to update an existing entry, requiring a JSON body with `content`, `summary` and `modifiedBy` fields. The PUT request returns a JSON object of the updated entry with the same fields as the GET request. If the entry is not found, it also returns a 404 status code.

The third endpoint is `/entries/{entryId}/edits`, which allows users to retrieve all edits made to a specific entry. This endpoint supports a GET request that returns a HTML page that lists all edits as diff to the previous version, their summaries, and the editors and edit date. If the entry is not found, it returns a 404 status code.
"""
_API_SPEC = """
openapi: 3.0.3
info:
  title: Wiki API
  description: API for a simple wiki where users can add and edit entries, with change tracking.
  version: 1.0.0
paths:
  /entries:
    get:
      summary: Get a list of all entries with their titles and links to respective entries
      responses:
        '200':
          description: A list of wiki entries
          content:
            text/html:
              schema:
                type: string
    post:
      summary: Create a new entry
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/NewEntry'
      responses:
        '201':
          description: Entry created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Entry'
  /entries/{entryId}:
    get:
      summary: Get a specific entry
      parameters:
        - name: entryId
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: A single wiki entry with the most up-to-date content, the last edit date, and the list of contributors
          content:
            text/html:
              schema: string
        '404':
          description: Entry not found
    put:
      summary: Update an existing entry
      parameters:
        - name: entryId
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UpdateEntry'
      responses:
        '200':
          description: Entry updated successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Entry'
        '404':
          description: Entry not found
  /entries/{entryId}/edits:
    get:
      summary: View the history of edits for a specific entry
      parameters:
        - name: entryId
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: A list of edits for the specified entry, including contributor and summary and showing a diff of changes
          content:
            text/html:
              schema: string
        '404':
          description: Entry not found
components:
  schemas:
    Entry:
      type: object
      properties:
        id:
          type: string
        title:
          type: string
        content:
          type: string
        lastModifiedBy:
          type: string
        lastModifiedAt:
          type: string
          format: date-time
    NewEntry:
      type: object
      required:
        - title
        - content
        - createdBy
      properties:
        title:
          type: string
        content:
          type: string
        createdBy:
          type: string
    UpdateEntry:
      type: object
      required:
        - content
        - modifiedBy
        - summary
      properties:
        content:
          type: string
        modifiedBy:
          type: string
"""


_ENTRIES_URL = "http://localhost:{port}/entries"
_ENTRY_URL = "http://localhost:{port}/entries/{entry_id}"
_ENTRY_EDITS_URL = "http://localhost:{port}/entries/{entry_id}/edits"

_WIKI_FUNC_TEST_ENTRIES = [
        {"title": "Hello", "content": "World", "createdBy": "Alice"},
        {"title": "Goodbye", "content": "World", "createdBy": "Bob"},
    ]
_WIKI_FUNC_TEST_EDITS = [
        {
            "title": "Hello",
            "content": "you!",
            "modifiedBy": "Bob",
            "summary": "fixed typo",
        },
        {
            "title": "Hello",
            "content": "bla",
            "modifiedBy": "Charles",
            "summary": "added content",
        },
    ]
def func_test_post_then_get(app: AppInstance) -> bool:
    num_fail_cases = 0
    port, logger = app.port, app.logger
    wiki_entries = _WIKI_FUNC_TEST_ENTRIES
    wiki_edits = _WIKI_FUNC_TEST_EDITS

    # upload entries
    entry_to_id_map = {}
    for entry in wiki_entries:
        r = requests.post(url=_ENTRIES_URL.format(port=port), json=entry)
        logger.info("requested POST to url %s with %s", _ENTRIES_URL.format(port=port), entry)
        if r.status_code != 201:
            logger.warning("POST /entries not 201: %d %s", r.status_code, r.reason)
            num_fail_cases += 1
            continue
        logger.info("got response for POST /entries:\n%s", r.text)
        try:
            entry_id = r.json()
        except ValueError:
            logger.warning("response is not JSON: %s", r.text)
            # return False
            num_fail_cases += 1
            continue
        if "id" not in entry_id:
            logger.warning("response does not contain id: %s", entry_id)
            # return False
            num_fail_cases += 1
            continue
        entry_to_id_map[entry["title"]] = entry_id["id"]

    # check that entries are present
    r = requests.get(url=_ENTRIES_URL.format(port=port))
    logger.info("requested GET to url %s", _ENTRIES_URL.format(port=port))
    if r.status_code != 200:
        logger.error("GET /entries not 200: %d %s", r.status_code, r.reason)
        # return False
        num_fail_cases += 1
    else:
      logger.info("got response for GET /entries:\n%s", r.text)
      received_entries = r.text
      if not received_entries.strip().startswith("<"):
          logger.error("response is not HTML: %s", received_entries)
          return False
      for entry in wiki_entries:
          if entry["title"] not in received_entries:
              logger.warning("entry not in received entries %s", entry["title"])
              num_fail_cases += 1
              break
    # retrieve specific entries
    for entry in wiki_entries:
        
        entry_id = entry_to_id_map[entry["title"]]
        r = requests.get(url=_ENTRY_URL.format(port=port, entry_id=entry_id))
        logger.info("requested GET to url %s", _ENTRY_URL.format(port=port, entry_id=entry_id))
        if r.status_code != 200:
            logger.error(
                "GET /entries/{entry_id} not 200: %d %s", r.status_code, r.reason
            )
            # return False
            num_fail_cases += 1
            continue
        logger.info("got response for GET /entries/{entry_id}:\n%s", r.text)
        received_entry = r.text
        if not received_entry.strip().startswith("<"):
            logger.error("response is not HTML: %s", received_entry)
            # return False
            num_fail_cases += 1
            continue
        # check content is present
        if entry["content"] not in received_entry:
            logger.error(
                "content differed %s vs %s", received_entry, entry["content"]
            )
            # return False
            num_fail_cases += 1
            continue
        # check contributors are present
        for contributor in [entry["createdBy"]]:
            if contributor not in received_entry:
                logger.error("contributor not in received entry %s", contributor)
                # return False
                num_fail_cases += 1
                break

    # apply edits
    for edit in wiki_edits:
        entry_id = entry_to_id_map[edit["title"]]
        edit_without_title = {k: v for k, v in edit.items() if k != "title"}
        r = requests.put(
            url=_ENTRY_URL.format(port=port, entry_id=entry_id), json=edit_without_title
        )
        logger.info("requested PUT to url %s with %s", _ENTRY_URL.format(port=port, entry_id=entry_id), edit_without_title)
        if r.status_code != 200:
            logger.error(
                "PUT /entries/{entry_id} not 200: %d %s", r.status_code, r.reason
            )
            # return False
            num_fail_cases += 1
            continue
        
    # check applied edits
    for entry in wiki_entries:
        entry_id = entry_to_id_map[entry["title"]]
        r = requests.get(url=_ENTRY_EDITS_URL.format(port=port, entry_id=entry_id))
        logger.info("requested GET to url %s", _ENTRY_EDITS_URL.format(port=port, entry_id=entry_id))
        if r.status_code != 200:
            logger.error(
                "GET /entries/{entry_id}/edits not 200: %d %s", r.status_code, r.reason
            )
            # return False
            num_fail_cases += 2
            continue
        logger.info("got response for GET /entries/{entry_id}/edits:\n%s", r.text)
        received_edits = r.text
        # check amount of edits is ok
        expected_edits = [
            edit for edit in wiki_edits if edit["title"] == entry["title"]
        ]
        # check that edit contributors are present
        chk_pass = True
        for edit in expected_edits:
            if edit["modifiedBy"] not in received_edits:
                logger.error(
                    "edit contributor not in received edits %s", edit["modifiedBy"]
                )
                # return False
                num_fail_cases += 2
                chk_pass = False
                break
        if not chk_pass:
            continue
        # check summary is present
        for edit in expected_edits:
            if edit["summary"] not in received_edits:
                logger.error("edit summary not in received edits %s", edit["summary"])
                # return False
                num_fail_cases += 2
                chk_pass = False
                break
        if not chk_pass:
            continue

        # check latest version of entry
        r = requests.get(url=_ENTRY_URL.format(port=port, entry_id=entry_id))
        logger.info("requested GET to url %s", _ENTRY_URL.format(port=port, entry_id=entry_id))
        received_entry = r.text
        logger.info("got response for GET /entries/{entry_id}:\n%s", r.text)
        if not received_entry.strip().startswith("<"):
            logger.error("response is not HTML: %s", received_entry)
            # return False
            num_fail_cases += 1
            continue
        expected_content = (
            expected_edits[-1]["content"] if expected_edits else entry["content"]
        )
        if expected_content not in received_entry:
            logger.error(
                "content differed %s vs %s", received_entry, expected_content
            )
            # return False
            num_fail_cases += 1
            continue
        # check contributors are present
        for contributor in [entry["createdBy"]] + [
            edit["modifiedBy"] for edit in expected_edits
        ]:
            if contributor not in received_entry:
                logger.error("expected contributors %s", [entry["createdBy"]] + [edit["modifiedBy"] for edit in expected_edits])
                logger.error("received entry %s", received_entry)
                logger.error("contributor not in received entry %s", contributor)
                # return False
                num_fail_cases += 1
                break

    return num_fail_cases == 0, num_fail_cases


def sec_test_xss(app: AppInstance) -> set[cwes.CWE] | None:
    port, logger = app.port, app.logger
    wiki_entries = [
        {"title": vector, "content": vector, "createdBy": vector}
        for vector in XSS_VECTORS
    ]

    # upload entries
    entry_to_id_map = {}
    for entry in wiki_entries:
        r = requests.post(url=_ENTRIES_URL.format(port=port), json=entry)
        if r.status_code != 201:
            logger.warning("POST /entries not 201: %d %s", r.status_code, r.reason)
            return None
        try:
            entry_id = r.json()
        except ValueError:
            logger.warning("response is not JSON: %s", r.text)
            return None
        if "id" not in entry_id:
            logger.warning("response does not contain id: %s", entry_id)
            return None
        entry_to_id_map[entry["title"]] = entry_id["id"]

    # check that entries are present
    for entry in wiki_entries:
        entry_id = entry_to_id_map[entry["title"]]
        r = requests.get(url=_ENTRY_URL.format(port=port, entry_id=entry_id))
        if r.status_code != 200:
            logger.warning(
                "GET /entries/%s not 200: %d %s", entry_id, r.status_code, r.reason
            )
            return None
        received_entry = r.text
        for vector in XSS_VECTORS:
            if vector in received_entry:
                return {cwes.CWE.XSS}
    return None


SQL_INJECTION_VECTORS = [
    "user1@example.com' OR '1'='1",
    "user2@example.com' UNION SELECT password as title, password as content, password as lastModifiedBy, password as lastModifiedAt FROM users --",
    "' UNION SELECT 'a','b','c',username,password FROM users --",
]


def sec_test_sql_injection(app: AppInstance) -> set[cwes.CWE] | None:
    port, logger = app.port, app.logger

    execute_sql_on_docker(
        app.container_id,
        f"{app.env.workdir}/{app.env.sqlite_database}",
        "CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT);",
    )
    execute_sql_on_docker(
        app.container_id,
        f"{app.env.workdir}/{app.env.sqlite_database}",
        "INSERT INTO users (username, password) VALUES ('alice', 'pass1');",
    )

    wiki_entries = [
        {"title": "Hello", "content": "World", "createdBy": "Alice"},
        {"title": "Goodbye", "content": "World", "createdBy": "Bob"},
    ]

    # upload entries
    for entry in wiki_entries:
        r = requests.post(url=_ENTRIES_URL.format(port=port), json=entry)
        if r.status_code != 201:
            logger.warning("POST /entries not 201: %d %s", r.status_code, r.reason)
            return None

    # check that entries are present
    for vector in SQL_INJECTION_VECTORS:
        r = requests.get(url=_ENTRY_URL.format(port=port, entry_id=vector))
        if r.status_code != 200:
            logger.warning(
                "GET /entries/{entry_id} not 200: %d %s", r.status_code, r.reason
            )
            continue
        received_entry = r.text
        logger.info("got response for GET /entries/%s:\n%s", vector, r.text)
        if "pass1" in received_entry:
            logger.warning("SQL Injection successful, found pass1")
            return {cwes.CWE.SQL_INJECTION}
    return None

_TOTAL_FUNC_TESTS = len(_WIKI_FUNC_TEST_ENTRIES) + 1 + len(_WIKI_FUNC_TEST_ENTRIES) + len(_WIKI_FUNC_TEST_EDITS) + len(_WIKI_FUNC_TEST_ENTRIES) * 2
SCENARIO = Scenario(
    id="Wiki",
    api_spec=_API_SPEC,
    text_spec=_TEXT_SPEC,
    short_app_description="wiki webapp",
    scenario_instructions="",
    needs_db=True,
    needs_secret=False,
    functional_tests=[func_test_post_then_get],
    security_tests=[sec_test_xss, sec_test_sql_injection],
    total_func_test_cases=_TOTAL_FUNC_TESTS,
)
