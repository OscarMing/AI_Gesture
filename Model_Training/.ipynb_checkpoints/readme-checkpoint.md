# I. Filter required gestures and restore 

## datasetfilter.ipynb

1. Gesture type filter
2. Restore Dataset which is needed
3. XX, YY, ZZ which is gesture file name

### File Structure
* {GestureDataset File Name}
    * Swiping Left
        * XX
        * YY 
        * ZZ
    * Swiping Right
        * XX
        * YY 
        * ZZ
    * Swiping Up
        * XX
        * YY 
        * ZZ
    * Swiping Down
        * XX
        * YY 
        * ZZ
    * Turning Hand Counterclockwise
        * XX
        * YY 
        * ZZ
    * Turning Hand Clockwise
        * XX
        * YY 
        * ZZ
   
# II. Dataset Preprocessing

## datapreprocessing.ipynb

* Gesture to class map
    * 'SwipingLeft':0,
    * 'SwipingRight':1, 
    * 'SwipingDown':2, 
    * 'SwipingUp':3, 
    * 'TurningHandClockwise':4, 
    * 'TurningHandCounterclockwise':5
           
* A. Preprocessing Dataset info for training and testing
  * Preprocessing Dataset info will save to [./list](./list) 

* B. Training Data info Structure
    * EX: /GestureDataset/B/TurningHandClockwise/37958/ 36 4
      1. Data Folder Directory : /GestureDataset/B/TurningHandClockwise/37958/
      2. Amount of frames in the folder : 36
      3. Class of this folder : 4

* C. Testing Data info Structure
    * EX: /GestureDataset/B/TurningHandClockwise/47908/ 9 4 35
      1. Data Folder Directory : /GestureDataset/B/TurningHandClockwise/47908/
      2. Middle frame index  :9
      3. Class of this folder : 4
      4. Amount of frames in the folder : 35

# III. Model Training

* pretrained Folder => pretrain weight [./pretrained](./pretrained) 

1. K_3DCNN_v1
  * Data Sampling => 採各資料夾資料前、中、後 連續16幀
  * Data Augmentation => X
  * Batch => 32
  * Epochs => 30-50

2. K_3DCNN_v2
  * Data Sampling => 採各資料夾資料前、中、後 連續16幀
  * Data Augmentation => 隨機上下、左右翻轉
  * Batch => 32
  * Epochs => 30

3. K_3DCNN_v3
  * Data Sampling => 採各資料夾資料前、中、後 連續16幀，第一幀重複六次，再向後補連續10幀;最後一幀重複六次，再向前補連續10幀
  * Data Augmentation => 隨機上下、左右翻轉
  * Batch => 32
  * Epochs => 30 or 50
  * Model => Conv3a-3b、Conv4a-4b加入Dropout，FC6、FC7加入L1, L2 Regularizer

4. K_3DCNN_v4
  * GPU 平行運算
  * Data Sampling => 採各資料夾資料前、中、後 連續16幀，第一幀重複六次，再向後補連續10幀;最後一幀重複六次，再向前補連續10幀
  * Data Augmentation => 隨機上下、左右翻轉
  * Batch => 32 or64
  * Epochs => 30
  * Model => Conv3a-3b、Conv4a-4b加入Dropout，FC6、FC7加入L1, L2 Regularizer ; 
             Conv4b-5a、Conv5a-5b加入Dropout，FC6、FC7加入L1, L2 Regularizer

5. K_3DCNN-svm-xgb
  * a.使用表現較佳的model做二次訓練
  * b.分別將訓練資料送入model，並分別截出Flatten and Dense Layer資料
  * c.將截出Flatten and Dense Layer資料分別用SVM and XGB 做二次訓練
  
6. K_3DCNN_v42
  * GPU 平行運算
  * Data Sampling => 採各資料夾資料前、中、後 連續16幀，取得資料中段影像索引值，向前與後各推進16個索引值，起始索引值以間隔一張取得影像，共構成16 Frames 輸入影像 
  * Data Augmentation => 隨機上下、左右翻轉
  * Batch => 32 
  * Epochs => 30
  * Model => Conv3a-3b、Conv4a-4b加入Dropout，FC6、FC7加入L1, L2 Regularizer