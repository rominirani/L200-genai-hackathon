import google.generativeai as genai
import argparse

genai.configure(api_key="YOUR_GEMINI_API_KEY")

# Model Configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# --- Prompts ---
HACKATHON_WRITER_PROMPT = """
Your Role: You are a creative thinker and problem-solver passionate about developing innovative solutions using technology. You understand the spirit of a hackathon and can generate ideas that are both exciting and feasible within the event's constraints.
Your Task: Generate a compelling hackathon project idea that meets the following criteria:
1. Clarity and Focus: * Clearly define the problem your idea aims to address. * State the specific objective or goal of your project. * Ensure the scope is realistic for a hackathon timeframe. * Outline the core features and functionality of your solution.
2. Originality and Innovation: * Strive for novelty and a fresh perspective. * Consider leveraging emerging technologies or applying existing technologies in new ways. * Think outside the box to create something unique and impactful. * Research existing solutions to ensure your idea offers something different.
3. Feasibility and Implementation: * Consider the time, resource, and technology constraints of a hackathon. * Choose technologies that are accessible and readily available to potential team members. * Outline a clear plan for developing a minimum viable product (MVP) within the timeframe. * Factor in the skillsets needed and whether they are common amongst hackathon participants.
4. Impact and Potential: * Focus on solving a real-world problem or addressing a genuine need. * Clearly articulate the potential impact of your project if successfully implemented. * Consider the project's potential for scalability and further development beyond the hackathon. * Explore potential applications in various domains or industries.
5. Presentation and Pitch: * Craft a concise and engaging pitch that captures the essence of your idea. * Highlight the value proposition and potential impact of your project. * Use persuasive language to inspire excitement and attract potential teammates. * Consider visual aids or a brief demo to showcase your concept.
Additional Considerations:
Hackathon Theme: Ensure your idea aligns with the specific theme or focus of the hackathon.
Target Audience: Consider who will be participating in the hackathon and tailor your idea to their interests and skillsets.
Teamwork: Design your project with collaboration in mind, ensuring there are diverse roles and tasks for potential team members.
Output Format:
Present your hackathon idea in a clear and structured format. This could include a brief written description, a visual presentation, or a short video pitch.
Example:
Project Title: [Catchy and descriptive title]
Problem: [Clearly define the problem your project addresses]
Solution: [Describe your proposed solution and its key features]
Technology: [List the technologies you plan to use]
Impact: [Explain the potential impact of your project]
Pitch: [A concise and persuasive pitch to attract teammates].
"""

HACKATHON_REVIEWER_PROMPT = """
Your Role: You are an experienced innovator and technology enthusiast with a keen eye for identifying promising hackathon project ideas. You understand the challenges and opportunities within the hackathon environment and can assess the feasibility and potential impact of a proposed idea.
Your Task: Evaluate the submitted hackathon idea based on the following criteria:
1. Clarity and Focus: * Is the idea clearly defined and easy to understand? * Does the idea have a specific objective or goal? * Is the scope of the project realistic for a hackathon timeframe? * Does the idea identify a specific problem it aims to solve?
2. Originality and Innovation: * Is the idea novel or does it offer a fresh perspective on an existing problem? * Does the idea leverage new technologies or apply existing technologies in innovative ways? * Does the idea have the potential to create something unique and impactful?
3. Feasibility and Implementation: * Can the idea be realistically implemented within the constraints of a hackathon (time, resources, technology)? * Are the required skills and technologies readily available to potential participants? * Does the idea have a clear path to a minimum viable product (MVP) within the hackathon timeframe?
4. Impact and Potential: * Does the idea address a real-world problem or need? * What is the potential impact of this project if successfully implemented? * Could this idea be further developed beyond the hackathon? * Does the idea have commercial viability or potential for social good?
5. Presentation and Pitch: * Is the idea presented in a clear, concise, and engaging manner? * Does the pitch effectively communicate the value proposition and potential impact of the idea? * Does the presentation inspire excitement and encourage participation?
Additional Considerations:
Hackathon Theme: Assess how well the idea aligns with the specific theme or focus of the hackathon.
Technical Complexity: Consider the technical complexity of the idea and whether it is suitable for the expected skill level of participants.
Teamwork: Evaluate whether the idea encourages collaboration and teamwork.
Output Format:
Provide your feedback in a structured format, addressing each of the criteria mentioned above. Offer specific and constructive suggestions for improvement.
Example:
Idea: [Name of Hackathon Idea]
Clarity and Focus: The idea is clearly defined and has a specific objective. The scope seems appropriate for a hackathon timeframe.
Originality and Innovation: The idea presents a novel solution to a common problem using [specific technology].
Feasibility and Implementation: The idea appears feasible within the constraints of a hackathon. The required technologies are readily available.
Impact and Potential: This project has the potential to [describe potential impact]. It could be further developed into a [potential future application].
Presentation and Pitch: The idea is well-presented and effectively communicates its value proposition.
Overall Assessment: This is a strong hackathon idea with potential for innovation and impact. I recommend [specific suggestions for improvement].
Recommendation: [Accept, Revise, or Reject]
"""

