from flask import Flask, Response, request,flash, render_template, make_response, redirect,send_from_directory, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import json
from datetime import datetime

from flask import Flask, request, render_template, jsonify
import os
import csv
import base64
import zipfile
import matplotlib.pyplot as plt
import numpy as np
from bokeh.embed import components
from bokeh.plotting import figure, show
from bokeh.models import HoverTool, CustomJS, ColumnDataSource

import base64


from sqlalchemy import or_, and_

from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__, static_folder="assets", template_folder="templates")
CORS(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rooms.sqlite3'
app.config['SECRET_KEY'] = "random string"
db = SQLAlchemy(app)

class BGAs(db.Model):
    id = db.Column(db.String, primary_key=True)
    timer = db.Column(db.String(50))
    board_type = db.Column(db.String(50))
    ball_size = db.Column(db.Integer)
    paste_type = db.Column(db.String(200))
    paste_size = db.Column(db.Integer)
    reflow_temp= db.Column(db.Integer)
    reflow_time = db.Column(db.Integer)
    board_list = db.Column(db.JSON)
    paste_list = db.Column(db.JSON)
    hirox_result= db.Column(db.Text)
    shear_test_result= db.Column(db.Integer)
    drop_test_result = db.Column(db.Integer)
    
    

    def __init__(self,timer, id, board_type, ball_size, paste_type, paste_size, reflow_temp, reflow_time, board_list, paste_list,hirox_result,shear_test_result,drop_test_result):
        self.id= id
        self.timer=timer
        self.board_type= board_type
        self.ball_size= ball_size
        self.paste_type= paste_type
        self.paste_size= paste_size
        self.reflow_temp= reflow_temp
        self.reflow_time= reflow_time
        self.board_list= board_list
        self.paste_list= paste_list
        self.hirox_result= hirox_result
        self.drop_test_result= drop_test_result
        self.shear_test_result= shear_test_result

class NONBGAS(db.Model):
    id = db.Column(db.String, primary_key=True)
    timer = db.Column(db.String(50))
    type = db.Column(db.String(50))
    description= db.Column(db.String(200))
    hirox_result= db.Column(db.Text)
    shear_test_result= db.Column(db.Integer)
    drop_test_result = db.Column(db.Integer)
    
    def __init__(self, id, timer,type,description,hirox_result,shear_test_result,drop_test_result):
        self.id= id
        self.timer=timer
        self.type=type
        self.description= description
        self.hirox_result= hirox_result
        self.drop_test_result= drop_test_result
        self.shear_test_result= shear_test_result

@app.before_first_request
def create_tables():
    db.create_all()




# url=  r'C:\Users\ywang\Desktop\DFLT_summary\sample inforamtion'
url = '/Users/wangyifan/Desktop/DFLT_summary'


    
def save_to_csv(data, path):
    # Determine if we need to write the header
    write_header = not os.path.exists(path)
    
    # Flatten the data dictionary
    values = list(data.values())
    print(values)
    sample_name = str(values[0]['timer'])+str(values[0]['board_type']) + str(values[0]['ballsize'])+ str(values[0]['pastetype'])+ str(values[0]['pastesize'])+ str(values[0]['reflow_temp'])

    # [{'board_type': 'w', 'ballsize': 'w', 'pastetype': 'wer', 'pastesize': 'wer', 'reflow_temp': '110', 'reflow_time': '20', 
    #   'board_list': {'Boron': '12', 'Carbon': '13', 'Aluminium': '15', 'Beryllium': '56'}, 
    #   'paste_list': {'Boron': '12', 'Carbon': '13', 'Aluminium': '15', 'Beryllium': '56'}}]

    # Flatten the data dictionary

    flat_data = {"sample_name": sample_name}
    for key, value in data.items():
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                flat_data[subkey] = subvalue
        else:
            flat_data[key] = value
    

    with open(path, 'a', newline='') as csvfile:
        fieldnames = list(flat_data.keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if write_header:
            writer.writeheader()

        writer.writerow(flat_data)
        
@app.route('/', methods=['GET'])
def home():
    return render_template("index.html")


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return "data:image/png;base64," + base64.b64encode(image_file.read()).decode('utf-8')

def generate_plot(radii, percentages, images):
    x = [i for i in range(1, len(radii) + 1)]
    y = radii

    source = ColumnDataSource(data=dict(
        x=x,
        y=y,
        images=images,
        percentages=percentages
    ))

    p = figure(title="hirox result", plot_width=600, plot_height=400, background_fill_color='lightgrey')
    p.circle('x', 'y', size=10, color="green", source=source)

    hover = HoverTool(tooltips="""
        <div>
            <div>
                <img
                    src="@images" height="200" alt="@percentages" width="200"
                    style="float: left; margin: 0px 15px 15px 0px;"
                ></img>
            </div>
            <div>
                <span style="font-size: 17px; font-weight: bold;">@percentages</span>
            </div>
        </div>
    """)

    p.add_tools(hover)

    tap_js = CustomJS(args=dict(source=source), code="""
        var images = source.data['images'];
        var index = source.selected.indices[0];
        var dataURL = images[index];
        var link = document.createElement('a');
        link.href = dataURL;
        link.download = 'image.png';
        link.click();
    """)

    p.js_on_event('tap', tap_js)

    return p

@app.route('/try')
def try_search():
    radii = [3, 5, 8]
    percentages = [39.4, 28, 38.8]
    images = [
        image_to_base64('assets/images/image4.png'),
        image_to_base64('assets/images/image5.png'),
        image_to_base64('assets/images/image6.png')
    ]
    p = generate_plot(radii, percentages, images)
    script, div = components(p)
    return render_template("resume.html", script=script, div=div)

@app.route('/show_data', methods=['GET'])
def show_data():
    
    bga_page = request.args.get('bga_page', 1, type=int)
    nonbga_page = request.args.get('nonbga_page', 1, type=int)

   
    bgas_pagination = BGAs.query.paginate(bga_page, 5, False)
    nonbgas_pagination = NONBGAS.query.paginate(nonbga_page, 5, False)

    
    bgas = bgas_pagination.items
    nonbgas = nonbgas_pagination.items

    
    bga_next_url = url_for('show_data', bga_page=bgas_pagination.next_num) if bgas_pagination.has_next else None
    bga_prev_url = url_for('show_data', bga_page=bgas_pagination.prev_num) if bgas_pagination.has_prev else None

    nonbga_next_url = url_for('show_data', nonbga_page=nonbgas_pagination.next_num) if nonbgas_pagination.has_next else None
    nonbga_prev_url = url_for('show_data', nonbga_page=nonbgas_pagination.prev_num) if nonbgas_pagination.has_prev else None

    return render_template(
        'show_data.html', 
        bgas=bgas, 
        nonbgas=nonbgas, 
        bga_next_url=bga_next_url, 
        bga_prev_url=bga_prev_url,
        nonbga_next_url=nonbga_next_url, 
        nonbga_prev_url=nonbga_prev_url
    )




@app.route('/add', methods=['GET', 'POST'])

def add_date():
    if request.method == 'POST':
        data = request.json['Data']
        print(data)
        if data['choice']=='bga':
        
            new_bga = BGAs(
                    id = data["board_type"] + data["pastetype"] + data["timer"],
                    timer=data["timer"],
                    board_type=data["board_type"],
                    ball_size=data["ballsize"],
                    paste_type=data["pastetype"],
                    paste_size=data["pastesize"],
                    reflow_temp=data["reflow_temp"],
                    reflow_time=data["reflow_time"],
                    board_list=json.dumps(data["board_list"]),
                    paste_list=json.dumps(data["paste_list"]),
                    hirox_result= data["singlePhotoResult"],
                    drop_test_result=data["drop_result"],
                    shear_test_result=data["shear_result"],
        
            )

            # Add to the database session and commit
            db.session.add(new_bga)
            db.session.commit()
        else:
            print("this is before the database")
            print(data)
            
            new_nonbga=NONBGAS(
                id = data["type"]+ data["timer"],
                timer=data["timer"],
                type= data['type'],
                description=data['description'],
                hirox_result= data["singlePhotoResult"],
                drop_test_result=data["drop_result"],
                shear_test_result=data["shear_result"],

            )
            db.session.add(new_nonbga)
            db.session.commit()


          

        return jsonify(message="Data added successfully!")
    

    return render_template("new_add.html")


def get_column_names_from_model(model):
    return [column.name for column in model.__table__.columns]



 
@app.route('/search', methods=['GET'])
def search_data():
    bgas_columns = get_column_names_from_model(BGAs)
    nonbgas_columns = get_column_names_from_model(NONBGAS)
    print(bgas_columns)

    return render_template("search_bar.html", bga_columns=bgas_columns, nonbgas_columns= nonbgas_columns)

@app.route('/get_column_values', methods=['GET'])
def get_column_values():
    column = request.args.get('column')
    
    if column in BGAs.__table__.columns:
        values = db.session.query(BGAs.__table__.c[column]).distinct().all()
    else:
        values = db.session.query(NONBGAS.__table__.c[column]).distinct().all()

    unique_values = [value[0] for value in values if value[0]]
    return jsonify({'values': unique_values})

@app.route('/get_records_by_value', methods=['GET'])
def get_records_by_value():
    value = request.args.get('value')
    column_name = request.args.get('column')  
    selection= request.args.get('selection')

    if selection=="BGA":
        records = BGAs.query.filter_by(**{column_name: value}).all()
    else:
        records = NONBGAS.query.filter_by(**{column_name: value}).all()

    # Convert records to a format that can be serialized
    records_list = [record.__dict__ for record in records]
    # Remove the _sa_instance_state key
    for record in records_list:
        record.pop('_sa_instance_state', None)
    

    return jsonify({'records': records_list})


from werkzeug.utils import secure_filename
from flask import request, jsonify
def save_to_number_csv(filename, numberValue, csv_path):
    
    file_exists = os.path.exists(csv_path)
    
    with open(csv_path, 'a', newline='') as csvfile:
        fieldnames = ['filename', 'numberValue']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
       
        if not file_exists:
            writer.writeheader()
        
        writer.writerow({'filename': filename, 'numberValue': numberValue})

@app.route('/upload', methods=['POST'])
def upload():
 
    user_data_str = request.form.get('userData')
    print(user_data_str)
   
    if not user_data_str:
        return jsonify(status="error", message="Parameter 'userData' is missing"), 400

    
    try:
        userData = json.loads(user_data_str)
    except json.JSONDecodeError:
        return jsonify(status="error", message="Invalid format for 'userData'. Expecting valid JSON."), 400


    return jsonify(status="success", message="File uploaded successfully")






if __name__=='__main__':

    app.run(host='0.0.0.0', port=8081, debug=True)