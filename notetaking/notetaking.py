#!/usr/bin/env python3

# Track changes to a markdown file, convert markdown to a pdf
# display the pdf and update it consistently

#from __future__ import print_function
import os, sys

help_prompt = '''
usage: python3 notetaking.py <filename> [flags]

Options and arguments:
-h,--help       : print this help menu
-d              : display debugging information TODO
-b,--background : run in background
--html          : output a .html document for debugging
'''

# Goes through inotify events and yield the ones with the correct 
# filename
def file_reads(i, filenames_in_question):

    for event in i.event_gen(yield_nones=False):
        (_, type_names, path, filename) = event

        #print("PATH=[{}] FILENAME=[{}] EVENT_TYPES={}".format(
        #      path, filename, type_names))   
        #print(filenames_in_question)

        if filename in filenames_in_question:
            for access_type in type_names:
                yield access_type


def process_document(filename, pdf_filename, html_filename=None):

    # check file exists
    if not os.path.isfile(filename):
        open(filename,'a').close()

    # convert contents to html
    import markdown
    text = open(filename).read()
    html = markdown.markdown(text, extensions=['extra', 'codehilite', 'toc'])

    if html_filename is not None:
        with open(html_filename,'w') as f:
            f.write(html)
   
    # convert contents to pdf
    default_css = f'{os.path.dirname(os.path.abspath(__file__))}/css/default.css'
    from weasyprint import HTML, CSS
    HTML(string=html).write_pdf(pdf_filename,
    stylesheets=[default_css ])


def pdfviewer_handler(pdfviewer_subprocess):
    print('waiting')
    pdfviewer_subprocess.wait()
    print('done')
    import _thread
    _thread.interrupt_main() # TODO a more elegant solution would be nice but I cant find one
    


def main():

    # help prompt
    if len(sys.argv) < 2 or '-h' in sys.argv or '--help' in sys.argv:
        print(help_prompt)
        sys.exit(1)

    # run in background as daemon if '-b' flag
    if any(x in sys.argv for x in ['-b', '--background']):

        # Write stderr to /tmp/notetaking.log
        original_stderr = sys.stderr
        file_err = open('/tmp/notetaking.log', 'w', buffering=1) # I tried with .txt also
        sys.stderr = file_err

        # this code is how you revert the stderr
        #sys.stderr = original_stderr
        #file_err.close()

        # Also write stdout to log file
        sys.stdout = file_err

        # Daemonise
        from . import daemon
        daemon.createDaemon()

    # filename
    assert len(sys.argv) >= 1
    filename = sys.argv[1]

    # conjuer a filename for the pdf and for a html doc
    file_and_path, extension = os.path.splitext(filename)
    assert extension in ['.md','.markdown', '.html'], f"Unknown extension {extension}"
    pdf_filename = file_and_path + '.pdf'
    if '--html' in sys.argv and extension != 'html':
        html_filename = file_and_path + '.html'
    else:
        html_filename = None

    # Initial conversion of to a pdf
    process_document(filename, pdf_filename, html_filename)
    
    # Open pdf
    import subprocess
    pdfviewer = 'mupdf'
    pdfviewer_subprocess = subprocess.Popen([pdfviewer,pdf_filename])

    # Start a thread that will close the whole program when the
    # pdfviewer is closed
    import threading
    threading.Thread(target=pdfviewer_handler, args=(pdfviewer_subprocess,)).start()

    # setup inotify in the current directory
    # TODO ideally we dont need to check the whole directory
    # but inotify is buggy for one file
    import inotify.adapters
    i = inotify.adapters.InotifyTree('./')
    #i.add_watch('./') # TODO update for subdirectories
   
    # whenever the file is modified, update the pdf
    default_css = f'default.css'
    for access_type in file_reads(i, [filename,default_css]):

        # convert if the file has been modified
        if access_type != 'IN_MODIFY':
            continue
        print(filename, "has been modified")
        process_document(filename, pdf_filename, html_filename)

        # update pdf by sending the pdf viewer a SIGHUP
        # TODO will this method work for other pdf viewers?
        import signal
        os.kill(pdfviewer_subprocess.pid, signal.SIGHUP)


if __name__ == '__main__':
    main()
