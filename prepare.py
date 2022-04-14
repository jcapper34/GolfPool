# This script will be run to setup everything before the server starts
import os
import sass

WEB_DIR = 'web'


def compile_sass():
    for entry in os.scandir(WEB_DIR):
        if entry.is_dir():
            if entry.name == 'sass':
                sass_dir = os.path.join(WEB_DIR, 'sass')
                css_dir = os.path.join(WEB_DIR, 'static/css')
            else:
                sass_dir = os.path.join(WEB_DIR, entry.name, 'sass')
                css_dir = os.path.join(WEB_DIR, entry.name, 'static/css')

            if os.path.exists(sass_dir):
                if not os.path.exists(css_dir):
                    os.mkdir(css_dir)

                for sass_entry in os.scandir(sass_dir):
                    if sass_entry.is_file():
                        sass_filename = os.path.join(sass_dir, sass_entry.name)

                        css_out = sass.compile(filename=sass_filename,
                                               output_style='compressed', include_paths=["web/sass"])
                        css_filename = os.path.join(
                            css_dir, sass_entry.name.split(".")[0] + '.min.css')
                        with open(css_filename, 'w') as f:
                            f.write(css_out)
                            print("Compiled SASS into", css_filename)


if __name__ == "__main__":
    compile_sass()
