import os
import numpy as np
import onnxruntime as ort

class OnnxInferenceModel:
    """ Base class for all inference models that use onnxruntime 

    Attributes:
        model_path (str, optional): Path to the model folder. Defaults to "".
        force_cpu (bool, optional): Force the model to run on CPU or GPU. Defaults to GPU.
        default_model_name (str, optional): Default model name. Defaults to "model.onnx".
    """
    def __init__(
        self, 
        model_path: str = "",
        force_cpu: bool = False,
        default_model_name: str = "model.onnx",
        *args, **kwargs
        ):
        
        self.model_path = model_path
        self.force_cpu = force_cpu
        self.default_model_name = default_model_name

        # check if model path is a directory with os path
        if os.path.isdir(self.model_path):
            self.model_path = os.path.join(self.model_path, self.default_model_name)

        if not os.path.exists(self.model_path):
            raise Exception(f"Model path ({self.model_path}) does not exist")

        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"] if ort.get_device() == "GPU" and not force_cpu else ["CPUExecutionProvider"]

        self.model = ort.InferenceSession(self.model_path, providers=providers)

        self.metadata = {}
        if self.model.get_modelmeta().custom_metadata_map:
            # add metadata to self object
            for key, value in self.model.get_modelmeta().custom_metadata_map.items():
                try:
                    new_value = eval(value) # in case the value is a list or dict
                except:
                    new_value = value
                self.metadata[key] = new_value
                
        # Update providers priority to only CPUExecutionProvider
        if self.force_cpu:
            self.model.set_providers(["CPUExecutionProvider"])

        self.input_shape = self.model.get_inputs()[0].shape[1:]
        self.input_name = self.model._inputs_meta[0].name
        self.output_name = self.model._outputs_meta[0].name

    def predict(self, data: np.ndarray):
        raise NotImplementedError

    def __call__(self, data: np.ndarray):
        return self.predict(data)