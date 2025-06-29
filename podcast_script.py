import re
import os
import edge_tts
import xml.etree.ElementTree as ET
from pydub import AudioSegment
import asyncio

# Configuration: speaker and language
speaker1 = "Elena" # Change the name here
speaker2 = "Tomas" # Change the name here
lang = "Spanish"  # Change the language here

# Voice mapping
voice_map = {
    "Elena": "es-AR-ElenaNeural", # Change the edge-tts voice here
    "Tomas": "es-AR-TomasNeural" # Change the edge-tts voice here
}

# Function to generate SSML markup for a conversation
def generate_ssml_conversation(dialogue_text, speaker1="Elena", speaker2="Tomas"):
    print("Generating SSML conversation...")

    # Remove any stage directions or descriptions in parentheses
    dialogue_text = re.sub(r'\([^)]*\)', '', dialogue_text).strip()

    # Split the dialogue into parts based on the speaker's name
    ssml_output = '<speak>\n'
    dialogue_lines = dialogue_text.split("\n")

    for line in dialogue_lines:
        line = line.strip()
        if line.startswith(speaker1 + ":"):
            # Use speaker1's voice
            ssml_output += f'<voice name="{speaker1}">\n'
            ssml_output += f'    {line.replace(speaker1 + ":", "").strip()}\n'
            ssml_output += '    <break time="0.5s"/>\n'
            ssml_output += '</voice>\n'
        elif line.startswith(speaker2 + ":"):
            # Use speaker2's voice
            ssml_output += f'<voice name="{speaker2}">\n'
            ssml_output += f'    {line.replace(speaker2 + ":", "").strip()}\n'
            ssml_output += '    <break time="0.3s"/>\n'
            ssml_output += '</voice>\n'

    ssml_output += '</speak>'
    
    print("SSML conversation generated successfully.")
    return ssml_output

# Read the input content from dialogue.txt
print("Reading input content from 'dialogue.txt'...")
with open("dialogue.txt", "r") as file:
    dialogue_input = file.read().strip()

# Generate SSML conversation
ssml_conversation = generate_ssml_conversation(dialogue_input)

# Check if SSML conversation generation was successful
if ssml_conversation is None:
    print("Exiting the script due to error in SSML generation.")
    exit(1)  # Exit the script if there was an error

# Save the SSML output to a text file
print("Saving SSML output to 'SSML.txt'...")
with open("SSML.txt", "w") as file:
    file.write(ssml_conversation)

print("SSML output has been saved to SSML.txt.")

async def synthesize_text(text, voice_name, filename):
    """Use EdgeTTS to convert text to speech and save it as an MP3 file."""
    edge_voice = voice_map.get(voice_name)  # Get the right voice
    if edge_voice is None:
        raise ValueError(f"Unknown voice name: {voice_name}")
    print(f"Generating audio for voice: {edge_voice}")  # Debug output
    print(f"Text: {text}")  # Debug output
    communicate = edge_tts.Communicate(text, voice=edge_voice, rate="+15%")
    await communicate.save(filename)
    print(f"Audio saved to '{filename}'.")

def parse_ssml(file_path):
    """Parse the SSML file and extract text and speaker info."""
    print(f"Parsing SSML from '{file_path}'...")
    tree = ET.parse(file_path)
    root = tree.getroot()

    segments = []

    for elem in root:
        if elem.tag == 'voice':
            voice_name = elem.attrib['name']
            text = ''.join(elem.itertext()).strip()
            segments.append((voice_name, text))

    print("SSML parsing completed.")
    return segments

async def main():
    # Parse the SSML output that was saved earlier
    segments = parse_ssml("SSML.txt")
    print(f"Found {len(segments)} segments to synthesize.")

    # Synthesize speech for each segment
    for i, (voice_name, text) in enumerate(segments):
        mp3_filename = f"output_segment_{i + 1}.mp3"
        await synthesize_text(text, voice_name, mp3_filename)

    # Combine the segments into a single file
    print("Combining audio segments...")
    combined = AudioSegment.empty()
    for i in range(len(segments)):
        mp3_filename = f"output_segment_{i + 1}.mp3"
        audio_segment = AudioSegment.from_mp3(mp3_filename)
        combined += audio_segment

    # Save the final combined audio
    combined.export("final_output.mp3", format="mp3")
    print("Final audio file 'final_output.mp3' has been created.")

    # Remove temporary output MP3s
    for i in range(len(segments)):
        os.remove(f"output_segment_{i + 1}.mp3")

# Run the main function
asyncio.run(main())
