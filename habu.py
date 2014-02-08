#!/usr/bin/env python
# Copyright (C) 2014 Claudio "nex" Guarnieri.
# This file is part of Habu - https://github.com/botherder/habu
# See the file 'LICENSE' for copying permission.

# Big up for @ochsff for allowing me to rip off part of his code.

import os
import re
import sys
import time
import shutil
import argparse

def color(text, color_code):
    if sys.platform == "win32":
        return text

    return chr(0x1b) + "[" + str(color_code) + "m" + text + chr(0x1b) + "[0m"

def red(text):
    return color(text, 31)

def green(text):
    return color(text, 32)

def yellow(text):
    return color(text, 33)

def bold(text):
    return color(text, 1)

try:
    import yaml
    from markdown import Markdown
    from markdown.preprocessors import Preprocessor
    from jinja2.loaders import FileSystemLoader
    from jinja2.environment import Environment
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import get_lexer_by_name, TextLexer
except ImportError as e:
    print(red("Unable to import dependency:") + str(e))
    sys.exit(-1)

class CodeBlockPreprocessor(Preprocessor):
    """This converts code blocks into highlighted code.
    Neat stuff."""
    # Compile regexp, matching [code][/code] blocks.
    pattern = re.compile(r"\[code:(.+?)\](.+?)\[/code\]", re.S)
    # Add style formatter.
    formatter = HtmlFormatter(noclasses=True, cssclass="colorful")

    def run(self, lines):
        def repl(m):
            try:
                lexer = get_lexer_by_name(m.group(1))
            except ValueError:
                lexer = TextLexer()

            code = highlight(m.group(2), lexer, self.formatter)
            return "\n{0}\n".format(code)

        return [self.pattern.sub(repl, "\n".join(lines))]

def generate_static(destination):
    """Copy over static files to the destination.
    Generally includes JavaScript, CSS, pictures, etc.
    """
    # Check if there is a local static folder to copy over to destination.
    if not os.path.exists("static"):
        print("Unable to find local static folder... " + red("abort"))
        return

    print("Installing static folder to destination..."),

    # Loop through every entry in the local static folder.
    for entry in os.listdir("static"):
        orig = os.path.join("static", entry)
        dest = os.path.join(destination, entry)

        # If the destination folder/file already exists, we delete it and
        # rewrite everything again.
        if os.path.exists(dest):
            if os.path.isfile(dest):
                os.remove(dest)
            else:
                shutil.rmtree(dest)

        try:
            # If the current entry is a file, copy that alone.
            if os.path.isfile(orig):
                shutil.copy(orig, dest)
            # If it's a directory, copy it recursively.
            else:
                shutil.copytree(orig, dest)
        except Exception as e:
            print("hmm")
            continue

    print(green("done"))

def generate_pages(destination):
    """Generate static pages.
    """
    # Check if the pages folder exists.
    if not os.path.exists("pages"):
        print("Unable to find pages folder..." + red("abort"))
        return

    # Load template engine.
    env = Environment()
    # Load all files from the pages folder and from the template
    # folder, to get the skeleton and the content.
    env.loader = FileSystemLoader(["pages", "template"])

    # Loop through all static pages.
    for page in os.listdir("pages"):
        dest = os.path.join(destination, page)
        print("Generating page {0}...".format(dest)),

        # Load the template for the current page.
        template = env.get_template(page)
        # Generate the HTML output for the static page.
        html = template.render({"page" : page})
        # Write the HTML to the destination file.
        with open(dest, "w") as handle:
            handle.write(html)

        print(green("done"))

def generate_posts(destination):
    """Generate dynamic blog posts.
    """
    # Check if the posts folder exists.
    if not os.path.exists("posts"):
        print("Unable to find posts folder..." + red("abort"))
        return

    posts = []

    # Load template engine.
    env = Environment()
    # Load the template files, base and post.
    env.loader = FileSystemLoader("template")

    for post in os.listdir("posts"):
        orig = os.path.join("posts", post)

        if os.path.isdir(orig):
            print("Entry \"{0}\" is a directory, {1}".format(post, yellow("skip")))
            continue

        print("Processing \"{0}\"...".format(orig)),

        # Read the raw content of the blog post.
        raw = open(orig, "r").read()
        # Split headers and content, they're separated by the first
        # empty line.
        headers, content = raw.split("\n\n", 1)
        # Load YAML headers.
        headers = yaml.load(headers)
        # Initialize Markdown processor.
        md = Markdown()
        # Add the source code pre-processor.
        md.preprocessors.add("sourcecode", CodeBlockPreprocessor(), "_begin")
        # Generate the HTML conversion of the original Markdown content.
        content = md.convert(content)

        print(green("done"))

        # If the user specified a date use it, otherwise generate it.
        if headers.has_key("Date"):
            date = headers["Date"]
        else:
            date = time.strftime("%Y-%m-%d %H:%M:%S")

        # Generate post descriptor.
        post_object = dict(
            date=date,
            title=headers["Title"],
            slug=headers["Slug"],
            author=headers["Author"],
            content=content,
            link=None
        )

        # This is where we're going to generate the final HTML blog post.
        file_name = "{0}-{1}.html".format(str(post_object["date"])[:10], post_object["slug"])
        dest = os.path.join(destination, file_name)

        # If the blog post already exists, delete it.
        if not os.path.exists(dest):
            print("Generating HTML blog post at \"{0}\"...".format(dest)),

            # Load basic blog post template.
            template = env.get_template("post.html")
            # Generate the HTML content.
            html = template.render(**post_object)
            # Create the HTML file.
            with open(dest, "w") as handle:
                handle.write(html)

            print(green("done"))
        else:
            print("Post already exists, delete manually if needed... " + yellow("skip"))

        # Add the new file name to the post object.
        post_object["link"] = file_name

        # Add the generated post to the overall list.
        posts.append(post_object)

    # Order blog posts from recent to older.
    posts.sort(key=lambda key: key["date"])
    posts.reverse()

    return posts

def generate_index(posts, destination):
    """This generate the index page with the list of blog posts.
    """
    dest = os.path.join(destination, "index.html")

    print("Generating blog index..."),

    # Load template engine.
    env = Environment()
    # Load the template files, base and post.
    env.loader = FileSystemLoader("template")
    # Load template file.
    tpl = env.get_template("index.html")
    # Generate HTML content.
    first = posts.pop(0)
    html = tpl.render({"page" : "index", "first" : first, "posts" : posts})

    # Create file.
    with open(dest, "w") as handle:
        handle.write(html)

    print(green("done"))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--static", help="Install static files", action="store_true", default=False)
    parser.add_argument("-p", "--pages", help="Generate static pages", action="store_true", default=False)
    parser.add_argument("-d", "--destination", help="Specify the destination folder where to install the files", required=True)
    args = parser.parse_args()

    if not os.path.exists(args.destination):
        print("The destination folder does not exist, create it... " + red("abort"))
        return

    # If requested to do so, generate static pages.
    if args.pages:
        generate_pages(args.destination)

    # If requested to do so, install static files.
    if args.static:
        generate_static(args.destination)

    # Generate dynamic blog posts.
    posts = generate_posts(args.destination)
    generate_index(posts, args.destination)

if __name__ == "__main__":
    main()
