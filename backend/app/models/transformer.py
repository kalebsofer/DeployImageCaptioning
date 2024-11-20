import torch
import torch.nn as nn

import tapped_vit_b_16

from .decoder import get_gpt2_based_decoder


class Transformer(nn.Module):
    def __init__(self, *, decoder_params):
        super().__init__()

        self.encoder = tapped_vit_b_16.ImageEncoder()

        self.decoder = get_gpt2_based_decoder(**decoder_params)

        vocab_size = self.decoder.emb.num_embeddings
        emb_dim = self.decoder.emb.embedding_dim

        self.proj = nn.Linear(emb_dim, vocab_size)

    def forward(self, img, caption):

        img_embeds = self.encoder(img)

        caption_embeds = self.decoder(caption, img_embeds)

        out = self.proj(caption_embeds)

        return out


if __name__ == "__main__":
    model = BaselineImgCaptionGen()

    model_scripted = torch.jit.script(model)

    model_scripted.save("baseline_model.pt")
    # print(model)
    pass
