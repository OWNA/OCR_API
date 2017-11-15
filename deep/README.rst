To select the fonts for use in the deep trainer:

    python -m deep.paint


Tensorflow How to
-----------------

To create the TFRecords required to train the model:

    python -m deep.generate


To train the tensorflow model:

    python -m deep.ctcrnn.train

To evaluate the tensorflow model:

    python -m deep.evaluate


Keras How to
------------

To run the deep OCR training:

    python -m deep.legacy.runner
    gdb -ex r --args python -m deep.legacy.runner  # To debug segfaults


To evaluate the deep OCR training from a saved model file:

    python -m deep.legacy.evaluate


Nividia troubleshoot
--------------------

Make sure the following is installed:

    nvcc --version
    Cuda compilation tools, release 8.0, V8.0.26

    nvidia-smi
    NVIDIA-SMI 375.66 Driver Version: 375.66x

    cat /proc/driver/nvidia/version
    NVRM version: NVIDIA UNIX x86_64 Kernel Module 375.66
    GCC version:  gcc version 4.9.3
