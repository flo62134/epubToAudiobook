import os
import re
import numpy as np
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from datasets import load_dataset
import torch
import soundfile as sf
import sentencepiece


def custom_sort(filename):
    # Extract numbers from the filename using a regular expression
    numbers = [int(num) for num in re.findall(r'\d+', filename)]
    return numbers


def merge_sentences(sentences):
    MAX_LENGTH = 400
    merged_sentences = []
    current_sentence = ''

    for sentence in sentences:
        if len(current_sentence) + len(sentence) <= MAX_LENGTH:
            current_sentence += sentence
        else:
            merged_sentences.append(current_sentence)
            current_sentence = sentence

    if current_sentence:
        merged_sentences.append(current_sentence)

    return merged_sentences


def tts_conversion(sentence, processor, model, speaker_embeddings, vocoder):
    sentence = sentence.replace("\n", " ")
    sentence = sentence.replace("’s", "'s")
    sentence = sentence.replace("’t", "'t")

    if sentence.strip():  # Ensure the sentence is not empty
        print(sentence)
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
        sentences = [x + delimiter for x in text_content.split(delimiter) if x]
        sentences = merge_sentences(sentences)

        audio_pieces = []

        # Rely on a single thread to avoid errors
        for sentence in sentences:
            speech = tts_conversion(sentence, processor, model, speaker_embeddings, vocoder)
            if speech is not None:
                audio_pieces.append(speech)

        # Generate one second of silence
        silence = np.zeros(16000)

        # Insert the silence between audio pieces
        merged_audio_pieces = []
        for piece in audio_pieces:
            merged_audio_pieces.append(piece)
            merged_audio_pieces.append(silence)
        merged_audio = np.concatenate(merged_audio_pieces[:-1], axis=0)  # Exclude the last silence

        # Ensure the directory exists
        audio_dir = './audiobook'
        if not os.path.exists(audio_dir):
            os.makedirs(audio_dir)

        sf.write(audio_filename, merged_audio, samplerate=16000)
