import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
print("Reading credentials from .env file...")

# A dictionary to hold the JSON structure
service_account_info = {}

# List of expected environment variables for the service account
# The script will read these from your .env file
env_vars_to_read = [
    "GOOGLE_CLOUD_TYPE",
    "GOOGLE_CLOUD_PROJECT_ID",  # Renamed for clarity from GOOGLE_CLOUD_PROJECT
    "GOOGLE_CLOUD_PRIVATE_KEY_ID",
    "GOOGLE_CLOUD_PRIVATE_KEY",
    "GOOGLE_CLOUD_CLIENT_EMAIL",
    "GOOGLE_CLOUD_CLIENT_ID",
    "GOOGLE_CLOUD_AUTH_URI",
    "GOOGLE_CLOUD_TOKEN_URI",
    "GOOGLE_CLOUD_AUTH_PROVIDER_X509_CERT_URL",
    "GOOGLE_CLOUD_CLIENT_X509_CERT_URL",
    "GOOGLE_CLOUD_UNIVERSE_DOMAIN",
]

# Read each variable from the environment and build the dictionary
all_vars_found = True
for var in env_vars_to_read:
    value = os.getenv(var)
    if value:
        # The private key needs special handling to preserve newlines
        if var == "GOOGLE_CLOUD_PRIVATE_KEY":
            service_account_info[var.replace("GOOGLE_CLOUD_", "").lower()] = (
                value.replace("\\n", "\n")
            )
        else:
            # Convert the variable name to the JSON key format (e.g., "project_id")
            service_account_info[var.replace("GOOGLE_CLOUD_", "").lower()] = value
    else:
        print(f"Error: Environment variable '{var}' not found in .env file.")
        all_vars_found = False

# Only write the file if all variables were found
if all_vars_found:
    output_filename = "service-account.json"
    with open(output_filename, "w") as json_file:
        # Use json.dump to write the dictionary to the file with nice formatting
        json.dump(service_account_info, json_file, indent=2)

    print(f"Successfully created '{output_filename}'")
    print(
        "\nYou can now set your GOOGLE_APPLICATION_CREDENTIALS environment variable to point to this file."
    )
else:
    print("\nFile creation failed due to missing variables.")
