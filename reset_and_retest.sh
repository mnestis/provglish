killall java
pip uninstall provglish
nosetests --with-coverage --cover-package=provglish
pip install .
