from collections import namedtuple
from html import HTML
import os
import requests
from requests.auth import HTTPBasicAuth

SUBMITTABLE_API_KEY = os.getenv("SUBMITTABLE_API_KEY")
SUBMITTABLE_API_URL = 'https://api.submittable.com/v1'

Submitter = namedtuple('Submitter',
                       ['last_name', 'first_name', 'email', 'submissions', 'submission_count', 'country'],
                       rename = True)

def load_submitters():
    submitters = {}
    page = 1
    while True:
        data = requests.get(SUBMITTABLE_API_URL + '/submissions?count=500&page=' + str(page),
                            auth = HTTPBasicAuth(SUBMITTABLE_API_KEY, '')).json()
        for item in data['items']:
            submitter_info = item['submitter']
            numbers_in_name = [int(s) for s in item['category']['name'].split() if s.isdigit()]
            if submitter_info['email'] not in submitters:
                submitters[submitter_info['email']] = Submitter(
                    first_name=submitter_info['first_name'],
                    last_name=submitter_info['last_name'],
                    email=submitter_info['email'],
                    submissions=[],
                    submission_count=0,
                    country=submitter_info['country'])

            if len(numbers_in_name) == 1:
                submission = numbers_in_name[0]
                submitters[submitter_info['email']].submissions.append(submission)
                new_count = submitters[submitter_info['email']].submission_count + 1
                submitters[submitter_info['email']] = submitters[submitter_info['email']]._replace(submission_count=new_count)

        if page == data['total_pages']:
            ret = list(submitters.values())
            for submitter in ret:
                submitter.submissions.sort()
            return ret

        page += 1

def format_field_as_str(field):
    if field == None:
        return ""
    if isinstance(field, (list, set, tuple)):
        arr_field = map(lambda sub_field: format_field_as_str(sub_field), field)
        return ", ".join(arr_field)
    if isinstance(field, unicode):
        return field.encode("utf-8")
    return str(field)

def generate_html_str(submitters):
    html = HTML('html') 

    head = html.head()
    head.link(rel="stylesheet", href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css")
    head.link(rel="stylesheet", href="https://cdn.datatables.net/1.10.13/css/jquery.dataTables.min.css")

    body = html.body(style="padding: 20px 30px 0px 30px;")
    table = body.table(id="submitters-table", klass="table table-striped table-bordered", cellspacing="0", width="100%")

    thead = table.thead()
    thead_tr = table.tr()
    map(lambda field: thead_tr.td(field.replace("_", " ").title()), Submitter._fields)

    tbody = table.tbody()
    for submitter in submitters:
        tr = tbody.tr()
        map(lambda field: tr.td(format_field_as_str(submitter._asdict()[field])), Submitter._fields)

    body.script("",
                src="https://code.jquery.com/jquery-1.12.4.min.js",
                integrity="sha256-ZosEbRLbNQzLpnKIkEdrPv7lOy9C27hHQ+Xp8a4MxAQ=",
                crossorigin="anonymous")
    body.script("",
                type="text/javascript", src="https://cdn.datatables.net/1.10.13/js/jquery.dataTables.min.js")

    column_types = ", ".join(
        map(lambda field:
            "{ 'type': 'num' }"
            if format_field_as_str(submitters[0]._asdict()[field]).isdigit()
            else "{ 'type': 'html' }",
            Submitter._fields))
    body.script("""
                $(document).ready(function() {
                    $('#submitters-table').DataTable({
                        "columns": [
                """
                + column_types +
                """
                        ]
                    });
                });
                """)
    return html

print(generate_html_str(load_submitters()))
