Install dependencies with `pip install -r requirements.txt`.

Run each of these:

```bash
mprof run save-gudhi.py ./datasets_mem_test/1
mprof run save-gudhi.py ./datasets_mem_test/2
mprof run save-gudhi.py ./datasets_mem_test/3
mprof run save-gudhi.py ./datasets_mem_test/4
mprof run save-gudhi.py ./datasets_mem_test/5
mprof run save-gudhi.py ./datasets_mem_test/6
```

Both 1 and 3 may crash your computer. Linux might kill it if you're using Linux.

You'll get the results of Gudhi in a pickle file, `<number>_output.pickle`.
`mprof` will also generate files. Will need some way to map them to what data, either move them into their own folder or rename.
