#jupyterlab 安装及简单使用
pip install jupyterlab
#运行jupyter
jupyter lab --ip=0.0.0.0 --allow-root
jupyter lab --no-browser
#查看令牌
jupyter notebook list
#列出已安装扩展
jupyter labextension list
#卸载已安装扩展
jupyter labextension uninstall extension_name

常用快捷键
命令模式 (按键 Esc 开启)
Enter : 转入编辑模式
Shift-Enter : 运行本单元，选中下个单元
Ctrl-Enter : 运行本单元
Alt-Enter : 运行本单元，在其下插入新单元
Y : 单元转入代码状态
M :单元转入markdown状态
R : 单元转入raw状态
1 : 设定 1 级标题
2 : 设定 2 级标题
3 : 设定 3 级标题
4 : 设定 4 级标题
5 : 设定 5 级标题
6 : 设定 6 级标题
Up : 选中上方单元
K : 选中上方单元
Down : 选中下方单元
J : 选中下方单元
Shift-K : 扩大选中上方单元
Shift-J : 扩大选中下方单元
A : 在上方插入新单元
B : 在下方插入新单元
X : 剪切选中的单元
C : 复制选中的单元
Shift-V : 粘贴到上方单元
V : 粘贴到下方单元
Z : 恢复删除的最后一个单元
D,D : 删除选中的单元
Shift-M : 合并选中的单元
Ctrl-S : 文件存盘
S : 文件存盘
L : 转换行号
O : 转换输出
Shift-O : 转换输出滚动
Esc : 关闭页面
Q : 关闭页面
H : 显示快捷键帮助
I,I : 中断Notebook内核
0,0 : 重启Notebook内核
Shift : 忽略
Shift-Space : 向上滚动
Space : 向下滚动

编辑模式 ( Enter 键启动)
Tab : 代码补全或缩进
Shift-Tab : 提示函数参数，查看函数源码
Ctrl-] : 缩进
Ctrl-[ : 解除缩进
Ctrl-A : 全选
Ctrl-Z : 复原
Ctrl-Shift-Z : 再做
Ctrl-Y : 再做
Ctrl-Home : 跳到单元开头
Ctrl-Up : 跳到单元开头
Ctrl-End : 跳到单元末尾
Ctrl-Down : 跳到单元末尾
Ctrl-Left : 跳到左边一个字首
Ctrl-Right : 跳到右边一个字首
Ctrl-Backspace : 删除前面一个字
Ctrl-Delete : 删除后面一个字
Esc : 进入命令模式
Ctrl-M : 进入命令模式
Shift-Enter : 运行本单元，选中下一单元
Ctrl-Enter : 运行本单元
Alt-Enter : 运行本单元，在下面插入一单元
Ctrl-Shift-- : 分割单元
Ctrl-Shift-Subtract : 分割单元
Ctrl-S : 文件存盘
Shift : 忽略
Up : 光标上移或转入上一单元
Down :光标下移或转入下一单元

#常用配置

主题字体设置
Setting --> Jupyter Lab Theme --> JupyterLab Dark
点击View-->点击Toggle Line Numbers

Jupyter Lab 插件安装
Settings --> Advanced Settings Editor ，将Extension Manager 里的enabled 的 false 改成 true

Markdown、Raw cell字体设置
Settings --> Advanced Settings Editor --> Notebook --> 将系统默认配置拷贝到个人配置，修改'fontSize'字体大小 18
文本编辑字体设置
Settings --> Advanced Settings Editor --> Text Editor --> 将系统默认配置拷贝到个人配置，修改'fontSize'字体大小 18

配置jupyrter工作目录：
1.打开C:\Users\Administrator\.jupyter\jupyter_notebook_config.py文件，修改 c.NotebookApp.notebook_dir = ''配置项
2.右键查看jupyter快捷方式的属性，找到快捷方式的目标，修改最后一个参数及是工作目录


Jupyter中的魔法函数:
1）%pwd
该魔法函数用于显示Jupyter当前的工作空间。
2）%hist
该魔法函数用于显示当前Jupyter中，所有运行过的历史代码。
3）%who
该魔法函数用于显示当前Jupyter环境中的所有变量或名称。
4）%reset
该魔法函数用于删除当前Jupyter环境中的所有变量或名称。
5)%time
该魔法函数用于计算当前代码行的运行时长。
6)%timeit
该魔法函数用于计算当前代码行的平均运行时长（即在执行一个语句100000次(默认情况下)后，再给出运行最快3次的平均值。
7)%%timeit
该魔法函数用于计算当前cell的代码运行时长。
8）%matplotlib
该魔法函数用于显示绘图结果的风格，默认为%matplotlib inline，是直接将图片显示在浏览器中，如果希望图片单独生成，可以使用%matplotlib。
9）%load
该魔法函数用于加载本地Python文件或者网络中的Python文件，例如本地脚本文件的加载：%load xxx.py。
10）%run
该魔法函数用于运行本地或网络中的Python文件，例如本地脚本文件的运行：%load xxx.py。
