from setuptools import setup, find_packages
from torch.utils import cpp_extension
from torch.utils.cpp_extension import BuildExtension, CUDAExtension
from torch.cuda import is_available as torch_cuda_available
from pathlib import Path
import subprocess

def _get_cuda_bare_metal_version(cuda_dir):
    raw_output = subprocess.check_output([cuda_dir + "/bin/nvcc", "-V"],
                                         universal_newlines=True)
    output = raw_output.split()
    release_idx = output.index("release") + 1
    release = output[release_idx].split(".")
    bare_metal_major = release[0]
    bare_metal_minor = release[1][0]

    return raw_output, bare_metal_major, bare_metal_minor

srcpath = Path(__file__).parent.absolute()
cc_flag = []
_, bare_metal_major, _ = _get_cuda_bare_metal_version(
    cpp_extension.CUDA_HOME)

nvcc_flags = ['-O3', '--use_fast_math', '-U__CUDA_NO_HALF_OPERATORS__', '-U__CUDA_NO_HALF_CONVERSIONS__',
              '--expt-relaxed-constexpr', '--expt-extended-lambda']
cuda_ext_args = {'cxx': ['-O3'],
            'nvcc': nvcc_flags + cc_flag
        }
layernorm_cuda_args = {'cxx': ['-O3'],
            'nvcc': nvcc_flags + cc_flag + ['-maxrregcount=50']
        }
setup(
    name='fused_kernels',
    version='0.0.1',
    author="Sid Black & Alejandro Molina et al.",
    author_email="alejandro.molina@aleph-alpha.de",
    include_package_data=False,
    ext_modules=[
        CUDAExtension('scaled_upper_triang_masked_softmax_cuda', [str(srcpath / 'scaled_upper_triang_masked_softmax.cpp'), str(srcpath / 'scaled_upper_triang_masked_softmax_cuda.cu')],  
                      extra_compile_args=cuda_ext_args),
        CUDAExtension('scaled_masked_softmax_cuda', [str(srcpath / 'scaled_masked_softmax.cpp'), str(srcpath / 'scaled_masked_softmax_cuda.cu')],  
                      extra_compile_args=cuda_ext_args),
        CUDAExtension('fused_mix_prec_layer_norm_cuda', [str(srcpath / 'layer_norm_cuda.cpp'), str(srcpath / 'layer_norm_cuda_kernel.cu')],  
                      extra_compile_args=layernorm_cuda_args)
    ] if torch_cuda_available() else [],
    cmdclass={
        'build_ext': BuildExtension
    })
