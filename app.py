import streamlit as st

from libs import Generator
from libs.config import ConfigReader


# Placeholder functions for AI processing (replace with your actual implementation)
def generate_text(prompt, model, domain):
    # This function should use the selected writer model and domain to generate the initial text
    # Replace this with your actual AI text generation logic
    return f"Initial output from {model} for domain {domain} based on prompt: {prompt}"

def revise_text(text, model, domain):
    # This function should use the selected reviewer model and domain to revise the text
    # Replace this with your actual AI text revision logic
    return f"Revised output from {model} for domain {domain}: {text}", 5, "Token count: 100"

#Store a list of domain names in the Streamlit session state
if 'domains' not in st.session_state:
    st.session_state.domains = ConfigReader().get_domains().keys()

#Store a list of model names in the Streamlit session state
if 'models' not in st.session_state:
    st.session_state.models = ConfigReader().get_models().keys()

#Initialize Session State for the Prompt
# Initialize session state for user_prompt
if "user_prompt" not in st.session_state:
    st.session_state.user_prompt = "Here is my CFP Proposal: \n <<Write your CFP here>>"

# Function to update user prompt based on domain
def update_prompt(domain):
    if domain == "cfp":
        st.session_state.user_prompt = "Here is my CFP Proposal: \n <<Write your CFP here>>"
    elif domain == "hackathon":
        st.session_state.user_prompt = "Here is my hackathon idea: \n <<Write your Hackathon idea here>>"

# Define the UI elements
st.title("AI Text Generation App")

# Domain selection
domain = st.selectbox("Select Domain:", st.session_state.domains)

# Writer model selection (replace with your actual model options)
writer_model = st.selectbox("Select Writer Model:", st.session_state.models)

# Reviewer model selection (replace with your actual model options)
reviewer_model = st.selectbox("Select Reviewer Model:", st.session_state.models)

st.cache_data.clear()  # Clear cache to ensure update_prompt is called
update_prompt(domain)

# User prompt
user_prompt = st.text_area("Enter your prompt:", placeholder="Write your prompt here...", value=st.session_state.user_prompt)

# Display the selected domain and models
#st.write(f"Selected Domain: {domain}")
#st.write(f"Selected Writer Model: {writer_model}")
#st.write(f"Selected Reviewer Model: {reviewer_model}")
#st.write(f"User Prompt: {user_prompt}")

# Submit button
if st.button("Submit"):
    if user_prompt == "":
        st.warning("Please enter a prompt before submitting.")
    else:
        # Placeholder for your AI processing logic
        #initial_output = generate_text(user_prompt, writer_model, domain)  # Replace with your actual function
        #final_output, num_iterations, token_info = revise_text(initial_output, reviewer_model, domain)  # Replace with your actual function

        generator = Generator(domain)
        first_response = generator.generate_initial_output(user_prompt)
        final_response = generator.generate_iterative_output(first_response['output'])

        initial_output = first_response['output']
        final_output = final_response['output']
        num_iterations = final_response['iterations']
        token_info = final_response['usage_metadata']

        # Display results
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Initial Output")
            st.write(first_response['output'])
        with col2:
            st.subheader("Final Output")
            st.write(final_output)

        st.write("**Token Information:**")
        st.json(token_info, expanded=False)
        st.write(f"**Number of Iterations:** {num_iterations}")

