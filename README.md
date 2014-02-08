Habu
====

Welcome to Habu.

Habu is likely the simplest static blog generator you'll encounter, no bullshit.
If you're techie enough and need a simple page to publish your work and if you share
my disgust and terror for blog platforms with massive codebases and my repulsion for
all those byzantine Ruby static generators, you might find this little tool of some use.

Firstly, you can install all the required dependencies with:

    pip install Jinja2 Markdown Pygments PyYAML

Now just download and extract Habu somewhere, you'll find the main script `habu.py` with
the following available command line options:

    usage: habu.py [-h] [-s] [-p] -d DESTINATION

    optional arguments:
      -h, --help            show this help message and exit
      -s, --static          Install static files
      -p, --pages           Generate static pages
      -d DESTINATION, --destination DESTINATION
                            Specify the destination folder where to install the
                            files

You simply need to execute `python habu.py -d /path/to/dest` and the 
script will automatically process the available blog posts and generate the
resulting HTML pages in the destination folder.

By providing the options `--static` or `--pages` you instruct Habu to
respectively install the static files (CSS, JavaScript and so on) and generate
the static pages.

All available blog posts are stored in the *posts/* directory and they consist
in a set of YAML headers followed by the body, separated by an empty line:

    Title: Blog Post
    Slug: blog-post
    Data: 1971-01-01 00:00:00

    Blog post content.

The blog post content can be defined with the popular [Markdown](https://daringfireball.net/projects/markdown/)
syntax, which makes the editing very easy and flexible, or with pure HTML.

Habu also integrates a [Pygments](http://pygments.org/) based pre-processor, which will highlight
code blocks according to the specified programming language.

This is pretty much it for now.

Enjoy.
