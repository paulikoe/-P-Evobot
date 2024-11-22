for filename in ../api/*.py
do
    pydoc -w $filename
done
