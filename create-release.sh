rm *.zip
zip -r cogosys-$1.zip flask1 utils -x \*\*/__pycache__/\* \*.pyc
