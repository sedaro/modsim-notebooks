source .venv/bin/activate
pip install --upgrade --force-reinstall sedaro matplotlib requests
for i in *.ipynb; do
    jupyter nbconvert --to python $i
    p="${i/.ipynb/.py}"
    echo "Running $p"
    python "$p"
    echo "Done"
done
deactivate
