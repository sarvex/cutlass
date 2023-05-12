#################################################################################################
#
# Copyright (c) 2017 - 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
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

# test/unit/conv/device/conv2d_fprop_fixed_channels_f16nhwc_f16nhwc_f16nhwc_tensor_op_f32_sm80.cu
import cutlass.backend
from cutlass.backend import *
from cutlass.backend.test import *
from cutlass.backend.utils.device import device_cc
import unittest


@unittest.skipIf(device_cc() < 80, "Device compute capability is insufficient for SM80 tests.")
def conv2d_fixed_channel_problemsizes(channels):
    return [
        cutlass_bindings.conv.Conv2dProblemSize(
            cutlass_bindings.Tensor4DCoord(1, 8, 8, channels),
            cutlass_bindings.Tensor4DCoord(16, 3, 3, channels),
            cutlass_bindings.Tensor4DCoord(1, 1, 1, 1),
            cutlass_bindings.MatrixCoord(2, 2),
            cutlass_bindings.MatrixCoord(1, 1),
            cutlass_bindings.conv.Mode.cross_correlation,
            1,
            1,
        ),
        cutlass_bindings.conv.Conv2dProblemSize(
            cutlass_bindings.Tensor4DCoord(1, 224, 224, channels),
            cutlass_bindings.Tensor4DCoord(32, 7, 7, channels),
            cutlass_bindings.Tensor4DCoord(1, 1, 1, 1),
            cutlass_bindings.MatrixCoord(1, 1),
            cutlass_bindings.MatrixCoord(1, 1),
            cutlass_bindings.conv.Mode.cross_correlation,
            1,
            1,
        ),
        cutlass_bindings.conv.Conv2dProblemSize(
            cutlass_bindings.Tensor4DCoord(1, 224, 224, channels),
            cutlass_bindings.Tensor4DCoord(64, 7, 7, channels),
            cutlass_bindings.Tensor4DCoord(1, 1, 1, 1),
            cutlass_bindings.MatrixCoord(2, 2),
            cutlass_bindings.MatrixCoord(1, 1),
            cutlass_bindings.conv.Mode.cross_correlation,
            1,
            1,
        ),
        cutlass_bindings.conv.Conv2dProblemSize(
            cutlass_bindings.Tensor4DCoord(1, 224, 224, channels),
            cutlass_bindings.Tensor4DCoord(64, 5, 5, channels),
            cutlass_bindings.Tensor4DCoord(1, 1, 1, 1),
            cutlass_bindings.MatrixCoord(1, 1),
            cutlass_bindings.MatrixCoord(1, 1),
            cutlass_bindings.conv.Mode.cross_correlation,
            1,
            1,
        ),
        cutlass_bindings.conv.Conv2dProblemSize(
            cutlass_bindings.Tensor4DCoord(1, 224, 224, channels),
            cutlass_bindings.Tensor4DCoord(64, 5, 5, channels),
            cutlass_bindings.Tensor4DCoord(1, 1, 1, 1),
            cutlass_bindings.MatrixCoord(2, 2),
            cutlass_bindings.MatrixCoord(1, 1),
            cutlass_bindings.conv.Mode.cross_correlation,
            1,
            1,
        ),
    ]

