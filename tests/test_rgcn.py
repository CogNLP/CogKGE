import torch
from torch.utils.data import RandomSampler
from pathlib import Path
import sys
import numpy as np

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0].parents[0]  # CogKGE root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add CogKGE root directory to PATH

from cogkge import *

device = init_cogkge(device_id="4,5,6,7", seed=1)
loader = FB15KLoader(dataset_path="../dataset", download=True)

train_data, valid_data, test_data = loader.load_all_data()
node_lut, relation_lut = loader.load_all_lut()
# loader.describe()
# train_data.describe()
# node_lut.describe()

# processor = COGNET680KProcessor(node_lut, relation_lut)
processor = FB15KProcessor(node_lut, relation_lut, reprocess=True)
train_dataset = processor.process(train_data)
valid_dataset = processor.process(valid_data)
test_dataset = processor.process(test_data)
node_lut, relation_lut = processor.process_lut()
# node_lut.print_table(front=3)
# relation_lut.print_table(front=3)

train_sampler = RandomSampler(train_dataset)
valid_sampler = RandomSampler(valid_dataset)
test_sampler = RandomSampler(test_dataset)

edge_index, edge_type = construct_adj(train_dataset, relation_dict_len=len(relation_lut))

model = RGCN(edge_index=edge_index,
                edge_type=edge_type,
                entity_dict_len=len(node_lut),
                relation_dict_len=len(relation_lut),
                embedding_dim=200,
                )

# loss = MarginLoss(margin=1.0, C=0)

loss = NegLogLikehoodLoss(C=0.1)

optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=0)

metric = Link_Prediction(link_prediction_raw=True,
                         link_prediction_filt=False,
                         batch_size=50000,
                         reverse=True)


lr_scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode='min', patience=3, threshold_mode='abs', threshold=5,
    factor=0.5, min_lr=1e-9, verbose=True
)

negative_sampler = UnifNegativeSampler(triples=train_dataset,
                                       entity_dict_len=len(node_lut),
                                       relation_dict_len=len(relation_lut))

trainer = ScoreTrainer(
    train_dataset=train_dataset,
    valid_dataset=valid_dataset,
    train_sampler=train_sampler,
    valid_sampler=valid_sampler,
    model=model,
    loss=loss,
    optimizer=optimizer,
    negative_sampler=negative_sampler,
    device=device,
    output_path="../dataset",
    lookuptable_E=node_lut,
    lookuptable_R=relation_lut,
    metric=metric,
    lr_scheduler=lr_scheduler,
    log=True,
    trainer_batch_size=10000,
    epoch=1000,
    visualization=0,
    apex=True,
    dataloaderX=True,
    num_workers=4,
    pin_memory=True,
    metric_step=100,
    save_step=200,
    metric_final_model=True,
    save_final_model=True,
    load_checkpoint=None
)
trainer.train()

evaluator = Evaluator(
    test_dataset=test_dataset,
    test_sampler=test_sampler,
    model=model,
    device=device,
    metric=metric,
    output_path="../dataset",
    train_dataset=train_dataset,
    valid_dataset=valid_dataset,
    lookuptable_E=node_lut,
    lookuptable_R=relation_lut,
    log=True,
    evaluator_batch_size=500,
    dataloaderX=False,
    num_workers=4,
    pin_memory=True,
    trained_model_path=None
)
evaluator.evaluate()


