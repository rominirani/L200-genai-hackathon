import argparse
import json

import dotenv
import os

import logging
import sys

from libs import Generator
from libs.config import ConfigReader

dotenv.load_dotenv()

#Current code works with Gemini AI API and requires the key.
#Later on will look to incorporate other models from Vertex and / or Model Garden
# import google.generativeai as genai
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# def get_domain_models_map(domain_configfile, model_configfile):
#   """
#   Reads a JSON configuration file and returns a dictionary mapping domain names to 
#   their respective writer and reviewer model names.

#   Args:
#     config_file: Path to the JSON configuration file.

#   Returns:
#     A dictionary mapping domain names to dictionaries containing 'writer' and 
#     'reviewer' model names.
#   """

#   try:
#       with open(domain_configfile, 'r') as d, open(model_configfile, 'r') as m:
#         domain_config = json.load(d)
#         model_config = json.load(m)
#   except FileNotFoundError:
#       print(f"Error: Input file not found: {domain_configfile}")
#       exit(1)

#   domains = domain_config['domains']
#   models = {model['model_id']: model for model in model_config['models']} 
#   domain_models_map = {}

#   for domain in domains:
#     domain_name = domain['domain_name']
#     writer_model_id = domain['domain_model_id_writer']
#     reviewer_model_id = domain['domain_model_id_reviewer']
#     prompts_config_file = domain['domain_prompts_config_file']

#     domain_models_map[domain_name] = {
#         'name': domain_name,
#         'prompts_config_file': prompts_config_file,
#         'writer': models[writer_model_id],
#         'reviewer': models[reviewer_model_id]
#     }

#   return domain_models_map

# def get_domain_prompts(config_file):
#   """
#   Reads a JSON configuration file and returns a dictionary mapping prompts for the domain

#   Args:
#     config_file: Path to the JSON configuration file.

#   Returns:
#     A dictionary mapping domain names to dictionaries containing 'writer' and 
#     'reviewer' prompts.
#   """

#   try:
#       with open(config_file, 'r') as f:
#         prompts_config = json.load(f)
#   except FileNotFoundError:
#       print(f"Error: Input file not found: {config_file}")
#       exit(1)

#   return prompts_config

# def create_model(domain, role):
#     """Creates a generative model with the appropriate prompt."""
#     print("Now loading the prompts for ", domain["prompts_config_file"])
#     domain_prompts = get_domain_prompts(domain["prompts_config_file"])

#     #Now load the main system prompt
#     prompt = domain_prompts[role]["system_prompt"]

#     if role == "writer":
#         model_name = domain["writer"]["model_name"]
#         model_generation_config = domain["writer"]["model_generation_config"]
#     elif role == "reviewer":
#         model_name = domain["reviewer"]["model_name"]
#         model_generation_config = domain["reviewer"]["model_generation_config"]

#     return genai.GenerativeModel(
#         model_name=model_name,
#         generation_config=model_generation_config,
#         system_instruction=prompt,
#     )

# Core Logic (using a single function that specifies which domain to run)
# def run_model_iteration(input_text, domain_model,  num_iterations=3):
#     """Runs the writer and reviewer models iteratively."""

#     print(f"Starting the Create/Review process for: {domain_model["name"]}")
#     domain_prompts = get_domain_prompts(domain_model["prompts_config_file"])
#     print(f'Loading the domain prompts for: {domain_model["name"]}')

#     writer_model = create_model(domain_model, "writer")
#     reviewer_model = create_model(domain_model, "reviewer")

#     chat_history_writer = []
#     chat_writer = writer_model.start_chat(history=chat_history_writer)

#     chat_history_reviewer = []
#     chat_reviewer = reviewer_model.start_chat(history=chat_history_reviewer)

#     for iteration in range(1, num_iterations + 1):
#         print(f"\nIteration: {iteration}/{num_iterations}")

#         # Writer Model
#         print(" - Calling the writer model...")
#         if iteration == 1:
#             input_text = domain_prompts["writer"]["initial_prompt"].replace("{data}", input_text) 
#         else:
#             input_text = domain_prompts["writer"]["iterative_prompt"].replace("{data}", input_text) 
#         response = chat_writer.send_message(input_text)
#         print(f"Token Details: {response.usage_metadata}")
#         chat_history_writer.extend([
#             {"role": "user", "content": input_text},
#             {"role": "model", "content": response.text}
#         ])
#         print(f"Model Writer Output:\n{response.text}")

#         # Reviewer Model
#         print(" - Calling the reviewer model...")
#         if iteration == 1:
#             input_text = domain_prompts["reviewer"]["initial_prompt"].replace("{data}", response.text)
#         else:
#             input_text = domain_prompts["reviewer"]["iterative_prompt"].replace("{data}", response.text)
#         #response = reviewer_model.generate_content(response.text)
#         response = chat_reviewer.send_message(input_text)
#         print(f"Token Details: {response.usage_metadata}")
#         print(f"Model Reviewer Feedback:\n{response.text}")
#         modelReviewerRecommendation = json.loads(response.text)["recommendation"]
#         if modelReviewerRecommendation == "Approve":
#             break;

#         # Early Exit if "Looks Good"
#         #if "Looks Good".lower() in response.text.lower():
#         #    print("Looks Good! Exiting the loop.")
#         #    break

#         # Update input for next iteration
#         input_text = response.text

#     return chat_history_writer[-1]['content']  # Return the last model output



# Main Execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Self Refine Iterator')
    parser.add_argument('-o', dest='outfile', required=True,
                        action='store', help='Output file')
    parser.add_argument('-i', dest='infile', required=True,
                        action='store', help='Input file')
    parser.add_argument('--domain', dest='domain', required=True,
                        action='store', choices={'hackathon', 'cfp'},
                        help='Which domain to run? (hackathon or cfp)')
    args = parser.parse_args()

    # Read the input file/prompt given by the user
    try:
        with open(args.infile, 'r') as f:
            input_text = f.read()
    except FileNotFoundError:
        print(f"Error: Input file not found: {args.infile}")
        exit(1)

    # Check if domain exists
    if args.domain not in ConfigReader().get_domains().keys():
        print(f"Error: Domain not found: {args.domain}")
        exit(1)

    # Execute logic
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    generator = Generator(args.domain)
    first_response = generator.generate_initial_output(input_text)
    print(f"Token Details: {first_response['usage_metadata']}")
    print(f"First Response:\n{first_response['output']}")

    final_response = generator.generate_iterative_output(first_response['output'])
    print(f"Token Details: {final_response['usage_metadata']}")
    print(f"Final Response:\n{final_response['output']}")

    with open(args.outfile, 'w') as f:
        f.write(final_response['output'])

    print(f"Output written to: {args.outfile}")
