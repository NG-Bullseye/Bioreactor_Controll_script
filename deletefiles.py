from pathlib import Path

pathlist = Path("").glob('**/*.*')

for path in pathlist:
     # because path is object not string
     path_in_str = str(path)
     # print(path_in_str)