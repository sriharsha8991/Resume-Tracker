
# Resume Filtering System

The Resume Filtering System is a Streamlit-based application designed to help HR professionals efficiently filter and analyze resumes. It allows users to rank resumes based on their relevance to a given job description and manage the top-ranked resumes conveniently.

## Features

- **Automated Resume Ranking**: Automatically rank resumes based on their textual similarity to a job description using advanced NLP techniques.
- **Resume Management**: Save and review the top resumes in a dedicated folder.
- **Analysis Reporting**: Generate and save textual reports of job description analyses.

## Prerequisites

Before you can run this application, you'll need to have the following installed:
- Python 3.8 or higher
- Streamlit
- spaCy
- pdfminer.six
- scikit-learn
- matplotlib
- pandas

You can install the necessary Python packages using:

```bash
python -m spacy download en_core_web_sm
```

## Installation

1. Clone the repository to your local machine:

```bash
git clone <link>
cd your-repository-folder
```

2. Install the required Python libraries:

```bash
pip install -r requirements.txt
```

## Running the Application

To run the application, navigate to the project directory and use the following command:

```bash
streamlit run app.py
```

## Usage

- **Launch the Application**: Run the command above and navigate to `http://localhost:8501` in your web browser.
- **Upload Resumes**: Navigate to the 'Resume Filtering Page' and enter the directory where your resumes are stored.
- **Enter Job Description**: Provide a job description against which the resumes will be ranked.
- **Analyze and Save Top Resumes**: Click the 'Analyze and Save Top Resumes' button to process and save the top resumes.
- **View and Manage Top Resumes**: Navigate to the 'Top Resumes Processing Page' to view and further manage the top resumes.

## Contributing

Contributions to this project are welcome! Please fork the repository and submit a pull request with your enhancements.



You can adjust the contents based on the specific needs of your project or any additional details you might want to include.