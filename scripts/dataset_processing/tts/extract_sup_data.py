# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import torch
from hydra.utils import instantiate
from tqdm import tqdm

from nemo.core.config import hydra_runner


def preprocess_ds_for_fastpitch_align(dataloader):
    pitch_list = []
    for batch in tqdm(dataloader, total=len(dataloader)):
        tokens, tokens_lengths, audios, audio_lengths, align_prior_matrices, pitches, pitches_lengths = batch

        pitch = pitches.squeeze(0)
        pitch_list.append(pitch[pitch != 0])

    pitch_tensor = torch.cat(pitch_list)
    print(f"PITCH_MEAN, PITCH_STD = {pitch_tensor.mean().item()}, {pitch_tensor.std().item()}")


def preprocess_ds_for_mixer_tts_x(dataloader):
    pitch_list = []
    for batch in tqdm(dataloader, total=len(dataloader)):
        (
            tokens,
            tokens_lengths,
            audios,
            audio_lengths,
            align_prior_matrices,
            pitches,
            pitches_lengths,
            lm_tokens,
        ) = batch

        pitch = pitches.squeeze(0)
        pitch_list.append(pitch[pitch != 0])

    pitch_tensor = torch.cat(pitch_list)
    print(f"PITCH_MEAN, PITCH_STD = {pitch_tensor.mean().item()}, {pitch_tensor.std().item()}")


CFG_NAME2FUNC = {
    "ds_for_fastpitch_align": preprocess_ds_for_fastpitch_align,
    "ds_for_mixer_tts": preprocess_ds_for_fastpitch_align,
    "ds_for_mixer_tts_x": preprocess_ds_for_mixer_tts_x,
}


@hydra_runner(config_path='ljspeech/ds_conf', config_name='ds_for_fastpitch_align')
def main(cfg):
    dataset = instantiate(cfg.dataset)
    dataloader = torch.utils.data.DataLoader(
        dataset=dataset, batch_size=1, collate_fn=dataset._collate_fn, num_workers=4
    )

    print(f"Processing {cfg.manifest_filepath}:")
    CFG_NAME2FUNC[cfg.name](dataloader)


if __name__ == '__main__':
    main()  # noqa pylint: disable=no-value-for-parameter
