# yomigana ebook

![cover](./github_assets/cover.png)

本项目旨在为日语电子书中的每一个汉字添加读音（振り仮名），让正在学习日语的读者能够更轻松地阅读日语电子书。

项目使用 [MeCab](https://taku910.github.io/mecab/)（日语形态素解析器）和 [UniDic](https://clrd.ninjal.ac.jp/unidic/)（由 NICT 开发的词典）对文本进行分词，获取每个词语对应的读音，然后以 `<ruby>` 标签的形式插入到电子书的汉字上方，方便读者识读。

- 使用 `ProcessPoolExecutor` 并行处理 HTML 文件，转换速度极快
- 支持 `-f` 参数过滤非日语段落，避免对非日语内容进行不必要的处理
- 输出文件自动添加 `with-yomigana_` 前缀

> 本工具是目前同类工具中速度最快的（对比 [Mumumu4/furigana4epub](https://github.com/Mumumu4/furigana4epub) 和 [itsupera/furiganalyse](https://github.com/itsupera/furiganalyse)）

## 使用方法

### 从 PyPI 安装

```bash
# 安装包
$ pip install yomigana-ebook

# 下载 UniDic 词典（必须）
$ python -m unidic download

# 为日语电子书添加读音
$ yomigana_ebook [epub文件...]

# 使用 -f 参数过滤非日语段落
$ yomigana_ebook -f [epub文件...]
```

### 从源码构建

```bash
$ git clone https://github.com/FFFold/yomigana-ebook.git
$ cd yomigana-ebook

# 安装依赖（使用 Poetry）
$ poetry install

# 下载 UniDic 词典（必须）
$ python -m unidic download

# 运行
$ poetry run yomigana_ebook [epub文件...]
```

### Windows 用户

由于 fugashi 在 Windows 上存在一个已知 bug（详见 [polm/fugashi#42](https://github.com/polm/fugashi/issues/42)），必须在虚拟环境中使用本工具。

#### 从 PyPI 安装

```bash
# 创建虚拟环境
$ python -m venv .venv

# 激活虚拟环境
$ .venv\Scripts\activate

# 安装包
$ pip install yomigana-ebook

# 下载 UniDic 词典
$ python -m unidic download

# 为日语电子书添加读音
$ yomigana_ebook [epub文件...]
```

#### 从源码构建

```bash
$ git clone https://github.com/FFFold/yomigana-ebook.git
$ cd yomigana-ebook

# 创建并激活虚拟环境
$ python -m venv .venv
$ .venv\Scripts\activate

# 安装项目
$ pip install .

# 下载 UniDic 词典
$ python -m unidic download

# 为日语电子书添加读音
$ yomigana_ebook [epub文件...]
```

退出虚拟环境：

```bash
$ deactivate
```

### 通过 Docker 运行 Web Demo

Web Demo 基于 FastAPI（后端）+ Vite/React（前端）构建，提供网页版的读音标注功能。

> 注意：必须在项目根目录下执行以下命令，不要在 `web-demo` 目录中执行！

1. 构建镜像：

    ```bash
    $ docker build -t yomigana-ebook/web-demo -f Dockerfile.web-demo .
    ```

2. 运行容器：

    ```bash
    $ docker run --rm -p 8000:8000 yomigana-ebook/web-demo --host 0.0.0.0
    ```

3. 打开浏览器访问 `http://localhost:8000` 即可使用。

## 致谢

本项目受到 [Mumumu4/furigana4epub](https://github.com/Mumumu4/furigana4epub) 和 [itsupera/furiganalyse](https://github.com/itsupera/furiganalyse) 的启发，并引用了其中部分代码。
