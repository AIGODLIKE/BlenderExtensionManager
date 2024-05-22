# Intro

This is a native app which allow you to install, update and remove Blender extensions

# Download

Download link: [BlenderExtensionManager_win](PLACEHOLDER_FOR_DOWNLOAD_LINK)

# Feature

+ Extension manage(Local repo)
    1. select one repo
    2. edit / remove extension
    3. search
+ Convert addon to extension
    1. select .py/ folder addon
    2. make it an extension
    3. edit and send to repo
+ Edit extension
    + edit extension info
    + edit extension tags

![view1png](doc/images/view1.png)

![view1png](doc/images/view2.png)

![view1png](doc/images/view3.png)

Edit Dialog / Edit Tags

![](doc/images/dialog.png)

![](doc/images/tagEdit.png)



# Usage

1. Clone the repository

```
git clone <repository_url>
cd <repository_directory>
```

2. Set up a virtual environment

```
python -m venv venv
venv\Scripts\activate  # on Windows
```

3. Install the required dependencies

```
pip install -r requirements.txt
```

### run

```
python main.py --dev
```

+ `--dev` auto-reload
+ `--web` run on browser

### build

> only windows now
> windows_output: .dist/BME.exe

```
python build.py
```