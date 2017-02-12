from collections import namedtuple
from html import HTML
import os
import requests
from requests.auth import HTTPBasicAuth

SUBMITTABLE_API_KEY = os.getenv("SUBMITTABLE_API_KEY")
SUBMITTABLE_API_URL = 'https://api.submittable.com/v1'

Submitter = namedtuple('Submitter', ['first_name', 'last_name', 'email', 'submissions', 'country'], rename = True)

def load_submissions(user_email):
    ret = []
    page = 1
    while True:
        data = requests.get(SUBMITTABLE_API_URL + '/submissions?count=100&search=' + user_email,
                            auth = HTTPBasicAuth(SUBMITTABLE_API_KEY, '')).json()
        for item in data['items']:
            if user_email == item['submitter']['email']:
                numbers_in_name = [int(s) for s in item['category']['name'].split() if s.isdigit()]
                if len(numbers_in_name) == 1:
                    ret.append(str(numbers_in_name[0]))
        if page == data['total_pages']:
            ret.sort()
            return ret
        page += 1

def load_submitters():
    ret = []
    page = 1
    while True:
        data = requests.get(SUBMITTABLE_API_URL + '/submitters?page=' + str(page),
                            auth = HTTPBasicAuth(SUBMITTABLE_API_KEY, '')).json()
        submitters = map(
            lambda item: Submitter(
                first_name=item['first_name'],
                last_name=item['last_name'],
                email=item['email'],
                submissions=load_submissions(item['email']),
                country=item['country']),
            data['items'])
        ret.extend(submitters)
        if page == data['total_pages']:
            return ret
        page += 1

def format_field_as_str(field):
    if not field:
        return "--"
    if isinstance(field, (list, tuple)):
        arr_field = map(lambda sub_field: format_field_as_str(sub_field), field)
        return str(len(field)) + "\t(" + ", ".join(arr_field) + ")"
    return field.encode('utf-8')

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
    body.script("""
                $(document).ready(function() {
                    $('#submitters-table').DataTable();
                });
                """)
    return html

print(generate_html_str(load_submitters()))
