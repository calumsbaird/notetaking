#!/usr/bin/env python3

# Track changes to a markdown file, convert markdown to a pdf
# display the pdf and update it consistently

#from __future__ import print_function
import os, sys
import requests, logging, base64

# Current version
import pkg_resources  # part of setuptools
package_information = pkg_resources.require("notetaking")[0]
VERSION = package_information.version

#import markdown_katex
#markdown_katex.html.HTML_TEMPLATE = markdown_katex.html.HTML_TEMPLATE.replace(markdown_katex.html._STYLESHEET_LINK, f'{os.path.dirname(os.path.abspath(__file__))}/css/katex.css')

help_prompt = f'''
notetaking {VERSION}
usage: python3 notetaking.py <filename> [flags]

Options and arguments:
-h,--help       : print this help menu
-d              : display debugging information TODO
-b,--background : run in background
--version       : print version number
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

import weasyprint
def url_fetcher(url):

    if url == 'https://cdn.jsdelivr.net/npm/katex@0.12.0/dist/katex.min.css':
        path = f'file://{os.path.dirname(os.path.abspath(__file__))}/css/katex.css'
        return weasyprint.default_url_fetcher(path)
    elif url.startswith('font:'):
        font_file = url.split('font:')[1]  
        font_path = f'file://{os.path.dirname(os.path.abspath(__file__))}/fonts/{font_file}'
        print('fetching font from:', font_path)
        return weasyprint.default_url_fetcher(font_path)

    # If its a web font, download it and cache
    elif url.startswith('http'):

        # Get the suffix of the file
        try:
            suffix = '.' + url.split('.')[-1]
        except:
            suffix = ''

        # Encode rest of path in base64
        url_base64 = str(base64.b64encode(url.encode("utf-8")),"utf-8")

        # Cache in /tmp
        #font_filename = f'{os.path.dirname(os.path.abspath(__file__))}/fonts/{url_base64}.css'
        file_path = f'/tmp/{url_base64}{suffix}'
        file_url = f'file://{file_path}'
        if not os.path.exists(file_path):
            print('downloading and caching url')
            file_contents = requests.get(url).content
            open(file_path, 'wb').write(file_contents) 
        else:
            print('using cached url')
        return weasyprint.default_url_fetcher(file_url)

    return weasyprint.default_url_fetcher(url)


def process_document(filename, pdf_filename, html_filename=None):

    # check file exists
    if not os.path.isfile(filename):
        open(filename,'a').close()

    # convert contents to html
    import markdown
    text = open(filename).read()
    md = markdown.Markdown( 
        extensions=['extra', 'codehilite', 'toc', 'markdown_katex'],
        extension_config= {
            'codehilite': {'guess_lang': True},
            'markdown_katex': {
                'no_inline_svg': True,      # should be true for WeasyPrint
                'insert_fonts_css': True,
            },
        }
    )
    html = md.convert(text)

    if html_filename is not None:
        with open(html_filename,'w') as f:
            f.write(html)
   
    # convert contents to pdf
    default_css = f'{os.path.dirname(os.path.abspath(__file__))}/css/default.css'
    from weasyprint import HTML, CSS
    from weasyprint.fonts import FontConfiguration
    font_config = FontConfiguration()
    css = CSS(default_css, font_config=font_config, url_fetcher=url_fetcher)
    HTML(string=html,base_url=os.getcwd(),url_fetcher=url_fetcher).write_pdf(pdf_filename,
    stylesheets=[css], font_config=font_config)



def pdfviewer_handler(pdfviewer_subprocess):
    print('waiting')
    pdfviewer_subprocess.wait()
    print('done')
    import _thread
    _thread.interrupt_main() # TODO a more elegant solution would be nice but I cant find one
    


def main():

    # help prompt
    # TODO separate cmd parsing function
    if len(sys.argv) < 2 or '-h' in sys.argv or '--help' in sys.argv:
        print(help_prompt)
        sys.exit(1)

    # version prompt
    if '--version' in sys.argv:
        print(f'notetaking {VERSION}')
        sys.exit(0)

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

    # TODO make logging better
    import logging
    logger = logging.getLogger('weasyprint')
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

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
    #u = url_fetcher('https://cdn.jsdelivr.net/npm/katex@0.12.0/dist/katex.min.css') 
    main()
