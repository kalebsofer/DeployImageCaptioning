import torch
import torch.nn as nn

from .tapped_vit_b_16 import ImageEncoder

from .decoder import FrankDecoder


class Transformer(nn.Module):
    def __init__(self, *, decoder_params):
        super().__init__()

        self.encoder = ImageEncoder()

        self.decoder = FrankDecoder(**decoder_params)

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
