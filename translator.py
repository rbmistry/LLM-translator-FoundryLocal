import os
import gradio as gr
import time
import tempfile
from gtts import gTTS
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from foundry_local import FoundryLocalManager
from langdetect import detect

# Function to clean translation output by removing thinking tags
def clean_translation_output(text):
    """Clean the translation output by removing any thinking tags"""
    # Remove any instances of '</think>' tags
    cleaned_text = text.replace("</think>", "").strip()
    
    # If the text has multiple '\n\n' that might indicate separation between thinking and result
    # Split by double newlines and take the last part as the actual translation
    if "\n\n" in cleaned_text:
        parts = cleaned_text.split("\n\n")
        cleaned_text = parts[-1].strip()
    
    return cleaned_text

# Initialize language mapping
LANGUAGES = {
    "English": "en",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Japanese": "ja",
    "Chinese": "zh",
    "Arabic": "ar",
    "Hindi": "hi",
    "Korean": "ko",
    "Dutch": "nl",
    "Swedish": "sv",
    "Turkish": "tr"
}

# Reverse mapping for language detection
LANG_CODES_TO_NAMES = {v: k for k, v in LANGUAGES.items()}

class TranslationApp:
    def __init__(self, model_alias="deepseek-r1-7b"):
        self.model_alias = model_alias
        self.manager = None
        self.llm = None
        self.setup_llm()
        
    def setup_llm(self):
        """Initialize the Foundry Local Manager and LLM"""
        print(f"Loading model: {self.model_alias}...")
        self.manager = FoundryLocalManager(self.model_alias)
        
        # Configure ChatOpenAI to use locally-running model
        self.llm = ChatOpenAI(
            model=self.manager.get_model_info(self.model_alias).id,
            base_url=self.manager.endpoint,
            api_key=self.manager.api_key,
            temperature=0.2,
            streaming=True
        )
        print(f"Model {self.model_alias} loaded successfully!")
        
    def detect_language(self, text):
        """Detect the language of the input text"""
        try:
            detected_code = detect(text)
            detected_name = LANG_CODES_TO_NAMES.get(detected_code, "Unknown")
            return detected_name
        except:
            return "Unknown"
    
    def create_translation_chain(self):
        """Create the translation chain with language detection"""
        # Enhanced prompt for better translations that avoids thinking tags
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are an expert translator with deep knowledge of many languages.
                Translate the following text from {input_language} to {output_language}.
                Preserve the tone, formality level, and cultural nuances where possible.
                If there are idioms or expressions, try to find appropriate equivalents.
                
                IMPORTANT: ONLY return the translated text without ANY explanations, tags (like </think>), 
                or additional text. Do not include any markup, notes, or thinking process in your output.
                Return ONLY the final translation."""
            ),
            ("human", "{input}")
        ])
        
        # Build the chain
        chain = prompt | self.llm | StrOutputParser()
        return chain
    
    def translate(self, input_text, output_language, auto_detect=False):
        """Translate text with optional auto-detection of input language"""
        if not input_text.strip():
            return "", "No text provided"
            
        # Auto-detect input language if enabled
        input_language = self.detect_language(input_text) if auto_detect else None
        info_message = f"Detected language: {input_language}" if auto_detect else ""
        
        try:
            chain = self.create_translation_chain()
            
            # If auto-detect is enabled, use the detected language
            translation = chain.invoke({
                "input_language": input_language if auto_detect else "English",
                "output_language": output_language,
                "input": input_text
            })
            
            # Clean the translation output to remove thinking tags
            cleaned_translation = clean_translation_output(translation)
            
            return cleaned_translation, info_message
        except Exception as e:
            return "", f"Error: {str(e)}"
    
    def text_to_speech(self, text, language):
        """Convert text to speech using gTTS"""
        if not text.strip():
            return None, "No text to convert to speech"
            
        try:
            # Get the language code for the selected language
            lang_code = LANGUAGES.get(language, "en")
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_filename = temp_file.name
            
            # Generate the audio
            tts = gTTS(text=text, lang=lang_code, slow=False)
            tts.save(temp_filename)
            
            return temp_filename, f"Generated audio for: {text[:30]}..." if len(text) > 30 else f"Generated audio for: {text}"
        except Exception as e:
            return None, f"Error generating audio: {str(e)}"
    
    def launch_interface(self):
        """Create and launch the Gradio interface"""
        with gr.Blocks(title="AI Translator", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# 🌐 AI Translator")
            gr.Markdown(f"Powered by Foundry Local with {self.model_alias}")
            
            with gr.Row():
                with gr.Column():
                    input_text = gr.Textbox(
                        label="Input Text",
                        placeholder="Enter text to translate...",
                        lines=5
                    )
                    auto_detect = gr.Checkbox(label="Auto-detect input language", value=True)
                    
                    with gr.Row():
                        output_language = gr.Dropdown(
                            choices=list(LANGUAGES.keys()),
                            label="Translate to",
                            value="French"
                        )
                        translate_btn = gr.Button("Translate", variant="primary")
                    
                with gr.Column():
                    output_text = gr.Textbox(
                        label="Translation",
                        lines=5,
                        interactive=False
                    )
                    info_message = gr.Textbox(
                        label="Info",
                        interactive=False
                    )
                    
                    with gr.Row():
                        clear_btn = gr.Button("Clear")
                        # Always include TTS button
                        tts_btn = gr.Button("🔊 Listen")
            
            # TTS functionality
            audio_output = gr.Audio(
                label="Translation Audio", 
                type="filepath",
                visible=True
            )
            
            # Set up event handlers
            translate_btn.click(
                fn=self.translate,
                inputs=[input_text, output_language, auto_detect],
                outputs=[output_text, info_message]
            )
            
            clear_btn.click(
                fn=lambda: ("", ""),
                inputs=None,
                outputs=[input_text, output_text]
            )
            
            tts_btn.click(
                fn=self.text_to_speech,
                inputs=[output_text, output_language],
                outputs=[audio_output, info_message]
            )
            
            # Examples
            examples = [
                ["Tell me how to get to Qualcomm Party Tonight at Mind the Bridge, San Francisco?", "Spanish", True],
                ["I love programming with AI models.", "French", True],
                ["The weather is beautiful today.", "Japanese", True],
                ["Could you help me find the nearest restaurant?", "German", True]
            ]
            
            gr.Examples(
                examples=examples,
                inputs=[input_text, output_language, auto_detect],
                outputs=[output_text, info_message],
                fn=self.translate
            )
            
            # Usage instructions
            with gr.Accordion("Usage Instructions", open=False):
                gr.Markdown("""
                ## How to use this translator:
                
                1. Enter the text you want to translate in the input box
                2. Select the target language from the dropdown
                3. Enable "Auto-detect" to automatically identify the source language
                4. Click "Translate" to get your translation
                5. Use "Listen" to hear the translation
                6. Click "Clear" to reset the fields
                
                This application uses the deepseek-r1-7b model running locally on your device
                through Foundry Local.
                """)
        
        # Launch the interface
        interface.launch(share=False)


# For command-line usage
if __name__ == "__main__":
    # Parse command line arguments if needed
    import argparse
    parser = argparse.ArgumentParser(description="AI Translation App with Foundry Local")
    parser.add_argument("--model", default="deepseek-r1-7b", help="Model alias to use")
    args = parser.parse_args()
    
    # Create and run the app
    app = TranslationApp(model_alias=args.model)
    app.launch_interface()
