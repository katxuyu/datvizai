from openai import OpenAI
import os
import logging
import json
import tiktoken

logger = logging.getLogger('app_logger')

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORGANIZATION_ID")
)
def calculate_prompt_credits(prompt_text, model="gpt-4o-2024-08-06"):
    """
    Calculate the token count for the given prompt text using the OpenAI model.
    """
    try:
        # Load the encoding for the model
        encoding = tiktoken.encoding_for_model(model)
        # Encode the prompt and calculate the number of tokens
        token_count = len(encoding.encode(prompt_text))
        logger.info(f"Token count for the prompt: {token_count}")
        return token_count/100
    except Exception as e:
        logger.error(f"Error calculating prompt credits: {str(e)}")
        raise

def query_openai(filename, data):
    """
    Queries OpenAI to analyze the table and provide insights, including:
    - Insights about the table.
    - Five prompt suggestions for data analysis visualization.
    """
    try:
        # Prepare the prompt for OpenAI
        prompt = (
            f"Analyze the following tabular data from the file '{filename}' and provide the following details:\n"
            f"1. Insights about the table (one sentense long). \n"
            f"2. Five prompt suggestions for data analysis visualization.\n\n"
            f"Data Preview:\n{data[:5]}"  # Preview first 5 rows
        )
        
        # Use OpenAI ChatCompletion with the correct response format
        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in data analysis and provide structured JSON outputs."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "data_analysis",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "insights": {
                                "description": "General insights about the table",
                                "type": "string"
                            },
                            "prompt_suggestions": {
                                "description": "Five suggestions for data analysis or visualization",
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "minItems": 5,
                                "maxItems": 5
                            }
                        },
                        "required": ["insights", "prompt_suggestions"],
                        "additionalProperties": False
                    }
                }
            }
        )
        # Calculate real prompt credits
        prompt_credits = calculate_prompt_credits(prompt)
        # Extract and return the structured response
        result = response.choices[0].message.content  # Use the .content attribute
        logger.info(f"OpenAI query successful for file: {prompt_credits} {filename}")
        return (result, prompt_credits)

    except Exception as e:
        logger.error(f"Error querying OpenAI for file {filename}: {str(e)}")
        return {'error': f"Failed to query OpenAI for file {filename}. Reason: {str(e)}"}

def generate_graph_json(user_prompt, combined_data):
    """
    Directly generates a Plotly graph JSON and metadata based on the user's prompt and dataset using OpenAI.
    Includes validation for all chart types and tables supported by Plotly.
    """
    try:
        # Combine tables into a JSON string
        data_as_json = json.dumps(combined_data, indent=2)

        # Construct the refined prompt
        defined_prompt = (
            f"Validate the user's prompt: '{user_prompt}' for creating graphs or tables using Plotly. "
            f"The graph or table should use the following JSON data:\n\n"
            f"{data_as_json}\n\n"
            "Perform the following steps:\n"
            "1. Check if the user's prompt specifies a valid graph or table type supported by Plotly.\n"
            "2. Check if the prompt references valid columns in the dataset: "
            f"{', '.join(set(col for row in combined_data for col in row.keys()))}.\n\n"
            "If the user's prompt mentions 'regression,' create a regression graph with:\n"
            "- A scatter plot of the data points.\n"
            "- A regression line fitted to the data.\n"
            "- Statistical metrics such as R-squared, p-value, and regression equation displayed beautifully within the graph.\n"
            "- Display these metrics in an annotation box on the graph with a semi-transparent background.\n"
            "- Use clear and visually appealing formatting for the annotation (e.g., a light background, rounded corners, and a professional font).\n\n"
            "For 'hypothesis testing,' generate a Plotly table JSON object that displays:\n"
            "- Key statistical results (e.g., t-statistic, p-value, confidence intervals).\n"
            "- A conclusion about the hypothesis in a clearly labeled row.\n"
            "- Ensure the table layout is visually appealing, with alternating row colors and bold headers.\n\n"
            "For valid prompts, generate:\n"
            "1. 'graph_json' - the Plotly graph or table in JSON format. Ensure the graph title is strong and meaningful (min 5 words).\n"
            "2. 'title' - a suggested title for the graph or table. Do not start with 'The' or 'A'.\n"
            "3. 'description' - a one-sentence description of the graph or table.\n\n"
            "If the prompt is invalid, return:\n"
            "1. 'status': 'error'\n"
            "2. 'suggestions': A list of three alternative prompts to guide the user in specifying a valid request.\n\n"
            "Ensure the output includes all valid graphs or tables requested in the prompt.\n"
            "After generating the JSON, validate it to ensure that it is syntactically correct and complete. "
            "Do not return the result if it fails validation.\n\n"
            "Make sure to prettify the graph or table (e.g., titles, labels, colors, annotations, and fonts).\n"
        )

        # Call OpenAI ChatCompletion with the refined prompt
        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in data visualization using Plotly and JSON generation."
                },
                {
                    "role": "user",
                    "content": defined_prompt
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "plotly_graph_or_table_generation",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "description": "Status of the validation and graph generation",
                                "type": "string",
                                "enum": ["success", "error"]
                            },
                            "graphs": {
                                "description": "List of Plotly graph or table JSON objects and their metadata",
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "graph_json": {
                                            "description": "Plotly graph or table JSON object",
                                            "type": "object"
                                        },
                                        "title": {
                                            "description": "Suggested title for the graph or table",
                                            "type": "string"
                                        },
                                        "description": {
                                            "description": "One-sentence description of the graph or table",
                                            "type": "string"
                                        }
                                    },
                                    "required": ["graph_json", "title", "description"],
                                    "additionalProperties": False
                                }
                            },
                            "suggestions": {
                                "description": "Suggestions for improving the user's prompt",
                                "type": "array",
                                "items": {
                                    "type": "string"
                                }
                            }
                        },
                        "required": ["status"],
                        "additionalProperties": False
                    }
                }
            }
        )
        # Calculate real prompt credits
        prompt_credits = calculate_prompt_credits(defined_prompt)
        # Extract the response content
        result = response.choices[0].message.content
        logger.info(f"OpenAI graph or table generation completed successfully. Prompt cost: {prompt_credits}")
        return (result, prompt_credits)

    except Exception as e:
        logger.error(f"Error querying OpenAI for graph or table generation: {str(e)}")
        raise




def suggest_improvements(user_prompt):
    """
    Generates three suggested prompts for improving a vague or invalid user prompt.
    """
    try:
        defined_prompt = (
            f"The user's prompt: '{user_prompt}' was vague or invalid. Suggest three alternative prompts to improve the user's input."
        )

        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in crafting effective data visualization prompts."
                },
                {
                    "role": "user",
                    "content": defined_prompt
                }
            ]
        )

        suggestions = response.choices[0].message.content.split("\n")
        logger.info("Prompt improvement suggestions generated successfully.")
        return suggestions[:3]

    except Exception as e:
        logger.error(f"Error generating suggestions for prompt improvement: {str(e)}")
        return ["Try being more specific about the data to visualize.", 
                "Specify the type of chart or analysis you need.", 
                "Include details about the x-axis and y-axis data."]