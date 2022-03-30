from flask import Flask
import tooth_segmenter
import os

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, This is 3D Tooth Segmentation API!</p>"

@app.route("/segment/<string:type_object>/<string:pred_option>/<path:path_file>")
def segment(type_object,pred_option, path_file):
    tooth_segmenter.segment(type_object, pred_option, path_file)
    
    if(pred_option=='all'):
        return {
            'downsampling': os.path.join(os.getcwd(),'saved','out_downsampling.vtp'),
            'downsampling_refined': os.path.join(os.getcwd(),'saved','out_downsampling_refined.vtp'),
            'refined': os.path.join(os.getcwd(),'saved','out_refined.vtp')
        }
    if(pred_option=='d'):
        return {
            'downsampling': os.path.join(os.getcwd(),'saved','out_downsampling.vtp'),
        }
    if(pred_option=='d_r'):
        return {
            'downsampling_refined': os.path.join(os.getcwd(),'saved','out_downsampling_refined.vtp'),
        }
    if(pred_option=='r'):
        return {
            'refined': os.path.join(os.getcwd(),'saved','out_refined.vtp')
        }
    else:
        raise ValueError('Prediction option is not exist.')

