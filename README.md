# 功能

1. 抓取特斯拉二手车各车型（my，mx，m3，ms）的以下数据：
   - 车架号,型号,系列,公里数,城市,价格,续航,时速,百公里加速
2. 将抓取的数据保存到csv文件，以天为单位进行保存

# 使用方法

1. 使用python的selenium，csv通过git同步到GitHub，需要安装以下库

   - ```python
     pip3 insatll selenium
     pip3 install GitPython
     ```

   - 推荐chrome及chrome驱动，相关下载请见<a href="https://developer.chrome.com/docs/chromedriver/downloads?hl=zh-cn">下载链接</a>

2. 需要在根目录创建config.py

   - 用来存放Chromedriver的路径

     ```python 
     DRIVER_PATH = 'your path'
     ```

3. 运行main.py即可实现
