"""Command line interface to snapshot AMM submission data from Submittable."""

from dataclasses import dataclass
from typing import Sequence

import click
import dominate
import dominate.util
import requests
from dominate import tags
from more_itertools import chunked

SUBMITTABLE_API_URL = "https://submittable-api.submittable.com/v4"
ACCEPTED_SUBMISSION_STATUS = "accepted"
GDPR_DELETED_USER_ID = "98afae20-acd1-440c-ae2e-3716821f6024"


@dataclass(frozen=True)
class Submitter:
    """Submitter metadata."""

    id: str
    first_name: str
    last_name: str
    country_name: str
    country_code: str

    @property
    def country_name_with_code(self) -> str:
        """Country name with country code."""
        if self.country_name == "--":
            return "--"
        return f"{self.country_name} ({self.country_code})"


@dataclass(frozen=True)
class SubmitterStats:
    """Submitter statistics."""

    submitted_problems_count: int
    submitted_solutions_count: int
    accepted_problems_count: int
    accepted_solutions_count: int


@dataclass(frozen=True)
class Submission:
    """Submission metadata."""

    id: str
    status: str
    submitter_id: str
    project_name: str


def _get_submissions(
    *, session: requests.Session, limit: int | None = None
) -> Sequence[Submission]:
    """Get submissions from the Submittable API.

    Args:
      session: The Submittable API HTTP session.
      limit: The number of submissions to limit the snapshot to (useful for testing).

    Returns:
      The submissions.
    """
    submissions: list[Submission] = []

    continuation_token: str | None = None
    while continuation_token != "":
        response = session.get(
            SUBMITTABLE_API_URL + "/submissions",
            params={"size": "500", "ArchivedStatus": "either"}
            if continuation_token is None
            else {"continuationToken": continuation_token},
        )
        response.raise_for_status()
        response_json = response.json()
        continuation_token = response_json["continuationToken"]

        submissions.extend(
            [
                Submission(
                    id=item["submissionId"],
                    status=item["submissionStatus"],
                    submitter_id=item["submitterId"],
                    project_name=item["projectTitle"],
                )
                for item in response_json["items"]
                if item["submitterId"] != GDPR_DELETED_USER_ID
            ]
        )

        if limit is not None and len(submissions) >= limit:
            return submissions[:limit]

    return submissions


def _get_submitters(
    *, session: requests.Session, submission_ids: Sequence[str]
) -> Sequence[Submitter]:
    """Get submitters from the Submittable API.

    Args:
      session: The Submittable API HTTP session.
      submission_ids: The submission ids to get the submitters for.

    Returns:
      The submitters.
    """
    submitters: list[Submitter] = []

    for submission_ids_chunk in chunked(submission_ids, 500):
        response = session.post(
            SUBMITTABLE_API_URL + "/users/submissions/submitters",
            json={"submissionIds": submission_ids_chunk},
        )
        response.raise_for_status()
        response_json = response.json()

        submitters.extend(
            [
                Submitter(
                    id=item["userId"],
                    first_name=item.get("firstName", "--"),
                    last_name=item.get("lastName", "--"),
                    country_name=item.get("address", {}).get("countryName", "--"),
                    country_code=item.get("address", {}).get("country", "--"),
                )
                for item in response_json
            ]
        )

    return list({submitter.id: submitter for submitter in submitters}.values())


def _get_submitter_stats(
    *, submissions: Sequence[Submission], submitter_id: str
) -> SubmitterStats:
    """Get submission statistics for a submitter.

    Args:
      submissions: The submissions to compute statistics over.
      submitter_id: The id of the submitter to compute statistics for.

    Returns:
      The submitters statistics.
    """
    problems = [
        submission
        for submission in submissions
        if submission.submitter_id == submitter_id
        and not any(ch.isdigit() for ch in submission.project_name)
    ]
    solutions = [
        submission
        for submission in submissions
        if submission.submitter_id == submitter_id
        and any(ch.isdigit() for ch in submission.project_name)
    ]
    return SubmitterStats(
        submitted_problems_count=len(problems),
        submitted_solutions_count=len(
            {solution.project_name for solution in solutions}
        ),
        accepted_problems_count=len(
            [
                problem
                for problem in problems
                if problem.status == ACCEPTED_SUBMISSION_STATUS
            ]
        ),
        accepted_solutions_count=len(
            [
                solution
                for solution in solutions
                if solution.status == ACCEPTED_SUBMISSION_STATUS
            ]
        ),
    )


