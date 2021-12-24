import os
import torch
import random
import numpy as np
from torch.utils.data import RandomSampler

from cogktr import *

class Init_CogKTR():
    def __init__(self,seed,device_id,data_path,model_name):
        self.seed=seed
        self.device_id=device_id
        self.data_path=data_path
        self.model_name=model_name
    def _init_seed(self):
        random.seed(self.seed)
        np.random.seed(self.seed)
        torch.manual_seed(self.seed)
        torch.cuda.manual_seed_all(self.seed)
    def _init_device(self):
        device_list=str(self.device_id).strip().lower().replace('cuda:', '')
        cpu = device_list == 'cpu'
        if cpu:
            os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # force torch.cuda.is_available() = False
        elif device_list:  # non-cpu device requested
            os.environ['CUDA_VISIBLE_DEVICES'] = device_list  # set environment variable
            assert torch.cuda.is_available(), f'CUDA unavailable, invalid device {device_list} requested'  # check availability
        self.device = torch.device('cuda:0' if torch.cuda.is_available() == True else "cpu")
    def _init_output_path(self):
        output_path = cal_output_path(self.data_path, self.model_name)
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        self.output_path =output_path
    def _init_logger(self):
        logger = save_logger(os.path.join(self.output_path, "run.log"))
        logger.info("Data Path:{}".format(self.data_path))
        logger.info("Output Path:{}".format(self.output_path))
        self.logger=logger
    def start(self):
        self._init_seed()
        self._init_device()
        self._init_output_path()
        self._init_logger()
    def get_device(self):
        return self.device
    def get_output_path(self):
        return self.output_path
    def get_logger(self):
        return self.logger




init=Init_CogKTR(seed=1,
                 device_id="7",
                 data_path="../dataset/kr/FB15K/raw_data",
                 model_name="TransE")
init.start()
device=init.get_device()
output_path=init.get_output_path()
logger=init.get_logger()

loader = FB15KLoader(path="../dataset/kr/FB15K/raw_data",
                     download=True,
                     download_path="Research_code/CogKTR/dataset")
train_data, valid_data, test_data = loader.load_all_data()
node_lut, relation_lut = loader.load_all_lut()

processor = FB15KProcessor(node_lut, relation_lut)
train_dataset = processor.process(train_data)
valid_dataset = processor.process(valid_data)
test_dataset = processor.process(test_data)

train_sampler = RandomSampler(train_dataset)
valid_sampler = RandomSampler(valid_dataset)
test_sampler = RandomSampler(test_dataset)

model = TransE(entity_dict_len=len(node_lut),
               relation_dict_len=len(relation_lut),
               embedding_dim=50)

loss = MarginLoss(margin=1.0,C=0)

optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=0)

metric = Link_Prediction(link_prediction_raw=True,
                         link_prediction_filt=True,
                         batch_size=2000000,
                         reverse=False)

lr_scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode='min', patience=3, threshold_mode='abs', threshold=5,
    factor=0.5, min_lr=1e-9, verbose=True
)

negative_sampler = UnifNegativeSampler(triples=train_dataset,
                                       entity_dict_len=len(node_lut),
                                       relation_dict_len=len(relation_lut))


trainer = Kr_Trainer(
    train_dataset=train_dataset,
    valid_dataset=valid_dataset,
    train_sampler=train_sampler,
    valid_sampler=valid_sampler,
    model=model,
    loss=loss,
    optimizer=optimizer,
    negative_sampler=negative_sampler,
    device=device,
    output_path=output_path,
    lookuptable_E= node_lut,
    lookuptable_R= relation_lut,
    metric=metric,
    lr_scheduler=lr_scheduler,
    logger=logger,
    trainer_batch_size=50000,
    epoch=1000,
    visualization=0,
    apex=True,
    dataloaderX=True,
    num_workers=4,
    pin_memory=True,
    metric_step=2000,
    save_step=100,
    metric_final_model=True,
    save_final_model=False,
    load_checkpoint= None
)
trainer.train()

evaluator = Kr_Evaluator(
    test_dataset=test_dataset,
    test_sampler=test_sampler,
    model=model,
    device=device,
    metric=metric,
    output_path=output_path,
    train_dataset=train_dataset,
    valid_dataset=valid_dataset,
    lookuptable_E= node_lut,
    lookuptable_R= relation_lut,
    logger=logger,
    evaluator_batch_size=50000,
    dataloaderX=True,
    num_workers= 4,
    pin_memory=True,
    trained_model_path=None
)
evaluator.evaluate()

print("end")