source .venv/bin/activate
pip install --upgrade --force-reinstall sedaro matplotlib
for i in *.ipynb; do
    jupyter nbconvert --to python $i
    p="${i/.ipynb/.py}"
    echo "Running $p"
    python "$p"
    if [ $? -ne 0 ]; then
        echo "Failed"
        break
    fi
    echo "Done"
done
deactivate
