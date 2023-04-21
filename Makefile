build: dist/antibiotics-0.4-py3-none-any.whl dist/antibiotics-0.4.tar.gz

check:
	mypy --strict setup.py antibiotics examples

publish: build
	twine upload dist/* -u __token__

publish-test: build
	twine upload --repository testpypi dist/* -u __token__

doc: doc/antibiotics/index.html

clean:
	-rm doc/*
	-rm dist/*

dist/antibiotics-0.4-py3-none-any.whl dist/antibiotics-0.4.tar.gz &: antibiotics/__init__.py setup.py
	python setup.py sdist bdist_wheel

doc/antibiotics/index.html: antibiotics/__init__.py
	pdoc -o doc antibiotics

.PHONY: build check publish publish-test doc clean
