This is a console app from python to do tooth segmentation
The only need to run is tooth_segmenter.py
It has 2 arguments:
--path-file : string => path to STL / VTP file
--type : 'max'|'min' => Type for maxillary or mandibular

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