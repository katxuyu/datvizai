from flask import Blueprint, request, jsonify, send_file
import os
import hashlib
from werkzeug.utils import secure_filename
from .database import Database, encrypt, hash_ip
from .services import parse_csv
from .logging_config import logger
from .helpers.openai_helper import query_openai, generate_graph_json, suggest_improvements
from .helpers.file_helper import validate_csv_file, parse_csv, get_file_statistics
import pandas as pd
import plotly.utils
import json
from functools import wraps
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

main_bp = Blueprint('main', __name__)

# Initialize the database
db = Database()

# Load AUTH_TOKEN from environment
AUTH_TOKEN = os.getenv("AUTH_TOKEN")

def token_required(f):
    """
    Decorator to ensure the request contains a valid authorization token.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.debug(f)
        token = request.headers.get('Authorization')
        if not token:
            logger.error("Authorization token missing.")
            return jsonify({'error': 'Authorization token is required.'}), 401
        if token != f"Bearer {AUTH_TOKEN}":
            logger.error(f"Invalid authorization token. {AUTH_TOKEN}")
            return jsonify({'error': 'Invalid authorization token.'}), 403
        return f(*args, **kwargs)
    return decorated_function

@main_bp.route('/upload', methods=['POST'])
@token_required
def upload_files():
    """
    Processes multiple CSV files in memory, validates their format,
    generates file statistics, deducts prompt credits, and includes insights and prompt suggestions directly.
    """
    MAX_TOTAL_SIZE_MB = 500  # Maximum allowed size in MB
    MAX_TOTAL_SIZE_BYTES = MAX_TOTAL_SIZE_MB * 1024 * 1024

    uuid = request.form.get('uuid')  # Retrieve the UUID from the request form

    if not uuid:
        logger.error("No UUID provided in the request.")
        return jsonify({'error': 'UUID is required.'}), 400

    logger.info(f"Received request to process files in memory. UUID: {uuid}")

    if 'files' not in request.files:
        logger.error(f"No files part in the request. UUID: {uuid}")
        return jsonify({'error': 'No files part in the request.'}), 400

    files = request.files.getlist('files')
    if not files:
        logger.error(f"No files selected for processing. UUID: {uuid}")
        return jsonify({'error': 'No files selected for processing.'}), 400

    # Calculate total size of all files
    total_size = sum(
        file.content_length for file in files if file.content_length is not None)
    if total_size > MAX_TOTAL_SIZE_BYTES:
        logger.error(f"Total file size exceeds 500MB. Total size: {total_size} bytes. UUID: {uuid}")
        return jsonify({'error': 'Total file size exceeds 500MB. Please upload files smaller than 500MB in total.'}), 400

    # Retrieve user credits from the database
    user = db.query(
        "SELECT available_credits FROM users WHERE uuid = %s", (uuid,))
    if not user:
        logger.error(f"User not found. UUID: {uuid}")
        return jsonify({'error': 'User not found.'}), 404

    available_credits = user[0]['available_credits']

    total_prompt_credits_used = 0
    processed_files = []

    for file in files:
        if file.filename == '':
            logger.warning(f"A file with no name was skipped. UUID: {uuid}")
            continue

        if not validate_csv_file(file.filename):
            logger.warning(f"Invalid file format skipped: {file.filename}. UUID: {uuid}")
            continue

        try:
            # Parse the CSV file directly from the file stream
            logger.debug(f"Processing file in memory: {file.filename}. UUID: {uuid}")
            df = pd.read_csv(file)  # Read CSV from the file stream

            # Generate file statistics
            file_stats = get_file_statistics(df)

            # Extract file data
            data = df.to_dict(orient='records')

            # Query OpenAI with the processed data for insights and prompt suggestions
            openai_result, prompt_credits = query_openai(file.filename, data)
            # Check if the user has enough credits
            if available_credits < prompt_credits:
                logger.error(f"Insufficient credits. UUID: {uuid}, Available: {available_credits}, Required: {prompt_credits}")
                return jsonify({'error': 'Insufficient credits. Subscribe to our Pro Version!'}), 201

            # Parse OpenAI response if it's a JSON string
            try:
                openai_result_dict = json.loads(openai_result)
                insights = openai_result_dict.get(
                    "insights", "No insights available.")
                prompt_suggestions = openai_result_dict.get(
                    "prompt_suggestions", [])
                # Calculate prompt credits used (assume each prompt costs 50 credits)
                total_prompt_credits_used += prompt_credits
            except json.JSONDecodeError:
                insights = "No insights available due to OpenAI response format issue."
                prompt_suggestions = []

            # Collect results
            processed_files.append({
                "file_name": file.filename,
                "statistics": file_stats,
                "data": data,
                "insights": insights,
                "prompt_suggestions": prompt_suggestions
            })

        except Exception as e:
            logger.exception(f"Error processing file in memory: {file.filename}. Reason: {str(e)}. UUID: {uuid}")
            processed_files.append({
                "file_name": file.filename,
                "error": f"Failed to process the file: {str(e)}"
            })

    # Deduct credits from the database
    if total_prompt_credits_used > available_credits:
        logger.error(f"Insufficient credits. UUID: {uuid}, Required: {total_prompt_credits_used}, Available: {available_credits}")
        return jsonify({'error': 'Insufficient credits.'}), 400

    available_credits -= total_prompt_credits_used
    db.query("UPDATE users SET available_credits = %s WHERE uuid = %s",
             (available_credits, uuid))

    logger.info(f"Credits deducted. UUID: {uuid}, Used: {total_prompt_credits_used}, Remaining: {available_credits}")

    if not processed_files:
        logger.error(f"No valid files were processed. UUID: {uuid}")
        return jsonify({'error': 'No valid files were uploaded or processed.'}), 400

    return jsonify({
        'message': 'Files processed successfully in memory',
        'uuid': uuid,
        'files': processed_files,
        'available_credits': available_credits
    }), 200


@main_bp.route('/user/register', methods=['POST'])
@token_required
def register_user():
    """
    Registers a user based on email and public IP.
    Hashes and stores email and IP, generates a UUID, and reuses UUID if user exists.
    """
    FREE_PROMPT_CREDITS = int(
        os.getenv("FREE_PROMPT_CREDITS", 3000))  # Default to 3000 if not set

    data = request.json
    email = data.get('email')
    public_ip = data.get('public_ip')

    if not email or not public_ip:
        logger.error("Email or public IP missing in the request.")
        return jsonify({'error': 'Email and public IP are required.'}), 400

    try:
        # Hash the IP for consistent storage
        hashed_ip = hash_ip(public_ip)

        # Encrypt the email (email encryption can stay because matching email isn't required)
        encrypted_email = encrypt(email)

        # Check for existing user by email or hashed IP
        existing_user = db.query(
            "SELECT uuid, available_credits FROM users WHERE email = %s OR ip = %s",
            (encrypted_email, hashed_ip)
        )

        if existing_user:
            user_uuid = existing_user[0]['uuid']
            available_credits = existing_user[0]['available_credits']
            logger.info(f"Existing user found. UUID: {user_uuid}, Credits: {available_credits}")
            return jsonify({
                'status': 'Existing',
                'uuid': user_uuid,
                'available_credits': available_credits
            }), 200

        # Generate a new UUID for the user
        user_uuid = hashlib.sha256(f"{email}{public_ip}".encode()).hexdigest()

        # Insert new user into the database with FREE_PROMPT_CREDITS
        db.query(
            "INSERT INTO users (email, ip, uuid, available_credits) VALUES (%s, %s, %s, %s)",
            (encrypted_email, hashed_ip, user_uuid, FREE_PROMPT_CREDITS)
        )
        logger.info(f"New user registered. UUID: {user_uuid}, Initial Credits: {FREE_PROMPT_CREDITS}")

        return jsonify({
            'status': 'New',
            'uuid': user_uuid,
            'available_credits': FREE_PROMPT_CREDITS
        }), 201

    except Exception as e:
        logger.exception(f"Error registering user: {str(e)}")
        return jsonify({'error': 'Failed to register user.'}), 500


@main_bp.route('/user/check', methods=['POST'])
@token_required
def check_user():
    """
    Checks if a user exists based on their hashed public IP.
    Returns 'Existing' if the hashed IP is found, otherwise 'New'.
    """
    data = request.json
    public_ip = data.get('public_ip')

    if not public_ip:
        logger.error("Public IP is missing in the request.")
        return jsonify({'error': 'Public IP is required.'}), 400

    try:
        # Hash the public IP for consistent storage and comparison
        hashed_ip = hash_ip(public_ip)

        # Check if the hashed IP exists in the database
        existing_user = db.query(
            "SELECT uuid FROM users WHERE ip = %s",
            (hashed_ip,)
        )

        if existing_user:
            logger.info(f"Existing user found with IP: {public_ip}")
            return jsonify({'status': 'Existing', 'uuid': existing_user[0]['uuid']}), 200
        else:
            logger.info(f"New user detected with IP: {public_ip}")
            return jsonify({'status': 'New'}), 200

    except Exception as e:
        logger.exception(f"Error checking user status: {str(e)}")
        return jsonify({'error': 'Failed to check user status.'}), 500


@main_bp.route('/generate_graph', methods=['POST'])
@token_required
def generate_graph():
    """
    Generates a list of Plotly graph JSON objects and metadata directly using OpenAI based on the user prompt and input data.
    Deducts credits after a successful generation or provides suggestions for vague/invalid prompts.
    """
    prompt_credits = 100  # Define the credit cost per prompt

    logger.info("Processing request to generate graph.")
    data = request.json
    # logger.debug(f"Received request payload: {json.dumps(data, indent=2)}")

    uuid = data.get('uuid')
    prompt = data.get('prompt')
    # Assuming files is a list of dictionaries with `data` and `file_name`
    files = data.get('files')

    if not uuid or not prompt or not files:
        logger.error("UUID, prompt, or files missing in the request.")
        return jsonify({'error': 'UUID, prompt, and files are required.'}), 400

    try:
        # Retrieve user credits from the database
        logger.info(f"Retrieving credits for UUID: {uuid}")
        user = db.query(
            "SELECT available_credits FROM users WHERE uuid = %s", (uuid,))
        if not user:
            logger.error(f"User not found. UUID: {uuid}")
            return jsonify({'error': 'User not found.'}), 404

        available_credits = user[0]['available_credits']
        logger.info(f"User found. UUID: {uuid}, Available Credits: {available_credits}")


        # Combine data from all files into a single dataset for analysis
        logger.info("Combining data from uploaded files.")
        combined_data = []
        for file in files:
            logger.debug(f"Processing file: {file.get('file_name')}")
            combined_data.extend(file['data'])

        logger.debug(f"Combined data size: {len(combined_data)} records")

        # Call the OpenAI function to generate the graphs JSON
        logger.info(
            f"Sending request to OpenAI for graph generation. Prompt: {prompt}")
        openai_response, prompt_credits = generate_graph_json(prompt, combined_data)
        logger.debug(f"OpenAI response: {openai_response}")
        # Check if the user has enough credits
        if available_credits < prompt_credits:
            logger.error(f"Insufficient credits. UUID: {uuid}, Available: {available_credits}, Required: {prompt_credits}")
            return jsonify({'error': 'Insufficient credits. Subscribe to our Pro Version!'}), 201

        # Parse OpenAI response
        logger.info("Parsing OpenAI response.")
        openai_result = json.loads(openai_response)
        status = openai_result.get("status")

        if status == "error":
            suggestions = openai_result.get("suggestions", [])
            logger.warning(f"Prompt validation failed. UUID: {uuid}, Suggestions: {suggestions}")
            return jsonify({
                'status': 'error',
                'message': 'The prompt was vague or invalid. Please try one of the suggested prompts.',
                'suggestions': suggestions
            }), 200

        # Success case: Extract graphs details
        graphs = openai_result.get("graphs", [])
        if not graphs:
            logger.error(f"No graphs generated. UUID: {uuid}")
            return jsonify({'error': 'No graphs generated from the provided prompt.'}), 500

        # Parse each graph's JSON string into a Python dictionary
        parsed_graphs = []
        for graph in graphs:
            try:
                graph_json = graph.get("graph_json")

                # Check and handle stringified JSON
                if isinstance(graph_json, str):
                    graph_json = json.loads(graph_json)  # Convert from string to dictionary

                # Validate if graph_json is now a dictionary
                if not isinstance(graph_json, dict):
                    raise ValueError(f"Invalid graph JSON format: {graph_json}")

                # Check if the graph type is "table"
                if graph_json.get("type") == "table":
                    # Add a footer to the table
                    footer_annotation = {
                        "text": "Source: DatViz AI",
                        "align": "center",
                        "font": {"size": 12, "color": "blue"},
                        "fill": {"color": "#f0f0f0"},
                        "line": {"color": "black", "width": 1}
                    }
                    if "cells" in graph_json:
                        graph_json["cells"]["values"].append(["Source: DatViz AI"])  # Add source row
                        graph_json["cells"]["align"] = "center"
                        graph_json["cells"]["fill"]["color"]= "#f0f0f0"

                else:
                    # Add source annotation to the layout for non-table graphs
                    graph_json['layout']['annotations'] = graph_json['layout'].get('annotations', []) + [{
                        'text': 'Source: DatViz AI',
                        'xref': 'paper',
                        'yref': 'paper',
                        'x': 1,
                        'y': 1,
                        'xanchor': 'right',
                        'yanchor': 'top',
                        'showarrow': False,
                        'font': {'size': 12, 'color': 'blue'}
                    }]

                    # Enable fullscreen mode (Plotly's responsive layout mode with fullscreen button)
                    graph_json['layout']['autosize'] = True
                    graph_json['layout']['responsive'] = True
                    graph_json['layout']['modebar'] = graph_json['layout'].get('modebar', {})
                    # Add interactable legend
                    graph_json['layout']['legend'] = {
                        'title': {'text': 'Legend'},
                        'orientation': 'h',
                        'x': 0,
                        'y': -0.2,
                        'bgcolor': 'rgba(255,255,255,0.5)'
                    }

                    # Add dynamic color customization option
                    if "custom_colors" in data:
                        graph_json['layout']['colorway'] = data["custom_colors"]
                    else:
                        graph_json['layout']['colorway'] = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A']

                    # Enable interactable legend
                    graph_json['layout']['showlegend'] = True

                parsed_graphs.append({
                    "graph": graph_json,
                    "title": graph.get("title", "Graph"),
                    "description": graph.get("description", "No description available.")
                })
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse graph JSON for UUID: {uuid}, Error: {str(e)}, {graph}")
                return jsonify({'error': 'Failed to parse one or more generated graphs.'}), 500




        # Deduct credits from the database
        available_credits -= prompt_credits
        logger.info(f"Deducting credits. UUID: {uuid}, Used: {prompt_credits}, Remaining: {available_credits}")
        db.query("UPDATE users SET available_credits = %s WHERE uuid = %s",
                 (available_credits, uuid))

        logger.info(
            f"Graph generation completed successfully for UUID: {uuid}")
        return jsonify({
            'status': 'success',
            'uuid': uuid,
            'graphs': parsed_graphs,  # Returning a list of parsed graphs
            'available_credits': available_credits
        }), 200

    except Exception as e:
        logger.exception(f"Error generating graph for UUID: {uuid}. Reason: {str(e)}")
        return jsonify({'error': 'Failed to generate graph.'}), 500
