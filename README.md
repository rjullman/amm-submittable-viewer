# AMM Problems Section Submittable.com Data Viewer

A dashboard for viewing submissions on Submittable.com made for the American
Mathematical Monthly (AMM) Problems Section.  

This was hacked together quickly as a favor for the head of the AMM Problems
Section Review Committee. This is hosted as a resource for him and others on
the committee.

## Building the Dashboard

1. Setup the Python environment:
```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

2. Generate the dashboard:

```
export SUBMITTABLE_API_KEY="<your-api-key>"
uv run snapshot.py --output-path ./build/index.html
```

You can use the `--limit` option (e.g. `--limit 10`) to limit the number of
submissions requested from Submittable.com . This can be useful for making the
snapshot faster for testing purposes.
