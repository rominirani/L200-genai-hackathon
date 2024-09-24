# Self-Refine Iterator with Google Gemini Pro

This Python script leverages Google's Gemini Pro large language model (LLM) to iteratively refine text in two specific domains:

- **Hackathon Idea Refinement:** Helps generate and refine ideas for hackathons.
- **CFP (Call for Papers) Submission Refinement:** Assists in crafting compelling proposals for technical conferences.

## How it Works

The script employs a two-model approach:

1. **Writer Model:** Generates text based on the chosen domain and initial input.
2. **Reviewer Model:** Evaluates the writer's output and provides constructive feedback.

The process is iterative: the reviewer's feedback becomes the input for the next iteration, leading to continuous improvement. This loop continues for a specified number of iterations or until the reviewer deems the text "Looks Good."

## Prerequisites

- **Google Cloud Project:** You need an active Google Cloud project with billing enabled.
- **Gemini API Key:** Obtain an API key for accessing Google's Gemini service.
- **Python 3.8 or later:** Ensure you have a compatible Python environment.

## Installation

1. Clone the Repository
2. Run the application as follows:
```bash 
$ python main.py -h
usage: Run Self Refine Iterator [-h] -o OUTFILE -i INFILE --domain {hackathon_idea_refine,cfp_submission_refine}

optional arguments:
  -h, --help            show this help message and exit
  -o OUTFILE, --outfile OUTFILE
                        Output file
  -i INFILE, --infile INFILE
                        Input file
  --domain {hackathon_idea_refine,cfp_submission_refine}
                        Which domain to run? 
                        (hackathon_idea_refine or cfp_submission_refine)

   ```
