
# notetaking with python

- write a file in markdown/html
- running `notetaking notes.md` will convert it to a pdf and open a pdfviewer (mupdf?)
- notetaking will continue to run in the background, every time the file is saved the pdf should update
- if the document is closed stop notetaking and close the pdf
    - this might not be possible because different editors will
        edit the file in different ways
- if the pdf is closed stop notetaking
- if there are any errors we need to notify the user via the OS, hoopefully this is universal

# TODO

- run in background somehow?
    - have system notifications if there is a syntax error
    - also call notetaking from vim
- include css support
- close background process when pdfviewer is closed
- config file, maybe use envionment variables?


## Useful resources

- inotify to track changes to the file <https://unix.stackexchange.com/questions/88399/how-to-generate-signal-interrupt-on-a-file-descriptor-in-linux>
    - might even be able to track changes to the vim .swp file too
- [python-markdown]: https://python-markdown.github.io/ for converted markdown and html with nested markdown into markdown


# Install

`./install.sh`

- add `let @t=':read! screenshot %^M'` to your vimrc

