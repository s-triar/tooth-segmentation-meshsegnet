This is a console app from python to do tooth segmentation
The only need to run is tooth_segmenter.py
It has 2 arguments:
1. --path-file : string => path to STL / VTP file
2. --type : 'max'|'min' => Type for maxillary or mandibular

The output is VTP file which is the segmented input file in saved folder
Take the out_refined.vtp file

example run:
"C:/Program Files/Python39/python.exe" "d:/NyeMan/KULIAH S2/Thesis/MeshSegNet-master/MeshSegNet-master/for-app/tooth_segmenter.py" --path-file "D:\NyeMan\KULIAH S2\Thesis\3Shape new-20220223T024758Z-001\3Shape new\1.MNF  Perempuan -18thn\MNF UpperJawScan.stl" --type max


dependencies:
- pytorch
- vedo
- scipy
- sklearn
- pygco
- numpy
- scikit-learn
- vedo
- pygco
- pandas
- Cython



How to setup and run:
1. if there is no venv folder, run `py -3 -m venv venv`
2. activate the venv with command `venv\Scripts\activate`
3. after the venv active, install flask witch command `pip install flask`
4. install Microsoft Visual for C++ 14.0 or higher 
5. install dependencies:
    `pip3 install numpy Cython scipy sklearn visdom scikit-learn pandas vedo pygco torch==1.8.2+cu102` if your PC does not have CUDA (GPU), remove +cu102
6. run below command:
    `set FLASK_ENV=development` (optional)
    `set FLASK_APP=app.py`
    `flask run`
7. if there is still error, run `pip install torchvision==0.9.2+cu102 torchaudio===0.8.2 -f https://download.pytorch.org/whl/lts/1.8/torch_lts.html` if your PC does not have CUDA (GPU), remove +cu102
8. do step number 6 again.

API:
- segment/<type>/<prediction-option>/<path-to-file (absolute)>
Call the api like this:
`http://127.0.0.1:5000/segment/max/d/D:\NyeMan\KULIAH S2\Thesis\3Shape new-20220223T024758Z-001\3Shape new\1.MNF  Perempuan -18thn\MNF UpperJawScan.stl`