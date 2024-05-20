# Intro

This is a native app which allow you to install, update and remove Blender extensions

# Feature

+ Extension manage(Local repo)
    + select different repo
    + edit / remove extension
    + search
+ Convert addon to extension
    + select .py/ folder addon
    + make it an extension and send to repo
+ Edit extension
    + edit extension info
    + edit extension tags

![view1png](doc/images/view1.png)

![view1png](doc/images/view2.png)

![view1png](doc/images/view3.png)

Edit Dialog / Edit Tag

![](doc/images/dialog.png)

![](doc/images/tagEdit.png)

# Develop

> use venv to setup, run and build

install dependencies

```
pip install -r requirements.txt
```

### run

```
main.py
```

args

+ `--dev` auto-reload
+ `--web` run on browser

### build

> only windows now
> windows_output: .dist/BME.exe

```
build.py
```