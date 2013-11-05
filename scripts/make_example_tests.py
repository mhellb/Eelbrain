'''
Generate test scipt for example scripts

'''
import os

curdir = os.path.dirname(__file__)
test_dir = os.path.abspath(os.path.join(curdir, '..', 'eelbrain', 'tests'))
dst = os.path.join(test_dir, 'test_examples.py')
example_dir = os.path.abspath(os.path.join('..', 'examples'))

temp = """
def test_{i}():
    "Test {example_name}"
    path = os.path.join(examples_dir, {relpath!r})
    os.chdir(path)
    plot.configure_backend(False, False)
    execfile({filename!r})
    plt.close('all')
"""

intro = """# generated by eelbrain/scripts/make_example_tests.py
import os

from matplotlib import pyplot as plt

from eelbrain.lab import plot

dir_ = os.path.dirname(__file__)
examples_dir = os.path.join(dir_, '..', '..', 'examples')
examples_dir = os.path.abspath(examples_dir)

"""
parts = [intro]

i = 0
for dirpath, _, filenames in os.walk(example_dir):
    relpath = os.path.relpath(dirpath, example_dir)
    for filename in filenames:
        if filename.endswith('.py'):
            example_name = os.path.join(relpath, filename)
            text = temp.format(i=i, example_name=example_name, relpath=relpath,
                               filename=filename)
            parts.append(text)
            i += 1

text = ''.join(parts)
with open(dst, 'w') as fid:
    fid.write(text)

print "Done!"
