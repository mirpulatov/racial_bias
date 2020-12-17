import onnxruntime as ort

class VectorExtractor:
    def __init__(self, model_path):
        self.ort_session = ort.InferenceSession(model_path)
        self.input_name = self.ort_session.get_inputs()[0].name
        self.output_name = self.ort_session.get_outputs()[0].name

    def process(self, img):
        return self.ort_session.run(None, {self.input_name: img})
# red_onx = sess.run([out.name], {inp.name: X_test_dict})[0]