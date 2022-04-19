import os
import shutil
from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader("webpage"),
    # searches in "templates/" directory next to the webpage module (this file)
    # autoescape=select_autoescape()
)
template = env.get_template("index.html.template")

def index(experiment_dir, visualization_dirs):
    """
    Create an index page with thumbnails that link to the individual runs.

    Ideally the paths in the web page are relative to the index file itself
    so that the webpage can be re-located.   
    """
    outfile = open(os.path.join(experiment_dir, 'index.html'), 'wt')

    print(
    """
    <html>
    <head></head>
    <body>
    """, file=outfile)
    
    for d,params in visualization_dirs:
        d = os.path.relpath(d, start=experiment_dir) # convert to a relative path
        print(f'<a href={d}/index.html> <img src={d}/thumbnail.png> </a>', file=outfile)

    print(
    """
    </body>
    </html>
    """, file=outfile)

    for d,run in visualization_dirs:
        # copy webpage template (possibly use template engine later)
        #sdir = os.path.dirname(os.path.abspath(__file__))
        #shutil.copyfile(os.path.join(sdir,'run_index.html'),
        #               os.path.join(d,'index.html'))
        dest = os.path.join(d,'index.html')
        outfile = open(dest, 'wt')
        print(template.render(params=run), file=outfile)
