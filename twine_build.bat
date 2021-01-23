:: python -m pip install twine wheel

:: delete old dists
rmdir /s/q dist
rmdir /s/q build

:: creating the package
python setup.py bdist_wheel

:: test the dist via twine
python -m twine check dist/*.whl

:: uploading the dist via twine
set twine_url=
if %1x neq x set twine_url=--repository-url https://test.pypi.org/legacy/
python -m twine upload %twine_url% dist/*.whl
