# AMM Problems Section Submittable.com Data Viewer
A dashboard for viewing submissions on Submittable.com made for the American Mathematical Monthly (AMM) Problems Section.  

This was hacked together quickly as a favor for the head of the AMM Problems Section Review Committee.
This is hosted as a resource for him and others on the committee.

## Building the Dashboard

1. Setup a Python development environment.  
    1. Make sure you have `python` and `pip` installed (I'd recommend installing `virtualenv` too).
    2. Install this project's dependencies with `pip` using `pip install -r requirements.txt`.
2. Setup your system shell environment (e.g. `export <VAR_NAME>=<VAR_VALUE>`).
    - Set `SUBMITTABLE_API_KEY` to be your Submittable.com API Key.
    - Set `LOGIN_USERNAME` and `LOGIN_PASSWORD` to be the username and password combination required to login to the generated dashboard.
    - (Optional) Set `PORT` to be the port on which the dashboard will be hosted.
3. Run `./scripts/deploy.sh` to generate and serve the dashboard on http://localhost:5000/ (or on the port specified by the `PORT` environment variable if it is set). 
