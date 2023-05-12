#################################################################################################
#
# Copyright (c) 2023 - 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 'AS IS'
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#################################################################################################

import os
from setuptools import setup


def _cutlass_path_from_dir() -> str:
    cutlass_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../')
    if not os.path.isdir(cutlass_path):
        raise Exception(f'Environment variable "CUTLASS_PATH" is not defined, and default path of {cutlass_path} does not exist.')
    return cutlass_path


def _cuda_install_path_from_nvcc() -> str:
    import subprocess
    # Attempt to detect CUDA_INSTALL_PATH based on location of NVCC
    result = subprocess.run(['which', 'nvcc'], capture_output=True)
    if result.returncode != 0:
        raise Exception('Unable to find nvcc via `which` utility.')

    cuda_install_path = result.stdout.decode('utf-8').split('/bin/nvcc')[0]
    if not os.path.isdir(cuda_install_path):
        raise Exception(f'Environment variable "CUDA_INSTALL_PATH" is not defined, and default path of {cuda_install_path} does not exist.')

    return cuda_install_path


cutlass_path = (
    os.getenv('CUTLASS_PATH')
    if os.getenv('CUTLASS_PATH') is not None
    else _cutlass_path_from_dir()
)

cuda_install_path = (
    os.getenv('CUDA_INSTALL_PATH')
    if os.getenv('CUDA_INSTALL_PATH') is not None
    else _cuda_install_path_from_nvcc()
)

ext_modules = []

try:
    from pybind11.setup_helpers import Pybind11Extension, build_ext
    include_dirs = [
        f'{cutlass_path}/include',
        f'{cuda_install_path}/include',
        f'{cutlass_path}/tools/util/include',
        f'{cutlass_path}/test',
    ]

    ext_modules = [
        Pybind11Extension('cutlass_bindings',
                          ['cutlass/cpp/cutlass_bindings.cpp'],
                          include_dirs=include_dirs,
                          extra_compile_args=['-fpermissive', '-w', '-std=c++17', '-DCUTLASS_PYTHON_HOST_CC=1'])
    ]
except ImportError:
    pass


setup(
    name='cutlass',
    version='3.1.0',
    description='CUTLASS Pythonic Interface',
    package_dir={'': '.'},
    packages=['cutlass', 'cutlass.emit', 'cutlass.op', 'cutlass.utils', 'cutlass.backend', 'cutlass.backend.utils'],
    setup_requires=['pybind11'],
    install_requires=[
        'bfloat16',
        'cuda-python>=11.8.0',
        'pybind11',
        'scikit-build',
        'treelib'
        ],
    ext_modules=ext_modules,
)
