# AutoCleaner
A beautiful, fast, and feature-rich file organization tool.

## Features
- Scans specified directories for files.
- Categorizes files based on their extensions.
- Organizes files into category-specific folders.
- Provides a preview of the organization before proceeding.
- Generates detailed reports of the organization process.

## Installation
1. Clone the repository:
   git clone https://github.com/borgox/AutoCleaner.git
2. Navigate to the project directory:
   cd AutoCleaner
3. Install the required packages:
   pip install -r requirements.txt

## Usage
Run the application with the desired folder paths:
python src/main.py [folders] [options]

## Options
- `--dry-run`: Preview changes without moving files.
- `--auto-organize`: Automatically resolve ambiguous files.
- `--no-backup`: Skip creating backup archives.
- `--delete-empty`: Delete empty folders after organization.
- `--log-level`: Set logging level (DEBUG, INFO, WARNING, ERROR).

## Contributing
Contributions are welcome! Please open an issue or submit a pull request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.