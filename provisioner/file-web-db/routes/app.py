from flask import Flask, request, json, Response, render_template, flash, redirect, jsonify, url_for
from pymongo import errors, MongoClient

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError

from werkzeug.datastructures import ImmutableMultiDict

from flask_table import Table, Col, LinkCol

import logging
import file_handler
import yaml, pathlib
from IPy import IP

LOG = logging.getLogger(__name__)
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ezpz'

ENV_FILE = pathlib.Path("/usr/share/flask/file_web_db.yml")

with open(ENV_FILE, "r") as yaml_data:
    ENV_DATA = yaml.load(yaml_data, Loader=yaml.FullLoader)
    HOST_IP = str(ENV_DATA['HOST_IP'])

nav = [
    {'name': 'Home', 'url': f'http://{HOST_IP}:5000/home'},
    {'name': 'Upload/Delete', 'url': f'http://{HOST_IP}:5000/upload'},
    {'name': 'Search', 'url': f'http://{HOST_IP}:5000/search'},
]

class Results(Table):
    id = Col('BranchId', show=False)
    edit = LinkCol(
        name='Edit',
        endpoint='update',
        url_kwargs=dict(id='routerName'),
    )
    Delete = LinkCol(
        name='Delete',
        endpoint='delete',
        url_kwargs=dict(id='routerName'),
    )
    routerName = Col('routerName')
    customer_pciAddress = Col('customer_pciAddress')
    customer_tenant = Col('customer_tenant')
    dns_servers = Col('dns_servers')
    entitlement_end_date = Col('entitlement_end_date')
    entitlement_mbs = Col('entitlement_mbs')
    interNodeSecurity = Col('interNodeSecurity')
    interRouterSecurity = Col('interRouterSecurity')
    location = Col('location')
    locationCoordinates = Col('locationCoordinates')
    management_loopback = Col('management_loopback')
    management_service_security = Col('management_service_security')
    management_tenant = Col('management_tenant')
    neighborhood_name = Col('neighborhood_name')
    ntp_servers = Col('ntp_servers')
    provider_gateway = Col('provider_gateway')
    provider_ipAddress = Col('provider_ipAddress')
    provider_pciAddress = Col('provider_pciAddress')
    provider_prefixLength = Col('provider_prefixLength')
    provider_tenant = Col('provider_tenant')


class SearchForm(FlaskForm):
    search = StringField('Branch ID')
    submit = SubmitField('search')


class DataForm(FlaskForm):
    """
        From for DB entry
    """
    # storeNumber = StringField('storeNumber', validators=[DataRequired()])
    # storeId = StringField('storeId', validators=[DataRequired()])
    # name = StringField('name', validators=[DataRequired()])
    # location = StringField('location', validators=[DataRequired()])
    # data = { "storeNumber": storeNumber, "name": name, "storeId": storeId, "location": location }
    # submit = SubmitField('Upload Data')


    routerName = StringField('routerName', validators=[DataRequired()])
    customer_pciAddress = StringField('customer_pciAddress', validators=[DataRequired()])
    customer_tenant = StringField('customer_tenant', validators=[DataRequired()])
    dns_servers = StringField('dns_servers', validators=[DataRequired()])
    entitlement_end_date = StringField('entitlement_end_date', validators=[DataRequired()])
    entitlement_mbs = StringField('entitlement_mbs', validators=[DataRequired()])
    interNodeSecurity = StringField('interNodeSecurity', validators=[DataRequired()])
    interRouterSecurity = StringField('interRouterSecurity', validators=[DataRequired()])
    location = StringField('location', validators=[DataRequired()])
    locationCoordinates = StringField('locationCoordinates', validators=[DataRequired()])
    management_loopback = StringField('management_loopback', validators=[DataRequired()])
    management_service_security = StringField('management_service_security', validators=[DataRequired()])
    management_tenant = StringField('management_tenant', validators=[DataRequired()])
    neighborhood_name = StringField('neighborhood_name', validators=[DataRequired()])
    ntp_servers = StringField('ntp_servers', validators=[DataRequired()])
    provider_gateway = StringField('provider_gateway', validators=[DataRequired()])
    provider_ipAddress = StringField('provider_ipAddress', validators=[DataRequired()])
    provider_pciAddress = StringField('provider_pciAddress', validators=[DataRequired()])
    provider_prefixLength = StringField('provider_prefixLength', validators=[DataRequired()])
    provider_tenant = StringField('provider_tenant', validators=[DataRequired()])
    data = { "routerName": routerName, "customer_pciAddress": customer_pciAddress, "customer_tenant": customer_tenant,
             "dns_servers": dns_servers, "entitlement_end_date": entitlement_end_date, "entitlement_mbs": entitlement_mbs,
             "interNodeSecurity": interNodeSecurity, "interRouterSecurity": interRouterSecurity, "location": location,
             "locationCoordinates": locationCoordinates, "management_loopback": management_loopback,
             "management_service_security": management_service_security, "management_tenant": management_tenant,
             "neighborhood_name": neighborhood_name, "ntp_servers": ntp_servers, "provider_gateway": provider_gateway,
             "provider_gateway": provider_gateway, "provider_pciAddress": provider_pciAddress,
             "provider_prefixLength": provider_prefixLength, "provider_tenant": provider_tenant}
    submit = SubmitField('Upload Data')

    def validate_dns_servers(form, field):
        ip_list = field.data.split(',')
        for address in ip_list:
            try:
                IP(address)
            except:
                raise ValidationError("Invalid IP list")

    def validate_ntp_servers(form, field):
        ip_list = field.data.split(',')
        for address in ip_list:
            try:
                IP(address)
            except:
                raise ValidationError("Invalid IP")


