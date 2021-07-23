from flask import Flask, request, json, Response, render_template, flash, redirect, jsonify, url_for
from pymongo import errors, MongoClient

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

from werkzeug.datastructures import ImmutableMultiDict

from flask_table import Table, Col

import logging as log

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ezpz'

class MongoAPI:
    def __init__(self, data=None):
        log.basicConfig(level=log.DEBUG, format='%(asctime)s %(levelname)s:\n%(message)s\n')
        # self.client = MongoClient("mongodb://db:27017/") ## Prod
        self.client = MongoClient("mongodb://localhost:27017/")

        db = 'LocalDB'
        col = 'Branch'
        provdb = self.client[db]
        self.collection = provdb[col]
        self.data = data
        self.collection.create_index("storeNumber", unique = True)

    def read_all(self):
        log.info('Reading All Data')
        documents = self.collection.find()
        output = [{item: data[item] for item in data if item != '_id'} for data in documents]
        return output

    def query_by_storenumber(self):
        log.info('Querying by storeNumber')
        documents = self.collection.find(self.data)
        output = [{item: data[item] for item in data if item != '_id'} for data in documents]
        return output

    def write(self):
        log.info('Writing Data')
        try:
            response = self.collection.insert_one(self.data)
            output = {'Status': 'Successfully Inserted',
                  'Document_ID': str(response.inserted_id)}
        except errors.DuplicateKeyError:
            log.info('Duplicate key error')
            output = {'Status': 'Duplicate key error'}
        return output

    def delete_one(self):
        log.info('Deleting Data')
        response = self.collection.delete_one(self.data)
        output = {'Status': 'Successfully Deleted' if response.deleted_count > 0 else "Document not found."}
        return output


store_data_1 = { "storeNumber": "01225", "storeId": "MAST01225P01" }
store_data_2 = { "storeNumber": "16743", "name": "128t-east", "storeId": "RIST16743P01", "location": "Burlington, MA" }

read_data = { "storeNumber": "16743" }

def write_test():
    repsonse = MongoAPI(store_data_2).write()
    # response = obj1.write(store_data)

def read_test():
    obj1 = MongoAPI()
    response = obj1.read_all()
    print(json.dumps(response))

def query_by_storenumber():
    obj1 = MongoAPI(read_data)
    response = obj1.query_by_storenumber()
    print(json.dumps(response))

def delete_one():
    obj1 = MongoAPI(read_data)
    obj1.delete_one()


read_test()
write_test()
# # delete_one()
read_test()

query_by_storenumber()


nav = [
    {'name': 'Home', 'url': 'http://localhost:5001/home'},
    {'name': 'Upload/Delete', 'url': 'http://localhost:5001/upload'},
    {'name': 'Search', 'url': 'http://localhost:5001/search'},
]

class Results(Table):
    id = Col('Id', show=False)
    storeNumber = Col('storeNumber')
    storeId = Col('storeId')
    name = Col('name')
    location = Col('location')


class SearchForm(FlaskForm):
    search = StringField('Branch ID')
    submit = SubmitField('search')


class DataForm(FlaskForm):
    """
        From for DB entry
    """
    storeNumber = StringField('storeNumber', validators=[DataRequired()])
    storeId = StringField('storeId', validators=[DataRequired()])
    name = StringField('name', validators=[DataRequired()])
    location = StringField('location', validators=[DataRequired()])
    data = { "storeNumber": storeNumber, "name": name, "storeId": storeId, "location": location }
    submit = SubmitField('Upload Data')


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
    input = search.data['search']
    print(f"=============>Search data: {input}, {type(input)}")
    if input == '':
        results = MongoAPI().read_all()
    else:
        data = { "storeNumber": input }
        results = MongoAPI(data).query_by_storenumber()
        print(f"=============>Search data: {results}")
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
        data = request.form.to_dict()
        print("Form to JSON: {}".format(data))
        try:
            [data.pop(key) for key in remove_list]
        except:
            print(f"Error reading form {data}")
        else:
            flash('Attempting to upload data for storeNumber {} with data \n {}'.format(
                form.storeNumber.data, data))
            response = MongoAPI(data).write()
            return Response(response=json.dumps(response),
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

# http://localhost:5572/api/v1/stores/all
@app.route('/api/v1/stores/all', methods=['GET'])
def mongo_read_all():
    obj1 = MongoAPI()
    response = obj1.read_all()
    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')

# http://localhost:5572/api/v1/stores?id=01225
@app.route('/api/v1/stores', methods=['GET'])
def mongo_query_by_storenumber():
    if 'id' in request.args:
        id = str(request.args['id'])
        data = { "storeNumber": id }
        response = MongoAPI(data).query_by_storenumber()
        return Response(response=json.dumps(response),
                        status=200,
                        mimetype='application/json')
    else:
        return page_not_found(404)

# curl --header "Content-Type: application/json" --request POST --data \
# '{ "storeNumber": "05868", "name": "RIST05868P01", "storeId": "RIST05868P01", "location": "Burlington, MA" }' \
# http://localhost:5001/api/v1/stores
@app.route('/api/v1/stores', methods=['POST'])
def mongo_insert_data():
    data = request.get_json()
    print(data)
    if data is None or data == {}:
        return Response(response=json.dumps({"Error": "Please provide connection information"}),
                        status=400,
                        mimetype='application/json')
    response = MongoAPI(data).write()
    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')

# @app.route('/mongodb', methods=['PUT'])
# def mongo_update():
#     data = request.json
#     if data is None or data == {} or 'Filter' not in data:
#         return Response(response=json.dumps({"Error": "Please provide connection information"}),
#                         status=400,
#                         mimetype='application/json')
#     obj1 = MongoAPI(data)
#     response = obj1.update()
#     return Response(response=json.dumps(response),
#                     status=200,
#                     mimetype='application/json')

# curl -H "Accept: application/json" --request DELETE http://localhost:5001/api/v1/stores?id=01225
@app.route('/api/v1/stores', methods=['DELETE'])
def mongo_delete():
    if 'id' in request.args:
        id = str(request.args['id'])
        data = { "storeNumber": id }
        response = MongoAPI(data).delete_one()
        return Response(response=json.dumps(response),
                        status=200,
                        mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')
