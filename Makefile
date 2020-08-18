publish-test: build
	twine upload --repository testpypi dist/* -u __token__
build: dist/antibiotics-0.2-py3-none-any.whl  dist/antibiotics-0.2.tar.gz
doc: doc/antibiotics/index.html

dist/antibiotics-0.2-py3-none-any.whl  dist/antibiotics-0.2.tar.gz &: antibiotics/__init__.py setup.py
	python setup.py sdist bdist_wheel

doc/antibiotics/index.html: antibiotics/__init__.py
	pdoc --html --force -o doc antibiotics
