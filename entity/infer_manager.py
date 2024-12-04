import numpy as np
import pycuda.driver as cuda
import pycuda.autoinit
import tensorrt as trt

TRT_LOGGER = trt.Logger(trt.Logger.WARNING)

class TrtInferManager():
    def __init__(self, engine_path):
        with open(engine_path, 'rb') as f, trt.Runtime(TRT_LOGGER) as runtime:
            self.engine = runtime.deserialize_cuda_engine(f.read())
            self.context = self.engine.create_execution_context()

        # Setup I/O bindings
        self.inputs = []
        self.outputs = []
        self.allocations = []
        for i in range(self.engine.num_io_tensors):
            name = self.engine.get_tensor_name(i)
            is_input = False
            if self.engine.get_tensor_mode(name) == trt.TensorIOMode.INPUT:
                is_input = True
            dtype = self.engine.get_tensor_dtype(name)
            shape = self.engine.get_tensor_shape(name)
            
            if is_input:
                self.batch_size = shape[0]

            size = np.prod(shape) * np.dtype(trt.nptype(dtype)).itemsize

            allocation = cuda.mem_alloc(int(size))
            binding = {
                "index": i,
                "name": name,
                "dtype": np.dtype(trt.nptype(dtype)),
                "shape": list(shape),
                "allocation": allocation,
            }
            self.allocations.append(allocation)
            if is_input:
                self.inputs.append(binding)
            else:
                self.outputs.append(binding)

        assert self.batch_size > 0
        assert len(self.inputs) > 0
        assert len(self.outputs) > 0
        assert len(self.allocations) > 0

    # 로드된 엔진으로 추론 실행
    def infer(self, input_data):
        # 입력 텐서에 데이터 복사
        for input_binding, input_tensor in zip(self.inputs, input_data):
            cuda.memcpy_htod(input_binding['allocation'], input_tensor)
        # 출력 텐서 준비
        bindings = [input_binding['allocation'] for input_binding in self.inputs] + \
                   [output_binding['allocation'] for output_binding in self.outputs]
        
        self.context.execute_v2(bindings)

        # 출력값 가져오기
        output_data = []
        for output_binding in self.outputs:
            output_tensor = np.empty(output_binding['shape'], dtype=output_binding['dtype'])
            cuda.memcpy_dtoh(output_tensor, output_binding['allocation'])
            output_data.append(output_tensor)
        
        return output_data

if __name__ == '__main__':
    # 추론 예제
    engine_path = 'models/best.trt'
    tim = TrtInferManager(engine_path)

    input_data = np.random.randn(1, 3, 256, 192).astype(np.float32)
    output = tim.infer(input_data)

    from scipy.special import softmax
    print(output[0].shape, softmax(output[1], axis=1).round(3))