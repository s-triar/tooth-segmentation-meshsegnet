import sys
import argparse
import predict

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process teeth segmentation.')
    parser.add_argument('--path-file', type=str,
                    help='path to VTP file')
    parser.add_argument('--type', type=str,default='max',
                    help='Default \'max\'.\nThere are 2 values: \'max\' for maxillary and \'man\' for mandibular')
    args = parser.parse_args()
    path_file = args.path_file
    type_object = args.type
    
    if type_object != 'max' and type_object != 'man':
        raise ValueError("--type must be either 'max' or 'man'")
    if path_file == None:
        raise ValueError("--path-file must be filled with path to file")
    model = './models/MeshSegNet_Max_15_classes_72samples_lr1e-2_best.zip'
    if(type_object == 'man'):
        model = './models/MeshSegNet_Man_15_classes_72samples_lr1e-2_best.zip'
    predict.predict(model,path_file)
    