from flask import Flask
import tooth_segmenter
import os

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/segment/<string:type_object>/<path:path_file>")
def segment(type_object,path_file):
    tooth_segmenter.segment(type_object,path_file)
    return {
        'downsampling': os.path.join(os.getcwd(),'saved','out_downsampling.vtp'),
        'downsampling_refined': os.path.join(os.getcwd(),'saved','out_downsampling_refined.vtp'),
        'refined': os.path.join(os.getcwd(),'saved','out_refined.vtp')
    }

