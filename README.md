
# Install

1. Install [mupdf](https://mupdf.com/) (`sudo apt install mupdf` on ubuntu)
2. Install notetaking
    - from PyPI: `pip3 install notetaking`
    - from source: `git clone https://github.com/calumsbaird/notetaking.git && pip3 install -r requirements.txt && python3 setup.py --install`




# Test

- hello world

```python3

def fenced_code():
    for i in range(10):
        print("hello world")
```

    some pseudo code

- hows this?
- *italic*
- **bold**
- ***both***

# notetaking with python

- write a file in markdown/html
- running `notetaking <file>` will convert it to a pdf and open a pdfviewer (mupdf?)
- notetaking will continue to run in the background, every time the file is saved the pdf should update
- if the document is closed stop notetaking and close the pdf
    - this might not be possible because different editors will
        edit the file in different ways
- if the pdf is closed stop notetaking
- if there are any errors we need to notify the user via the OS, hoopefully this is universal

# TODO

- include easy css support
- also call notetaking from vim
- log errors in markdown syntax
- config file, maybe use envionment variables?
- better logging messages

# Limitations

There is currently no way to track errors (syntax or otherwise)
in the markdown, html or css you write.

I havent found any lightweight math rendering yet
<https://github.com/mbarkhau/markdown-katex> has worked but
is very slow

Can't update in realtime.  Relies on linux signals when a file is saved.  Could use `.file.swp` but 

## Useful resources

- inotify to track changes to the file <https://unix.stackexchange.com/questions/88399/how-to-generate-signal-interrupt-on-a-file-descriptor-in-linux>
    - might even be able to track changes to the vim .swp file too
- [python-markdown]: https://python-markdown.github.io/ for converted markdown and html with nested markdown into markdown


# Packaging

```bash
python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/*
```


- add `let @t=':read! screenshot %^M'` to your vimrc


