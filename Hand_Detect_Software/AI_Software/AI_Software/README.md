# 以下為軟體操作說明
* 1. Python環境設置
* 2. App 使用說明

## 1. Python環境設置
* 1.0 安裝Python 3.7.x版本
* 1.1 安裝外部模組
  * 1.1.1 請修改Python目錄下install_all_modules.bat中"Python安裝路徑中Script路徑"
  * 1.1.2 請執行Python目錄下install_all_modules.bat
* 1.2 將自訂義的模組"Demo\libs"加入到Python安裝路徑中
  * 1.2.1 請修改cam_demo_lib.pth中自訂義的模組路徑
  * 1.2.2 請複製cam_demo_lib.pth到Python安裝路徑中下的"Lib\site-packages"中
* 1.3 開發專案
  * 1.3.1 請修改open_jupyter_lab.bat中"工作目錄"和"Python安裝路徑中jupyter-lab路徑"
  * 1.3.2 請開啟"Demo\Demo.ipynb"進行修改, 修改完成匯出Demo.py並覆蓋

## 2. App 使用說明
* 2.1 功能
  * 2.1.1 擷取Cam影像進行手勢辨識同時控制youtube 360影片
  * 2.1.2 手勢種類與影片對應
    * 2.1.2.1 左: 影片轉左
    * 2.1.2.2 右: 影片轉右
    * 2.1.2.3 上: 影片轉上
    * 2.1.2.4 下: 影片轉下
    * 2.1.2.5 順時針: 放大影片
    * 2.1.2.6 逆時針: 縮小影片
* 2.2 執行App
  * 2.2.1 請修改main.bat中"工作目錄下Demo路徑"和Python安裝路徑
  * 2.2.2 請執行main.bat
* 2.3 關閉App
  * 2.3.1 點擊鍵盤中"q"鍵
* 2.4 更換youtube 360影片
  * 2.4.1 修改Demo\Demo.py中的youtube_360_video_url變數
* 2.5 如要更換應用
  * 2.5.1 請繼承Demo\libs\desktop_lib.py進行實作
  * 2.5.2 增加Demo\libs\threed_cnn_lib.py中類別Three_D_CNN_Thread的mode變數
  * 2.5.3 修改Demo\Demo.py中threed_cnn_mode變數