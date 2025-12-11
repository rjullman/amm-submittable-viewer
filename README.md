# AMM Problems Section Submittable.com Data Viewer

A dashboard for viewing submissions on Submittable.com made for the American
Mathematical Monthly (AMM) Problems Section.  

This was hacked together quickly as a favor for the head of the AMM Problems
Section Review Committee. This is hosted as a resource for him and others on
the committee.

## Building the Dashboard

1. If needed [install uv](https://docs.astral.sh/uv/getting-started/installation/).

2. Generate the dashboard:

```
export SUBMITTABLE_API_KEY="<your-api-key>"
uv run snapshot.py --output-path ./build/index.html
```

You can use the `--limit` option (e.g. `--limit 10`) to limit the number of
submissions requested from Submittable.com . This can be useful for making the
snapshot faster for testing purposes.

Additionally you can add the `--serve` flag to serve the snapshot with a
webserver. This option has the following associated options:
  - `--serve-host <hostname>`: the webserver host name,
  - `--serve-port <port>`: the webserver port,
  - `--serve-auth <username>:<password>`: colon separated username/password for basic auth (or use envvar `SNAPSHOT_SERVER_AUTH`), and
  - `--serve-refresh-every <time-in-seconds>`: to regenerated the snapshot every given number of seconds.
Note that this command currently starts a Flask development server and not a
UWSGI server. As such, this should not be used as a production webserver.
