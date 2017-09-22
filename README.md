BAO is a digital book analyzer and organizer. Its major goal relates the implementations of a set of functions for automatic classification of e-books in various formats (pdf, djvu, epub).

Currently you need python2 to run it. In the future it will be fully python3-compatible. We suggest you to set up a python-virtualenv:

```
# install virtualenv, it depends on your O.S.
$ virtualenv BAO-venv
$ cd BAO-venv/bin
$ source activate
$ cd .. && git clone https://git.eigenlab.org/eigenlab/BAO.git
```
and to install needed libraries in your fresh virtualenv:

```
$ pip2 install python-magic PyPF2 xmltodict
$ pip2 install --upgrade --ignore-installed slate==0.3 pdfminer==20110515
```

the last command is needed in order to make advanced text extraction work, as it installs compatible versions of slate and pdfminer.

Lastly, you only need to specify the folder path you want to analyse (at the moment, analysis will be carried on only on files with type application/pdf).
Now, everything should be fine (it will not, for sure: please, be patient!), and you can start the script simply as:

```
$ cd BAO-venv/BAO/
$ python2 main.py
```