class Conv2dFpropFixedChannelsF16NHWCF16NHWCF16HNWCTensorOpF32SM80(unittest.TestCase):
    def test_SM80_Device_Conv2d_Fprop_Fixed_Channels_ImplicitGemm_f16nhwc_f16nhwc_f16nhwc_tensor_op_f32_channels_8(self):
        math_inst = MathInstruction(
            instruction_shape=[16, 8, 16],
            element_a=cutlass_bindings.float16, element_b=cutlass_bindings.float16,
            element_accumulator=cutlass_bindings.float32, opcode_class=cutlass_bindings.OpClass.TensorOp,
            math_operation=MathOperation.multiply_add
        )

        A = TensorDescription(
            element=math_inst.element_a, 
            layout=cutlass_bindings.TensorNHWC,
            alignment=8)
        B = TensorDescription(
            element=math_inst.element_b, 
            layout=cutlass_bindings.TensorNHWC, 
            alignment=8)
        C = TensorDescription(
            element=cutlass_bindings.float16,
            layout=cutlass_bindings.TensorNHWC, 
            alignment=8)

        tile_description = TileDescription(
            threadblock_shape=[128, 128, 64], stages=3, 
            warp_count=[2, 2, 1],
            math_instruction=math_inst
        )

        epilogue_functor = LinearCombination(
            C.element, C.alignment, 
            math_inst.element_accumulator, cutlass_bindings.float32)

        operation = Conv2dOperation(
            conv_kind=cutlass_bindings.conv.Operator.fprop, iterator_algorithm=cutlass_bindings.conv.IteratorAlgorithm.fixed_channels,
            arch=80, tile_description=tile_description, A=A, B=B, C=C, 
            stride_support=StrideSupport.Strided,
            epilogue_functor=epilogue_functor,
            swizzling_functor=cutlass_bindings.IdentitySwizzle1
        )
        
        self.assertTrue(test_all_conv2d(operation, conv2d_fixed_channel_problemsizes(8)))
    
    def test_SM80_Device_Conv2d_Fprop_Fixed_Channels_ImplicitGemm_f16nhwc_f16nhwc_f16nhwc_tensor_op_f32_channels_4(self):
        math_inst = MathInstruction(
            instruction_shape=[16, 8, 16],
            element_a=cutlass_bindings.float16, element_b=cutlass_bindings.float16,
            element_accumulator=cutlass_bindings.float32, opcode_class=cutlass_bindings.OpClass.TensorOp,
            math_operation=MathOperation.multiply_add
        )

        A = TensorDescription(
            element=math_inst.element_a, 
            layout=cutlass_bindings.TensorNHWC,
            alignment=4)
        B = TensorDescription(
            element=math_inst.element_b, 
            layout=cutlass_bindings.TensorNHWC, 
            alignment=4)
        C = TensorDescription(
            element=cutlass_bindings.float16,
            layout=cutlass_bindings.TensorNHWC, 
            alignment=8)

        tile_description = TileDescription(
            threadblock_shape=[128, 128, 64], stages=3, 
            warp_count=[2, 2, 1],
            math_instruction=math_inst
        )

        epilogue_functor = LinearCombination(
            C.element, C.alignment, 
            math_inst.element_accumulator, cutlass_bindings.float32)

        operation = Conv2dOperation(
            conv_kind=cutlass_bindings.conv.Operator.fprop, iterator_algorithm=cutlass_bindings.conv.IteratorAlgorithm.fixed_channels,
            arch=80, tile_description=tile_description, A=A, B=B, C=C, 
            stride_support=StrideSupport.Strided,
            epilogue_functor=epilogue_functor,
            swizzling_functor=cutlass_bindings.IdentitySwizzle1
        )
        
        self.assertTrue(test_all_conv2d(operation, conv2d_fixed_channel_problemsizes(4)))
    
    def test_SM80_Device_Conv2d_Fprop_Fixed_Channels_ImplicitGemm_f16nhwc_f16nhwc_f16nhwc_tensor_op_f32_channels_2(self):
        math_inst = MathInstruction(
            instruction_shape=[16, 8, 16],
            element_a=cutlass_bindings.float16, element_b=cutlass_bindings.float16,
            element_accumulator=cutlass_bindings.float32, opcode_class=cutlass_bindings.OpClass.TensorOp,
            math_operation=MathOperation.multiply_add
        )

        A = TensorDescription(
            element=math_inst.element_a, 
            layout=cutlass_bindings.TensorNHWC,
            alignment=2)
        B = TensorDescription(
            element=math_inst.element_b, 
            layout=cutlass_bindings.TensorNHWC, 
            alignment=2)
        C = TensorDescription(
            element=cutlass_bindings.float16,
            layout=cutlass_bindings.TensorNHWC, 
            alignment=8)

        tile_description = TileDescription(
            threadblock_shape=[128, 128, 64], stages=3, 
            warp_count=[2, 2, 1],
            math_instruction=math_inst
        )

        epilogue_functor = LinearCombination(
            C.element, C.alignment, 
            math_inst.element_accumulator, cutlass_bindings.float32)

        operation = Conv2dOperation(
            conv_kind=cutlass_bindings.conv.Operator.fprop, iterator_algorithm=cutlass_bindings.conv.IteratorAlgorithm.fixed_channels,
            arch=80, tile_description=tile_description, A=A, B=B, C=C, 
            stride_support=StrideSupport.Strided,
            epilogue_functor=epilogue_functor,
            swizzling_functor=cutlass_bindings.IdentitySwizzle1
        )
        
        self.assertTrue(test_all_conv2d(operation, conv2d_fixed_channel_problemsizes(2)))


if __name__ == '__main__':
    cutlass.backend.get_memory_pool(2**26, 2**26)
    unittest.main()
