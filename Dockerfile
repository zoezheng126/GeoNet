FROM mundialis/grass-py3-pdal:7.8.7-debian

RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install --upgrade Pillow && \
    apt-get update && \
    pip3 install six && \
    pip3 install rasterio && \
    pip3 install numpy && \
    pip3 install matplotlib && \
    pip3 install scipy && \
    pip3 install statsmodels && \
    pip3 install numba && \
    pip3 install psutil && \
    pip3 install dask && \
    pip3 install distributed && \
    git clone https://github.com/scikit-fmm/scikit-fmm.git && \
    cd scikit-fmm && \
    python3 setup.py install

