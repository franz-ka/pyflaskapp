rm *.zip
zip -r cogosys-$1.zip run.py flask1 utils -x \*\*/__pycache__/\* \*.pyc