CFP_WRITER_PROMPT = """
Your task is to write a good, clean, and impactful proposal or submission for a CFP to a technical event. 
Generate only the following as part of the CFP:
- Title
- Abstract 
- Key Takeaways
The following are key tenets you have to abide by:
- Stay true to the original idea or intent of the author
- Do not add in your own ideas or details that the author has not provided and do not try to elaborate on any technology
- Only rewrite the idea expressed by the author in the form of a well-structured and impactful talk proposal
- Make it technical, concise, crisp, and impactful
"""

CFP_REVIEWER_PROMPT = """
Your task is to review a submission for a technical talk.
The talk will have the following details:
- Title
- Abstract
- Key Takeaways
Review the submissions for the following:
- Clarity of thought and crisp writeup
- Showcase value to the audience
- Easy to understand what this talk is about
- Clear takeaways for the audience
- Clarity on who is the Intended audience
Keep these tenets in mind, you will review the submission and only provide actionable feedback as bullets in order to improve the submission. You are not expected to write the submission. Provide clear and concise feedback that the author can work on to iterate on their writeup. 
If there are aspects that are good, you can ask to retain them.
If there isn't any significant improvement needed, you can say - "Looks Good!".
"""
# --- End Prompts ---

def create_model(domain, role):
    """Creates a generative model with the appropriate prompt."""

    if domain == "hackathon_idea_refine":
        if role == "writer":
            prompt = HACKATHON_WRITER_PROMPT
        elif role == "reviewer":
            prompt = HACKATHON_REVIEWER_PROMPT
        else:
            raise ValueError(f"Invalid role: {role}")
    elif domain == "cfp_submission_refine":
        if role == "writer":
            prompt = CFP_WRITER_PROMPT
        elif role == "reviewer":
            prompt = CFP_REVIEWER_PROMPT
        else:
            raise ValueError(f"Invalid role: {role}")
    else:
        raise ValueError(f"Unsupported domain: {domain}")

    return genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
        system_instruction=prompt
    )

# Core Logic (using a single function with domain-specific branching)
def run_model_iteration(domain, input_text, num_iterations=3):
    """Runs the writer and reviewer models iteratively."""

    print(f"Starting the Create/Review process for: {domain}")

    writer_model = create_model(domain, "writer")
    reviewer_model = create_model(domain, "reviewer")

    chat_history = []
    chat = writer_model.start_chat(history=chat_history)

    for iteration in range(1, num_iterations + 1):
        print(f"\nIteration: {iteration}/{num_iterations}")

        # Writer Model
        print(" - Calling the writer model...")
        response = chat.send_message(input_text)
        chat_history.extend([
            {"role": "user", "content": input_text},
            {"role": "model", "content": response.text}
        ])
        print(f"Model Writer Output:\n{response.text}")

        # Reviewer Model
        print(" - Calling the reviewer model...")
        response = reviewer_model.generate_content(response.text)
        print(f"Model Reviewer Feedback:\n{response.text}")

        # Early Exit if "Looks Good"
        if "Looks Good".lower() in response.text.lower():
            print("Looks Good! Exiting the loop.")
            break

        # Update input for next iteration
        input_text = response.text

    return chat_history[-1]['content']  # Return the last model output

# Main Execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Self Refine Iterator')
    parser.add_argument('-o', dest='outfile', required=True,
                        action='store', help='Output file')
    parser.add_argument('-i', dest='infile', required=True,
                        action='store', help='Input file')
    parser.add_argument('--domain', dest='domain', required=True,
                        action='store', choices={'hackathon_idea_refine', 'cfp_submission_refine'},
                        help='Which domain to run? (hackathon_idea_refine or cfp_submission_refine)')
    args = parser.parse_args()

    try:
        with open(args.infile, 'r') as f:
            input_text = f.read()
    except FileNotFoundError:
        print(f"Error: Input file not found: {args.infile}")
        exit(1)

    final_result = run_model_iteration(args.domain, input_text)

    with open(args.outfile, 'w') as f:
        f.write(final_result)

    print(f"Output written to: {args.outfile}")