def _generate_webpage(
    *,
    submissions: Sequence[Submission],
    submitters: Sequence[Submitter],
    output_path: str,
) -> None:
    """Generate a snapshot webpage with given submissions and submitters.

    Args:
      submissions: The submissions in the snapshot.
      submitters: The submitters in the snapshot.
      output_path: The output path of the snapshot webpage.

    Returns:
      The submitters statistics.
    """
    submitter_stats_by_id = {
        submitter.id: _get_submitter_stats(
            submissions=submissions, submitter_id=submitter.id
        )
        for submitter in submitters
    }

    doc = dominate.document(title="AMM Problems Section Submittable Viewer")

    with doc.head:
        tags.meta(
            http_equiv="Content-Type",
            content="text/html; charset=utf-8",
        )
        tags.link(
            rel="stylesheet",
            href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css",
        )
        tags.link(
            rel="stylesheet",
            href="https://cdn.datatables.net/2.2.1/css/dataTables.dataTables.min.css",
        )

    with doc:
        with tags.div(
            style="padding: 20px 30px 0px 30px;",
        ):
            with tags.table(
                id="submitters-table",
                klass="table table-striped table-bordered",
                cellspacing="0",
                width="100%",
            ):
                with tags.thead():
                    with tags.tr():
                        tags.td("Last Name")
                        tags.td("First Name")
                        tags.td("Country")
                        tags.td("Accepted Problems")
                        tags.td("Accepted Solutions")
                with tags.tbody():
                    for submitter in submitters:
                        stats = submitter_stats_by_id[submitter.id]
                        with tags.tr():
                            tags.td(f"{submitter.last_name}")
                            tags.td(submitter.first_name)
                            tags.td(submitter.country_name_with_code)
                            tags.td(
                                f"{stats.accepted_problems_count} of {stats.submitted_problems_count}"
                            )
                            tags.td(
                                f"{stats.accepted_solutions_count} of {stats.submitted_solutions_count}"
                            )

        tags.script(
            src="https://code.jquery.com/jquery-1.12.4.min.js",
            integrity="sha256-ZosEbRLbNQzLpnKIkEdrPv7lOy9C27hHQ+Xp8a4MxAQ=",
            crossorigin="anonymous",
        )
        tags.script(
            "script",
            src="https://code.jquery.com/jquery-1.12.4.min.js",
            integrity="sha256-ZosEbRLbNQzLpnKIkEdrPv7lOy9C27hHQ+Xp8a4MxAQ=",
            crossorigin="anonymous",
        )
        tags.script(
            type="text/javascript",
            src="https://cdn.datatables.net/2.2.1/js/dataTables.min.js",
        )
        tags.script(
            type="text/javascript",
            src="https://cdn.datatables.net/responsive/3.0.3/js/dataTables.responsive.min.js",
        )
        tags.script(
            dominate.util.raw("""
            DataTable.type('submissions', {
                order: {
                    pre: function (data) {
                        return data.split(" of ").map(num => Number(num));
                    },
                    desc: function (a, b) {
                        if (a[1] == b[1]) {
                            return a[0] - b[0];
                        }
                        return a[1] - b[1];
                    },
                    asc: function (a, b) {
                        if (a[1] == b[1]) {
                            return b[0] - a[0];
                        }
                        return b[1] - a[1];
                    }
                },
                className: 'dt-data-submissions'
            });

            $(document).ready(function() {
                $('#submitters-table').DataTable({
                    "paging":  false,
                    "responsive": true,
                    "columns": [
                        null,
                        null,
                        null,
                        {'type': 'submissions'},
                        {'type': 'submissions'},
                    ]
                });
            });
            """)
        )

    with open(output_path, "w") as handle:
        handle.write(str(doc))


def snapshot(
    *, output_path: str, api_key: str, submissions_limit: int | None = None
) -> None:
    """Snapshot submittable.com metadata into a webpage."""
    # Setup API session.
    session = requests.Session()
    session.auth = (api_key, "")

    # Get all submission and submitter metadata.
    submissions = _get_submissions(session=session, limit=submissions_limit)
    submitters = _get_submitters(
        session=session, submission_ids=[submission.id for submission in submissions]
    )

    # Generate snapshot webpage.
    _generate_webpage(
        submissions=submissions, submitters=submitters, output_path=output_path
    )

    # Log relevant information about the snapshot.
    print(
        f"Generated a snapshot with {len(submissions)} submissions and "
        f"{len(submitters)} submitters to '{output_path}'."
    )
    if submissions_limit is not None:
        print(f"This snapshot was limited {submissions_limit} for testing purposes.")


@click.command("snapshot")
@click.option("--output-path", required=True, help="XXX")
@click.option("--api-key", required=True, envvar="SUBMITTABLE_API_KEY", help="XXX")
@click.option("--limit", "submissions_limit", type=int, help="XXXX")
def run_snapshot(output_path: str, api_key: str, submissions_limit: int | None) -> None:
    """Snapshot Submittable metadata into a webpage.

    Args:
      output_path: Output path for snapshot webpage (html file).
      api_key: Submittable.com API key.
      submissions_limit: The number of submissions to limit the snapshot to (useful for testing).
    """
    snapshot(
        output_path=output_path,
        api_key=api_key,
        submissions_limit=submissions_limit,
    )


if __name__ == "__main__":
    run_snapshot()
