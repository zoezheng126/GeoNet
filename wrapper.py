import os
import shutil
import subprocess
from glob import glob
from tempfile import TemporaryDirectory

# From Haozhen
def process_once(in_path, geonet_dir, file_name):
    try:
        subprocess.run(["python3", "pygeonet_configure.py", "-dir", geonet_dir, "-n", file_name.replace(".tif", "")])
        subprocess.run(["python3", "pygeonet_prepare.py"])
        import pygeonet_prepare as Parameters
        geo_inputs = Parameters.demDataFilePath
        print(os.path.join(in_path, file_name), os.path.join(geo_inputs, file_name))
        shutil.copy(os.path.join(in_path, file_name), os.path.join(geo_inputs, file_name))
        subprocess.run(["python3", "pygeonet_nonlinear_filter.py"])
        subprocess.run(["python3", "pygeonet_slope_curvature.py"])
        subprocess.run(["python3", "pygeonet_grass_py3.py"])
        subprocess.run(["python3", "pygeonet_skeleton_definition.py"])
        subprocess.run(["python3", "pygeonet_fast_marching.py"])
        subprocess.run(["python3", "pygeonet_channel_head_definition.py"])

        geo_outputs = Parameters.geonetResultsDir
        out_path = os.path.join(in_path, file_name[:-4])
        os.makedirs(out_path, exist_ok=True)
        for fname in os.listdir(geo_outputs):
            shutil.move(os.path.join(geo_outputs, fname), os.path.join(out_path, fname))

        shutil.rmtree(geo_inputs)
        shutil.rmtree(geo_outputs)
    except Exception as e:
        print(f"Error processing file {file_name}\n{e}")


def main():
    print("Starting processing")
    data_path = '/projects/bbkc/danielz/ILHMP/2010s/DTM_ROI/Mackinaw_River_Stream_Order_Buffer'
    with TemporaryDirectory(dir="/tmp") as tmpdir:
        print(tmpdir)
        for foldername in os.listdir(data_path):
            in_path = os.path.join(data_path, foldername)
            for filename in os.listdir(in_path):
                process_once(in_path, tmpdir, filename)

    print("Finished processing all files.")


if __name__ == '__main__':
    main()
