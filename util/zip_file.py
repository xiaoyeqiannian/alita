import os
from zipfile import ZipFile, ZIP_DEFLATED

def zip_dir(source_path, out_file, selected=[]):
    obj = ZipFile(out_file, "w", ZIP_DEFLATED)
    for root, dirs, files in os.walk(source_path):
        sub_path = root.replace(source_path,'')
        for item in files:
            file_path = os.path.join(sub_path, item)
            if selected and file_path not in selected:
                continue

            obj.write(os.path.join(root, item), os.path.join(sub_path, item))
    obj.close()


def unzip_file(zip_file, out):
    obj = ZipFile(zip_file, "r", ZIP_DEFLATED)
    for item in obj.namelist():
        obj.extract(item, out)