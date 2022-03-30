import os
import numpy as np
import torch
import torch.nn as nn
from meshsegnet import *
import vedo
import pandas as pd
from losses_and_metrics_for_mesh import *
from scipy.spatial import distance_matrix
import scipy.io as sio
import shutil
import time
from sklearn.svm import SVC # uncomment this line if you don't install thudersvm
# from thundersvm import SVC # comment this line if you don't install thudersvm
from sklearn.neighbors import KNeighborsClassifier
from pygco import cut_from_graph
import glob
import utils


# pred_option = ['all','d','d_r','r']
def predict(modelpath, filepath, pathsave='./saved', pred_option='all'):
    upsampling_method = 'KNN'
    if not os.path.exists(pathsave):
        os.mkdir(pathsave)
    num_classes = 15
    num_channels = 15
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = MeshSegNet(num_classes=num_classes, num_channels=num_channels).to(device, dtype=torch.float)
    checkpoint = torch.load(modelpath, map_location='cpu')
    model.load_state_dict(checkpoint['model_state_dict'])
    del checkpoint
    model = model.to(device, dtype=torch.float)
    torch.backends.cudnn.benchmark = True
    torch.backends.cudnn.enabled = True
    model.eval()
    with torch.no_grad():
        start_time = time.time()
        # create tmp folder
        tmp_path = './.tmp/'
        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)
        print('Predicting Sample filename: {}'.format(filepath))
        mesh = vedo.load(filepath)
        
        # pre-processing: downsampling
        print('\tDownsampling...')
        target_num = 10000
        ratio = target_num/mesh.NCells() # calculate ratio
        mesh_d = mesh.clone()
        mesh_d.decimate(fraction=ratio)
        predicted_labels_d = np.zeros([mesh_d.NCells(), 1], dtype=np.int32)
        
        print('\tPredicting...')
        cells = np.zeros([mesh_d.NCells(), 9], dtype='float32')
        for i in range(len(cells)):
            cells[i][0], cells[i][1], cells[i][2] = mesh_d.polydata().GetPoint(mesh_d.polydata().GetCell(i).GetPointId(0)) # don't need to copy
            cells[i][3], cells[i][4], cells[i][5] = mesh_d.polydata().GetPoint(mesh_d.polydata().GetCell(i).GetPointId(1)) # don't need to copy
            cells[i][6], cells[i][7], cells[i][8] = mesh_d.polydata().GetPoint(mesh_d.polydata().GetCell(i).GetPointId(2)) # don't need to copy

        original_cells_d = cells.copy()
        
        mean_cell_centers = mesh_d.centerOfMass()
        cells[:, 0:3] -= mean_cell_centers[0:3]
        cells[:, 3:6] -= mean_cell_centers[0:3]
        cells[:, 6:9] -= mean_cell_centers[0:3]

        # customized normal calculation; the vtk/vedo build-in function will change number of points
        v1 = np.zeros([mesh_d.NCells(), 3], dtype='float32')
        v2 = np.zeros([mesh_d.NCells(), 3], dtype='float32')
        v1[:, 0] = cells[:, 0] - cells[:, 3]
        v1[:, 1] = cells[:, 1] - cells[:, 4]
        v1[:, 2] = cells[:, 2] - cells[:, 5]
        v2[:, 0] = cells[:, 3] - cells[:, 6]
        v2[:, 1] = cells[:, 4] - cells[:, 7]
        v2[:, 2] = cells[:, 5] - cells[:, 8]
        mesh_normals = np.cross(v1, v2)
        mesh_normal_length = np.linalg.norm(mesh_normals, axis=1)
        mesh_normals[:, 0] /= mesh_normal_length[:]
        mesh_normals[:, 1] /= mesh_normal_length[:]
        mesh_normals[:, 2] /= mesh_normal_length[:]
        mesh_d.addCellArray(mesh_normals, 'Normal')
        
        # preprae input
        points = mesh_d.points().copy()
        points[:, 0:3] -= mean_cell_centers[0:3]
        normals = mesh_d.getCellArray('Normal').copy() # need to copy, they use the same memory address
        barycenters = mesh_d.cellCenters() # don't need to copy
        barycenters -= mean_cell_centers[0:3]
        
        #normalized data
        maxs = points.max(axis=0)
        mins = points.min(axis=0)
        means = points.mean(axis=0)
        stds = points.std(axis=0)
        nmeans = normals.mean(axis=0)
        nstds = normals.std(axis=0)

        for i in range(3):
            cells[:, i] = (cells[:, i] - means[i]) / stds[i] #point 1
            cells[:, i+3] = (cells[:, i+3] - means[i]) / stds[i] #point 2
            cells[:, i+6] = (cells[:, i+6] - means[i]) / stds[i] #point 3
            barycenters[:,i] = (barycenters[:,i] - mins[i]) / (maxs[i]-mins[i])
            normals[:,i] = (normals[:,i] - nmeans[i]) / nstds[i]

        X = np.column_stack((cells, barycenters, normals))
        
        # computing A_S and A_L
        A_S = np.zeros([X.shape[0], X.shape[0]], dtype='float32')
        A_L = np.zeros([X.shape[0], X.shape[0]], dtype='float32')
        D = distance_matrix(X[:, 9:12], X[:, 9:12])
        A_S[D<0.1] = 1.0
        A_S = A_S / np.dot(np.sum(A_S, axis=1, keepdims=True), np.ones((1, X.shape[0])))

        A_L[D<0.2] = 1.0
        A_L = A_L / np.dot(np.sum(A_L, axis=1, keepdims=True), np.ones((1, X.shape[0])))
        
        # numpy -> torch.tensor
        X = X.transpose(1, 0)
        X = X.reshape([1, X.shape[0], X.shape[1]])
        X = torch.from_numpy(X).to(device, dtype=torch.float)
        A_S = A_S.reshape([1, A_S.shape[0], A_S.shape[1]])
        A_L = A_L.reshape([1, A_L.shape[0], A_L.shape[1]])
        A_S = torch.from_numpy(A_S).to(device, dtype=torch.float)
        A_L = torch.from_numpy(A_L).to(device, dtype=torch.float)

        tensor_prob_output = model(X, A_S, A_L).to(device, dtype=torch.float)
        patch_prob_output = tensor_prob_output.cpu().numpy()

        for i_label in range(num_classes):
            predicted_labels_d[np.argmax(patch_prob_output[0, :], axis=-1)==i_label] = i_label

        # output downsampled predicted labels
        mesh2 = mesh_d.clone()
        mesh2.addCellArray(predicted_labels_d, 'Label')
        if(pred_option=='d' or pred_option =='all'):
            vedo.write(mesh2, os.path.join(pathsave, '{}_downsampling.vtp'.format('out')))
        if('r' in pred_option or 'd_r' == pred_option or pred_option=='all'):
            # refinement
            print('\tRefining by pygco...')
            round_factor = 100
            patch_prob_output[patch_prob_output<1.0e-6] = 1.0e-6

            # unaries
            unaries = -round_factor * np.log10(patch_prob_output)
            unaries = unaries.astype(np.int32)
            unaries = unaries.reshape(-1, num_classes)

            # parawise
            pairwise = (1 - np.eye(num_classes, dtype=np.int32))

            #edges
            normals = mesh_d.getCellArray('Normal').copy() # need to copy, they use the same memory address
            cells = original_cells_d.copy()
            barycenters = mesh_d.cellCenters() # don't need to copy
            cell_ids = np.asarray(mesh_d.faces())

            lambda_c = 30
            edges = np.empty([1, 3], order='C')
            for i_node in range(cells.shape[0]):
                # Find neighbors
                nei = np.sum(np.isin(cell_ids, cell_ids[i_node, :]), axis=1)
                nei_id = np.where(nei==2)
                for i_nei in nei_id[0][:]:
                    if i_node < i_nei:
                        cos_theta = np.dot(normals[i_node, 0:3], normals[i_nei, 0:3])/np.linalg.norm(normals[i_node, 0:3])/np.linalg.norm(normals[i_nei, 0:3])
                        if cos_theta >= 1.0:
                            cos_theta = 0.9999
                        theta = np.arccos(cos_theta)
                        phi = np.linalg.norm(barycenters[i_node, :] - barycenters[i_nei, :])
                        if theta > np.pi/2.0:
                            edges = np.concatenate((edges, np.array([i_node, i_nei, -np.log10(theta/np.pi)*phi]).reshape(1, 3)), axis=0)
                        else:
                            beta = 1 + np.linalg.norm(np.dot(normals[i_node, 0:3], normals[i_nei, 0:3]))
                            edges = np.concatenate((edges, np.array([i_node, i_nei, -beta*np.log10(theta/np.pi)*phi]).reshape(1, 3)), axis=0)
            edges = np.delete(edges, 0, 0)
            edges[:, 2] *= lambda_c*round_factor
            edges = edges.astype(np.int32)

            refine_labels = cut_from_graph(edges, unaries, pairwise)
            refine_labels = refine_labels.reshape([-1, 1])

            # output refined result
            mesh3 = mesh_d.clone()
            mesh3.addCellArray(refine_labels, 'Label')
        if(pred_option=='d_r' or pred_option =='all'):
            vedo.write(mesh3, os.path.join(pathsave, '{}_downsampling_refined.vtp'.format('out')))

        if(pred_option=='r' or pred_option=='all'):
            # upsampling
            print('\tUpsampling...')
            if mesh.NCells() > 100000:
                target_num = 100000 # set max number of cells
                ratio = target_num/mesh.NCells() # calculate ratio
                mesh.decimate(fraction=ratio)
                print('Original contains too many cells, simpify to {} cells'.format(mesh.NCells()))

            # get fine_cells
            cells = np.zeros([mesh.NCells(), 9], dtype='float32')
            for i in range(len(cells)):
                cells[i][0], cells[i][1], cells[i][2] = mesh.polydata().GetPoint(mesh.polydata().GetCell(i).GetPointId(0)) # don't need to copy
                cells[i][3], cells[i][4], cells[i][5] = mesh.polydata().GetPoint(mesh.polydata().GetCell(i).GetPointId(1)) # don't need to copy
                cells[i][6], cells[i][7], cells[i][8] = mesh.polydata().GetPoint(mesh.polydata().GetCell(i).GetPointId(2)) # don't need to copy

            fine_cells = cells

            barycenters = mesh3.cellCenters() # don't need to copy
            fine_barycenters = mesh.cellCenters() # don't need to copy

            
            
            neigh = KNeighborsClassifier(n_neighbors=3)
            # train KNN
            #neigh.fit(mesh2.cells, np.ravel(refine_labels))
            #fine_labels = neigh.predict(fine_cells)

            neigh.fit(barycenters, np.ravel(refine_labels))
            fine_labels = neigh.predict(fine_barycenters)
            fine_labels = fine_labels.reshape(-1, 1)

            mesh.addCellArray(fine_labels, 'Label')
            vedo.write(mesh, os.path.join(pathsave, '{}_refined.vtp'.format('out')))

        #remove tmp folder
        shutil.rmtree(tmp_path)

        end_time = time.time()
        print('Sample filename: {} completed'.format(filepath))
        print('computing time: {0:.2f} sec'.format(end_time-start_time))
