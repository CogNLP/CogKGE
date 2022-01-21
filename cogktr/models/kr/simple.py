import torch
import torch.nn as nn
import torch.nn.functional as F

class SimplE(nn.Module):
    def __init__(self, entity_dict_len, relation_dict_len, embedding_dim):
        super(SimplE, self).__init__()
        self.embedding_dim = embedding_dim
        self.name = "SimplE"
        self.entity_dict_len = entity_dict_len
        self.relation_dict_len = relation_dict_len
        self.head_embedding = nn.Embedding(entity_dict_len, embedding_dim)
        self.tail_embedding = nn.Embedding(entity_dict_len, embedding_dim)
        self.relation_embedding = nn.Embedding(relation_dict_len, embedding_dim)
        self.relation_inverse_embedding = nn.Embedding(relation_dict_len, embedding_dim)
        self.r = None
        self.r_ = None
        self.h = None
        self.h_ = None
        self.t = None
        self.t_ = None
 

        nn.init.xavier_uniform_(self.head_embedding.weight.data)
        nn.init.xavier_uniform_(self.tail_embedding.weight.data)
        nn.init.xavier_uniform_(self.relation_embedding.weight.data)
        nn.init.xavier_uniform_(self.relation_inverse_embedding.weight.data)

    def forward(self,sample):
        batch_h,batch_r,batch_t =  sample[:, 0], sample[:, 1], sample[:, 2]
        h = self.head_embedding(batch_h)
        r = self.relation_embedding(batch_r)
        self.r = r
        t = self.tail_embedding(batch_t)

        # h = F.normalize(h, p=2.0,dim=-1)
        # t = F.normalize(t, p=2.0, dim=-1)
        self.h = h
        self.t = t
        score_front = torch.sum(h * r * t,dim=1) # (batch,)
       
        h_ = self.head_embedding(batch_t)
        r_ = self.relation_inverse_embedding(batch_r)
        self.r_ = r_
        t_ = self.tail_embedding(batch_h)


        # h_ = F.normalize(h_, p=2.0,dim=-1)
        # t_ = F.normalize(t_, p=2.0, dim=-1)
        self.h_ = h_
        self.t_ = t_
        score_reverse = torch.sum(h_ * r_ * t_,dim=1) # (batch,)

        return (score_front + score_reverse) / 2
 
    def get_score(self,sample):
        return self.forward(sample)
    
    def get_penalty(self):
        return torch.norm(torch.mean(self.r + self.r_ + self.t + self.t_ + self.h + self.h_))
        # return torch.mean(torch.norm(self.r) + torch.norm(self.r_)) 