@app.route("/home")
def home():
    """Landing page."""
    return render_template(
        'home.html',
        nav=nav,
        title="Local Database UI",
        description="Web interface for interacting with the Database."
    )

@app.route("/search", methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if request.method == 'POST':
        return search_results(form)
    return render_template('search_new.html', nav=nav, form=form)

@app.route('/results')
def search_results(search):
    results = []
    # print(f"=============>Search data: {search.data}")
    branch = search.data['search']
    print(f"=============>Search data: {branch}, {type(branch)}")
    if branch == '':
        results = file_handler.get_all()
        print(results)
    else:
        print(f"=============>Search data: {results}, {type(results)}")
        results = [file_handler.get_store_data(branch)['variables']]
        print(f"=============>Search data: {results}, {type(results)}")
    if not results:
        flash('No results found!')
        return redirect('/search')
    table = Results(results)
    table.border = True
    return render_template('results.html', nav=nav, table=table)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    remove_list = ["csrf_token", "submit"]
    form = DataForm()
    if form.validate_on_submit():
        data = {}
        data['variables'] = request.form.to_dict()
        data['name'] = data['variables']['routerName']
        data['variables']['dns_servers'] = data['variables']['dns_servers'].strip()
        data['variables']['dns_servers'] = data['variables']['dns_servers'].split(",")
        data['variables']['ntp_servers'] = data['variables']['ntp_servers'].strip()
        data['variables']['ntp_servers'] = data['variables']['ntp_servers'].split(",")
        print("Form to JSON: {}".format(data))
        try:
            [data['variables'].pop(key) for key in remove_list]
        except:
            print(f"Error reading form {data}")
        else:
            # flash('Attempting to upload data for storeNumber {} with data \n {}'.format(
            #     form.routerName.data, data))
            response = file_handler.write_json_to_yml(data)
            if response:
                return Response(response=json.dumps(data),
                            status=200,
                            mimetype='application/json')
    # return render_template('base.html', title='Upload Data')
    # redirect('/api/v1/stores/all')
    return render_template('form_new.html',
        nav=nav,
        # title='Upload Data',
        # description="Form to upload branch data.",
        form=form,
        template="form-template"
        )


@app.route('/')
def base():
    return Response(response=json.dumps({"Status": "UP"}),
                    status=200,
                    mimetype='application/json')

@app.route('/list', methods=['GET'])
def list_all():
    file_list = file_handler.list_files()
    print(file_list)
    # file_handler.convert_json_to_yaml(file_list['list'][0])
    return(file_list)

"""
http://localhost:5000/api/v1/stores?id=base
"""
@app.route('/api/v1/stores', methods=['GET'])
def query_by_storenumber():
    if 'id' in request.args:
        branch_file = str(request.args['id']) + '.yml'
        print(branch_file)
        file_list = list_all()
        print(file_list)
        if branch_file in file_list['list']:
            branch_data = file_handler.convert_yaml_to_json(branch_file)
            return(branch_data)
            return Response(response=branch_data,
                            status=200,
                            mimetype='application/json')
    return page_not_found(404)


"""
curl --header "Content-Type: application/json" --request POST --data \
'{ "variables": {"routerName": "01225", "storeId": "RIST05868P01", "location": "Burlington, MA"}, "name": "Instance_1"}' \
http://localhost:5000/add
"""
@app.route('/api/v1/stores', methods=['POST'])
def insert_data():
    data = request.get_json()
    print(data)
    if data is None or data == {}:
        return Response(response=json.dumps({"Error": "Invalid Input"}),
                        status=400,
                        mimetype='application/json')
    if file_handler.write_json_to_yml(data):
        return Response(response=json.dumps({"Success": "DB entry created"}),
                        status=200,
                        mimetype='application/json')
    else:
        return Response(response=json.dumps({"Error": "unable to write to file"}),
                        status=400,
                        mimetype='application/json')


@app.route('/update/<id>', methods=['GET', 'POST'])
def update(id):
    branch_data = file_handler.get_store_data(id)['variables']
    if branch_data is None or branch_data == {}:
        return Response(response=json.dumps({"Error": "Invalid Input"}),
                        status=400,
                        mimetype='application/json')
    if branch_data:
        print(f"====================>{id}, {request}, {branch_data}")
        branch_data['dns_servers'] = ",".join(branch_data['dns_servers'])
        branch_data['ntp_servers'] = ",".join(branch_data['ntp_servers'])
        form = DataForm(data=branch_data)
        if request.method == 'POST' and form.validate_on_submit():
            file_handler.update_file(branch_data)
        return render_template('form_new.html',
            nav=nav,
            form=form,
            template="form-template"
            )
    else:
        return Response(response=json.dumps({"Error": "unable to update data"}),
                        status=400,
                        mimetype='application/json')


"""
curl -H "Accept: application/json" --request DELETE http://localhost:5000/delete\?id=01225
curl -X "DELETE" http://localhost:5000/delete?id=01225
"""
@app.route('/api/v1/stores', methods=['DELETE'])
def delete_data():
    if 'id' in request.args:
        id = str(request.args['id'])
        file_handler.delete_file(id)
        return Response(response=json.dumps({"Success": "DB entry removed"}),
                        status=200,
                        mimetype='application/json')
    return page_not_found(404)

@app.route('/delete/<id>', methods=['GET', 'POST'])
def delete(id):
    try:
        file_handler.delete_file(id)
        return Response(response=json.dumps({"Success": "DB entry removed"}),
                        status=200,
                        mimetype='application/json')
    except:
        return page_not_found(404)


@app.errorhandler(404)
def page_not_found(error):
    return "The resource could not be found.", 404



if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
