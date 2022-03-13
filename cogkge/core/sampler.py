import torch


class UnifNegativeSampler():
    def __init__(self, triples, entity_dict_len, relation_dict_len, node_lut,device=torch.device('cuda:0')):
        # tensor(len,3)
        self.triples = triples
        self.entity_dict_len = entity_dict_len
        self.relation_dict_len = relation_dict_len
        self.device = device
        self.node_lut = node_lut

    def create_negative(self, batch_pos):
        # tensor(batch,3)
        batch_neg = batch_pos.clone()
        entity_number = torch.randint(self.entity_dict_len, (batch_neg.size()[0],)).to(self.device)
        mask = torch.rand(batch_neg.size()[0])
        head_mask = (mask > 0.5).to(self.device)
        tail_mask = (mask <= 0.5).to(self.device)
        batch_neg[head_mask, 0] = entity_number[head_mask].to(self.device)
        batch_neg[tail_mask, 2] = entity_number[tail_mask].to(self.device)
        if self.node_lut.data:
            batch_dict = {"h":batch_neg[:,0],
                          "r":batch_neg[:,1],
                          "t":batch_neg[:,2]}
            batch_dict.update({"h_type":self.node_lut.type[batch_neg[:,0]],
                               "t_type":self.node_lut.type[batch_neg[:,2]]})
            return batch_dict
        return batch_neg


class BernNegativeSampler():
    def __init__(self, triples, entity_dict_len, relation_dict_len, device=torch.device('cuda:0')):
        # tensor(len,3)
        self.triples = triples
        self.entity_dict_len = entity_dict_len
        self.relation_dict_len = relation_dict_len
        self.device = device

        h_r_uniq, t_count = torch.unique(triples[:, :-1], return_counts=True, dim=0)
        r_t_uniq, h_count = torch.unique(triples[:, 1:], return_counts=True, dim=0)

        self.P_remove_head = torch.zeros(self.relation_dict_len)
        for r in range(self.relation_dict_len):
            idx = h_r_uniq[:, 1] == r
            tph = torch.mean(t_count[idx].type(torch.FloatTensor))

            idx = r_t_uniq[:, 0] == r
            hpt = torch.mean(h_count[idx].type(torch.FloatTensor))

            self.P_remove_head[r] = tph / (tph + hpt)

    def create_negative(self, batch_pos):
        # tensor(batch,3)
        batch_neg = batch_pos.clone()
        entity_number = torch.randint(self.entity_dict_len, (batch_neg.size()[0],)).to(self.device)
        relation = batch_pos[:, 1]
        mask = torch.rand(batch_neg.size()[0])
        head_mask = (mask < self.P_remove_head[relation]).to(self.device)
        tail_mask = (mask >= self.P_remove_head[relation]).to(self.device)
        batch_neg[head_mask, 0] = entity_number[head_mask].to(self.device)
        batch_neg[tail_mask, 2] = entity_number[tail_mask].to(self.device)
        return batch_neg


class AdversarialSampler:
    def __init__(self, triples, entity_dict_len, relation_dict_len, neg_per_pos, device=torch.device('cuda:0')):
        # tensor(len,3)
        self.triples = triples
        self.entity_dict_len = entity_dict_len
        self.relation_dict_len = relation_dict_len
        self.neg_per_pos = neg_per_pos
        self.device = device

    def create_negative(self, batch_pos):
        """
        batch_pos:(batch,3)
        return: batch_neg(batch * neg_per_pos,3)
        """
        return torch.cat([self._create_negative(batch_pos) for i in range(self.neg_per_pos)], dim=0)

    def _create_negative(self, batch_pos):
        batch_neg = batch_pos.clone()
        entity_number = torch.randint(self.entity_dict_len, (batch_neg.size()[0],)).to(self.device)
        mask = torch.rand(batch_neg.size()[0])
        head_mask = (mask > 0.5).bool().to(self.device)
        tail_mask = (mask <= 0.5).bool().to(self.device)
        batch_neg[head_mask, 0] = entity_number[head_mask].to(self.device)
        batch_neg[tail_mask, 2] = entity_number[tail_mask].to(self.device)
        return batch_neg


if __name__ == "__main__":
    fake_triples = torch.tensor([[1, 0, 0],
                                 [1, 0, 4],
                                 [1, 0, 3],
                                 [5, 0, 3],
                                 [2, 1, 5],
                                 [4, 2, 2]]).to("cuda:0")
    batch_pos = torch.tensor([[4, 2, 1],
                              [0, 3, 4]]).to("cuda:0")
    # sampler=UnifNegativeSampler(fake_triples,5,4)
    # batch_neg=sampler.create_negative(batch_pos)
    sampler = BernNegativeSampler(fake_triples, 6, 3)
    batch_neg = sampler.create_negative(batch_pos)
    # sampler=AdversarialSampler(fake_triples,5,4,3)
    # batch_neg=sampler.create_negative(batch_pos)
    print(batch_neg)
