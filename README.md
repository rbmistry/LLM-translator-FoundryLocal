# LLM-translator-FoundryLocal
This Python application provides AI-powered language translation with text-to-speech support. It uses a locally hosted LLM via Foundry, auto-detects input language, and delivers clean translations through a Gradio interface. The app also converts translated text to audio using gTTS, enhancing accessibility and multilingual communication.

This application is built on the how-to tutorial published below:
https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-local/how-to/how-to-use-langchain-with-foundry-local?pivots=programming-language-python

## Setting up the dev environment 

- Install VS Code
- Install Python Extension to VS Code
- Install Python Release 3.13.3 | Python.org
```python.exe -m pip install --upgrade pip```
- Microsoft C++ Build tools - https://visualstudio.microsoft.com/ 
- Install Rust on Windows using rustup - [https://sh.rustup.rs/](https://sh.rustup.rs/)
- Install openai API
```pip install openai```

## Download and install using the Foundry Local msix installer.

https://github.com/microsoft/Foundry-Local/releases

## Run AI Model Locally

```C:\>foundry model run deepseek-r1-7b```

Response: 

```🟢 Service is Started on http://localhost:5272, PID 41740!```
```[####################################] 100.00 % [Time remaining: about 0s]        12.9 MB/s```
```🕓 Loading model...```
```🟢 Model qnn-deepseek-r1-distill-qwen-7b loaded successfully```
```Interactive Chat. Enter /? or /help for help.```