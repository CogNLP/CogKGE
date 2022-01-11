import torch
from torch.utils.data import RandomSampler
from cogktr import *

device=init_cogktr(device_id="0,1,2,3",seed=1)

loader =CSKGLoader(dataset_path="../dataset",download=True)
train_data, valid_data, test_data = loader.load_all_data()
node_lut, relation_lut = loader.load_all_lut()
# loader.descrDibe()
# train_data.describe()
# node_lut.describe()

processor = CSKGProcessor(node_lut, relation_lut)
train_dataset = processor.process(train_data)
valid_dataset = processor.process(valid_data)
test_dataset = processor.process(test_data)

# node_lut.print_table(front=3)
# relation_lut.print_table(front=3)

train_sampler = RandomSampler(train_dataset)
valid_sampler = RandomSampler(valid_dataset)
test_sampler = RandomSampler(test_dataset)

model = TTD_TransE(entity_dict_len=len(node_lut),
            relation_dict_len=len(relation_lut),
            embedding_dim=20)

loss = MarginLoss(margin=1.0,C=0)

optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=0)

metric = Link_Prediction(link_prediction_raw=True,
                         link_prediction_filt=False,
                         batch_size=5000000,
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
    output_path="../dataset",
    lookuptable_E= node_lut,
    lookuptable_R= relation_lut,
    metric=metric,
    lr_scheduler=lr_scheduler,
    log=True,
    trainer_batch_size=100000,
    epoch=50,
    visualization=0,
    apex=True,
    dataloaderX=True,
    num_workers=4,
    pin_memory=True,
    metric_step=5,
    save_step=10000,
    metric_final_model=True,
    save_final_model=True,
    load_checkpoint= None
)
trainer.train()

evaluator = Kr_Evaluator(
    test_dataset=test_dataset,
    test_sampler=test_sampler,
    model=model,
    device=device,
    metric=metric,
    output_path="../dataset",
    train_dataset=train_dataset,
    valid_dataset=valid_dataset,
    lookuptable_E= node_lut,
    lookuptable_R= relation_lut,
    log=True,
    evaluator_batch_size=50000,
    dataloaderX=True,
    num_workers= 4,
    pin_memory=True,
    trained_model_path=None
)
evaluator.evaluate()

print("end")