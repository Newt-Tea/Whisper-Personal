# Whisper-Personal

Welcome to the Whisper-Personal repository! This project is designed to Transcribe and save audio files.

## Dependancies
    
    Python >= 3.12.6

## Usage

To use this project, follow these steps:

1. Download the scripts by cloning or zipping the repo
2. Ensure Python is installed with ```python --version ```
3. Run ```pip install -r requirements.txt```
4. Add your whisper API key
    - Set your HUGGINGFACE_API_KEY enviroment variable (requires restart) or
    - Change line 14 in main.py and line 10 in backup.py to api_key = {your_Key}
- You only have to run the commands above once
5. Run main.py 
6. If the model fails to transcript import your file into backup.py 

## Contributing

We welcome contributions! Please follow these steps to contribute:

1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Create a new Pull Request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or feedback, please contact [your email or contact information].
