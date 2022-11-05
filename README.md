# xxtmg

### 基于selenium的简单的学习通刷课脚本

### 介绍
此脚本只针对edge浏览器，其他浏览器自行修改  
由于学习通课程种类和网页结构复杂，无法兼容所有类型的课程
## 使用方式 
- clone此仓库
```bash
 git clone https://github.com/imag-er/xxtmg
 ```
- 下载对应EDGE版本的edgedriver并解压到此目录
- 在目录下创建aandp.txt文件并写入账号密码
```bash
 echo 账号 > aandp.txt && echo 密码 >> aandp.txt
```
- 安装selenium
```python
   pip install selenium
```
- 运行main.py