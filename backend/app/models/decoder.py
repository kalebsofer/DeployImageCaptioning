import torch
import torch.nn as nn
from torchtune.modules import RotaryPositionalEmbeddings

from .tokeniser import GPT2TokeniserPlus


class FrankDecoder(nn.Module):
    def __init__(
        self,
        *,
        vocab_size: int,
        embed_dim: int,
        num_layers: int,
        num_heads: int,
        ff_dim: int | None = None,
    ):
        if embed_dim % num_heads != 0:
            raise ValueError("embed_dim must be divisible by num_heads")

        if ff_dim is None:
            ff_dim = embed_dim * 4

        super().__init__()

        self.emb = nn.Embedding(vocab_size, embed_dim)

        self.pos_emb = SinusoidalPositionalEmbeddings(embed_dim)

        self.transformer = nn.TransformerDecoder(
            nn.TransformerDecoderLayer(
                d_model=embed_dim,
                nhead=num_heads,
                dim_feedforward=ff_dim,
                batch_first=True,
            ),
            num_layers,
        )

    def forward(self, x, memory):
        x = self.emb(x) + self.pos_emb(x)
        causal_mask = nn.Transformer.generate_square_subsequent_mask(x.size(1)).to(
            x.device
        )
        x = self.transformer(x, memory, tgt_is_causal=True, tgt_mask=causal_mask)
        return x


class SinusoidalPositionalEmbeddings(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        # Ensure that positions dont start at 0
        position = torch.arange(1, max_len + 1).unsqueeze(1)
        div_term = torch.exp(
            -torch.arange(0, d_model, 2) * (torch.log(torch.tensor(10000.0)) / d_model)
        )
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer("pe", pe)

    def forward(self, x):
        seq_len = x.size(-1)
        return self.pe[:seq_len].unsqueeze(0)
