
if [ ! -d test ]; then
    echo test directory does not exist
    exit 1
fi

echo Running tests in Python 2
PYTHONPATH=${PYTHONPATH}:${PWD}/src python2 -m unittest discover test/

echo Running tests in Python 3
PYTHONPATH=${PYTHONPATH}:${PWD}/src python3.3 -m unittest discover test/
