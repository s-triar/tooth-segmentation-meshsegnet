import sys
import argparse
import predict

def segment(type,pred_option, path):
    checkArgs(type,path,pred_option)
    
    model = './models/MeshSegNet_Max_15_classes_72samples_lr1e-2_best.zip'
    if(type == 'man'):
        model = './models/MeshSegNet_Man_15_classes_72samples_lr1e-2_best.zip'
    predict.predict(model,path,pred_option=pred_option)

def checkArgs(type_object, path_file, pred_option):
    if type_object != 'max' and type_object != 'man':
        raise ValueError("--type must be either 'max' or 'man'")
    if pred_option not in ['all','d','d_r','r']:
        raise ValueError("--pred-option must be 'all', 'd', 'd_r','r'")
    if path_file == None:
        raise ValueError("--path-file must be filled with path to file")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process teeth segmentation.')
    parser.add_argument('--path-file', type=str,
                    help='path to VTP file')
    parser.add_argument('--type', type=str,default='max',
                    help='Default \'max\'.\nThere are 2 values: \'max\' for maxillary and \'man\' for mandibular')
    parser.add_argument('--pred-option', type=str,default='all',
                    help='Default \'all\'.\nThere are 2 values: \'d\' for downsampling, \'d_r\' for refined downsampling, and \'r\' for refined ' )
    args = parser.parse_args()
    path_file = args.path_file
    type_object = args.type
    pred_option = args.pred_option
    
    segment(type_object,pred_option,path_file)
    
    