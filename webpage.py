import os
import shutil

def index(visualization_dirs):
    outfile = open('index.html', 'wt')

    print(
    """
    <html>
    <head></head>
    <body>
    """, file=outfile)
    
    for d in visualization_dirs:
        print(f'<a href={d}/index.html> <img src={d}/thumbnail.png> </a>', file=outfile)

    print(
    """
    </body>
    </html>
    """, file=outfile)

    for d in visualization_dirs:
        # copy webpage template (possibly use template engine later)
        sdir = os.path.dirname(os.path.abspath(__file__))
        shutil.copyfile(os.path.join(sdir,'run_index.html'),
                        os.path.join(d,'index.html'))
