import os
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from datasets import load_dataset
import torch
import soundfile as sf
import sentencepiece
import numpy as np
import re
from concurrent.futures import ThreadPoolExecutor


def custom_sort(filename):
    # Extract numbers from the filename using a regular expression
    numbers = [int(num) for num in re.findall(r'\d+', filename)]
    return numbers


def tts_conversion(sentence, processor, model, speaker_embeddings, vocoder):
    if sentence.strip():  # Ensure the sentence is not empty
        inputs = processor(text=sentence, return_tensors="pt")
        speech = model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=vocoder)
        return speech.numpy()
    return None


def convert():
    processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
    model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
    vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")

    # Get the list of all files in ./pages_text_grouped in alphabetical order
    text_files = sorted(
        [f for f in os.listdir('./pages_text_grouped') if os.path.isfile(os.path.join('./pages_text_grouped', f))],
        key=custom_sort)

    # Load xvector containing speaker's voice characteristics from a dataset
    embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
    speaker_embeddings = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)

    # Loop through each text file, read its content, and convert to speech
    for file in text_files:
        audio_filename = os.path.join('./audiobook', file + '.wav')
        # Check if audio file already exists
        if os.path.exists(audio_filename):
            print(f"File {audio_filename} already exists. Skipping...")
            continue

        print("TTS on " + file)
        with open(os.path.join('./pages_text_grouped', file), 'r', encoding='utf-8') as f:
            text_content = f.read()

        # Split text_content into sentences (sentences are separated by periods)
        delimiter = '.'
        sentences = [x+delimiter for x in text_content.split(delimiter) if x]
        print(sentences)

        audio_pieces = []

        # Parallelize the TTS conversion for sentences
        with ThreadPoolExecutor(max_workers=6) as executor:
            results = list(executor.map(tts_conversion, sentences,
                                        [processor] * len(sentences),
                                        [model] * len(sentences),
                                        [speaker_embeddings] * len(sentences),
                                        [vocoder] * len(sentences)))
            audio_pieces.extend([res for res in results if res is not None])

        # Merge the audio pieces into a single audio array
        merged_audio = np.concatenate(audio_pieces, axis=0)

        # Ensure the directory exists
        audio_dir = './audiobook'
        if not os.path.exists(audio_dir):
            os.makedirs(audio_dir)

        sf.write(audio_filename, merged_audio, samplerate=16000)
