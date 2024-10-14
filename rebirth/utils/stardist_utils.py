# utilities for loading and using a stardist model

from stardist.models import StarDist2D
from csbdeep.utils import normalize
import pathlib
from tqdm import tqdm

class stardist():

    '''
    Class wrapper for a stardist model,     
    '''

    def __init__(self, modelpath):
        path = pathlib.Path(modelpath)
        self._model = StarDist2D(None, path.name, str(path.parent))
        self.prob_threshold: float = self._model.thresholds.prob
        self.nms_threshold: float = self._model.thresholds.nms
    
    def detect(self, batch):
        detections_list = []
        data_list = []
        for image in tqdm(batch):
            segmentation, data = self._model.predict_instances(image, prob_thresh=self.prob_threshold, nms_thresh=self.nms_threshold, predict_kwargs={"verbose": 0})
            detections_list.append(segmentation)
            data_list.append(data)
        return detections_list, data_list
