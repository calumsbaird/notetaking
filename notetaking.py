#!/usr/bin/env python3

# Track changes to a markdown file, convert markdown to a pdf
# display the pdf and update it consistently

#from __future__ import print_function
import os, sys

help_prompt = '''
usage: python3 notetaking.py file.md [flags]

Options and arguments:
-h  : print this help menu TODO
-d  : display debugging information TODO
-b  : run in background
'''

# Goes through inotify events and yield the ones with the correct 
# filename
def file_reads(i, filename_in_question):

    for event in i.event_gen(yield_nones=False):
        (_, type_names, path, filename) = event

        if filename_in_question == filename:
            #print("PATH=[{}] FILENAME=[{}] EVENT_TYPES={}".format(
            #      path, filename, type_names))   

            for access_type in type_names:
                yield access_type


def process_document(filename, pdf_filename, html_filename=None):

    # convert contents to html
    import markdown
    text = open(filename).read()
    html = markdown.markdown(text, extensions=['extra', 'codehilite', 'toc', 'markdown_katex'])

    if html_filename is not None:
        with open(html_filename,'w') as f:
            f.write(html)
   
    # convert contents to pdf
    from weasyprint import HTML, CSS
    HTML(string=html).write_pdf(pdf_filename,
    stylesheets=[CSS(string='body { font-family: serif !important }'), 'test.css'])

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def pdfviewer_handler(pdfviewer_subprocess):
    print('waiting')
    pdfviewer_subprocess.wait()
    print('done')
    import _thread
    _thread.interrupt_main() # TODO a more elegant solution would be nice but I cant find one
    

if __name__ == '__main__':

    # cmd args
    if len(sys.argv) < 2 or '-h' in sys.argv:
        print(help_prompt)
        sys.exit(1)

    filename = sys.argv[1]

    # run in background as daemon if '-b' flag
    if '-b' in sys.argv:

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
        import daemon
        daemon.createDaemon()

    # conjuer a filename for the pdf
    pdf_filename = 'test.pdf' #TODO
    html_filename = 'test.html'

    process_document(filename, pdf_filename, html_filename)
    
    
    # Open pdf
    import subprocess
    pdfviewer_subprocess = subprocess.Popen(['mupdf',pdf_filename])

    # Start a thread that will close the whole program when the
    # pdfviewer is closed
    import threading
    threading.Thread(target=pdfviewer_handler, args=(pdfviewer_subprocess,)).start()
    print("Here")

    # setup inotify in the current directory
    # TODO ideally we dont need to check the whole directory
    # but inotify is buggy for one file
    import inotify.adapters
    i = inotify.adapters.Inotify()
    i.add_watch('./') # TODO update for subdirectories
    
    for access_type in file_reads(i, filename):
        print(access_type)

        # convert if the file has been modified
        if access_type != 'IN_MODIFY':
            continue

        process_document(filename, pdf_filename)

        # update pdf 
        import signal
        os.kill(pdfviewer_subprocess.pid, signal.SIGHUP)
