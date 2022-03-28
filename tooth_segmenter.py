import sys
import argparse
import predict

def segment(type,path):
    checkArgs(type,path)
    
    model = './models/MeshSegNet_Max_15_classes_72samples_lr1e-2_best.zip'
    if(type == 'man'):
        model = './models/MeshSegNet_Man_15_classes_72samples_lr1e-2_best.zip'
    predict.predict(model,path)

def checkArgs(type_object, path_file):
    if type_object != 'max' and type_object != 'man':
        raise ValueError("--type must be either 'max' or 'man'")
    if path_file == None:
        raise ValueError("--path-file must be filled with path to file")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process teeth segmentation.')
    parser.add_argument('--path-file', type=str,
                    help='path to VTP file')
    parser.add_argument('--type', type=str,default='max',
                    help='Default \'max\'.\nThere are 2 values: \'max\' for maxillary and \'man\' for mandibular')
    args = parser.parse_args()
    path_file = args.path_file
    type_object = args.type
    
    segment(type_object,path_file)
    
    