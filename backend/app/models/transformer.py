"""
Define transformer architecture here
"""

import torch.nn as nn


class Transformer(nn.Module):

    def __init__(self, learning_rate, batch_size):
        super(Transformer, self).__init__()
        self.learning_rate = learning_rate
        self.batch_size = batch_size

    def forward(self, x):
        pass
