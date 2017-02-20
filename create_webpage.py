from collections import namedtuple
from html import HTML
import os
import requests
from requests.auth import HTTPBasicAuth

SUBMITTABLE_API_KEY = os.getenv("SUBMITTABLE_API_KEY")
SUBMITTABLE_API_URL = 'https://api.submittable.com/v1'

class StringType:
    def format(self, value):
        if isinstance(value, unicode):
            return value.encode("utf-8")
        return str(value)

class NumberType:
    def format(self, value):
        return str(value)

class ArrayType:
    def __init__(self, value_type):
        self.value_type = value_type

    def format(self, value):
        return ", ".join(map(lambda arr_value: self.value_type.format(arr_value), value))

class ColumnMetadata:
    def __init__(self, field, name, type, data_table_config_str="null"):
        self.field = field;
        self.name = name;
        self.type = type;
        self.data_table_config_str = data_table_config_str

    def format(self, value):
        return self.type.format(value)

columns = [
    ColumnMetadata("last_name",        "Last Name",     StringType()),
    ColumnMetadata("first_name",       "First Name",    StringType()),
    ColumnMetadata("email",            "Email",         StringType()),
    ColumnMetadata("solutions",        "Submissions",   ArrayType(StringType())),
    ColumnMetadata("solution_count",   "# Solutions",   NumberType(), "{ 'type' : 'num' }"),
    ColumnMetadata("proposals",        "# Proposals",   NumberType(), "{ 'type' : 'num' }"),
    ColumnMetadata("country",          "Country",       StringType()),
]

Submitter = namedtuple('Submitter', map(lambda column: column.field, columns))

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
                    solutions=[],
                    solution_count=0,
                    proposals=0,
                    country=submitter_info['country'])

            submitter = submitters[submitter_info['email']]
            if len(numbers_in_name) == 1:
                solution = numbers_in_name[0]
                submitter.solutions.append(solution)
                submitters[submitter_info['email']] = submitter._replace(solution_count=submitter.solution_count + 1)
            else:
                submitters[submitter_info['email']] = submitter._replace(proposals=submitter.proposals + 1)

        if page == data['total_pages']:
            ret = list(submitters.values())
            for submitter in ret:
                submitter.solutions.sort()
            return ret

        page += 1

def generate_html_str(columns, submitters):
    html = HTML('html') 

    head = html.head()
    head.link(rel="stylesheet", href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css")
    head.link(rel="stylesheet", href="https://cdn.datatables.net/1.10.13/css/jquery.dataTables.min.css")

    body = html.body(style="padding: 20px 30px 0px 30px;")
    table = body.table(id="submitters-table", klass="table table-striped table-bordered", cellspacing="0", width="100%")

    thead = table.thead()
    thead_tr = table.tr()
    map(lambda column: thead_tr.td(column.name), columns)

    tbody = table.tbody()
    for submitter in submitters:
        tr = tbody.tr()
        map(lambda column: tr.td(column.format(submitter._asdict()[column.field])), columns)

    body.script("",
                src="https://code.jquery.com/jquery-1.12.4.min.js",
                integrity="sha256-ZosEbRLbNQzLpnKIkEdrPv7lOy9C27hHQ+Xp8a4MxAQ=",
                crossorigin="anonymous")
    body.script("",
                type="text/javascript", src="https://cdn.datatables.net/1.10.13/js/jquery.dataTables.min.js")

    data_table_config = ", ".join(map(lambda column: column.data_table_config_str, columns))
    body.script("""
                $(document).ready(function() {
                    $('#submitters-table').DataTable({
                        "columns": [
                """
                + data_table_config +
                """
                        ]
                    });
                });
                """)
    return html

print(generate_html_str(columns, load_submitters()))
