#!/bin/bash

# Comptox AI Deployment Script (Updated 10/05/2023)

# Overview: This script automates the deployment of Comptox AI on an EC2
# instance. It can also be executed locally for testing purposes. Below are the
# key tasks performed by this script.

# The script currently supports only Linux and macOS.

# Key Deployment Tasks:

# 1. **Update from GitHub:**
#    - Fetches the latest master version of Comptox AI from GitHub, ensuring
#      your deployment is always up-to-date.

# 2. **Python Environment Setup:**
#    - Activates the Micromamba environment to manage Python dependencies and
#      avoid conflicts.

# 3. **Python Package Installation:**
#    - Upgrades pip and setuptools to their latest versions.
#    - Installs Python packages required for Comptox AI, including packages
#      necessary for building documentation.

# 4. **Sphinx Documentation:**
#    - Cleans any previous documentation builds.
#    - Generates Sphinx documentation, ensuring the successful creation of HTML
#      documentation.
#    - Verifies the presence of required documentation files.

# 5. **JavaScript Package Installation:**
#    - Installs JavaScript packages using npm, verifying the installation in
#      case others install Comptox AI.

# 6. **React App Integration:**
#    - Cleans any existing React app builds.
#    - Builds the React app and merges it with Sphinx documentation, creating a
#      cohesive final deployment.

# 7. **Nginx Server Update:**
#    - Copies and pastes the updated documentation and React app build to the
#      Nginx server root.
#    - Reloads the Nginx server to reflect the latest changes made in the
#      deployment.

# 8. **API Installation:**
#    - Installs necessary packages for the API.
#    - Stops the API service with a brief delay and then restarts it.

# === Dependencies ===

# This script relies on the following dependencies:
# - Micromamba: A package manager for managing Python environments.
# - npm: A package manager for JavaScript packages.
# - pm2: A process manager for running Node.js applications.

# Ensure you have these dependencies installed before running this script.

# To install Micromamba:
# - Follow the installation instructions at:
#   https://micromamba.snakepit.net/docs/tutorials/installation

# To install npm:
# - npm is typically bundled with Node.js. You can download Node.js from:
#   https://nodejs.org/en/download/

# To install pm2:
# - You can install pm2 using npm: npm install pm2 -g

# === Define Directories ===
# It is essential to configure the directory paths at the beginning of this
# script to match your environment before execution.
home_dir="/home/ec2-user"
comptox_ai_dir="${home_dir}/comptox_ai"
app_dir="${comptox_ai_dir}/web/packages/app"
api_dir="${comptox_ai_dir}/web/packages/api"
docs_dir="${comptox_ai_dir}/docs"
docs_build_dir="${docs_dir}/build/html"

# Define the web root directory, which is used as the root for Nginx in EC2 and
# for local testing.
web_root_dir="/usr/share/nginx/html" # For EC2
# web_root_dir="${home_dir}/merged_build" # For local testing

# Check if the required directories exist
required_dirs=("${home_dir}" "${comptox_ai_dir}" "${app_dir}" "${api_dir}" "${docs_dir}" "${docs_build_dir}" "${web_root_dir}")

for dir in "${required_dirs[@]}"; do
  if [ ! -d "${dir}" ]; then
    check_error 1 "Directory ${dir} does not exist."
  fi
done

# Check if the script has permissions to access the directories
if [ ! -r "${home_dir}" ] || [ ! -w "${home_dir}" ]; then
  check_error 1 "Script does not have read and write permissions for ${home_dir}."
fi

if [ ! -r "${comptox_ai_dir}" ] || [ ! -w "${comptox_ai_dir}" ]; then
  check_error 1 "Script does not have read and write permissions for ${comptox_ai_dir}."
fi

# === Define Functions ===

# Function to log errors or steps
log_message() {
  local message="${1}"
  local log_file="${2:-${deploy_run_log}}" # Use deploy_run_log as default log file if not provided
  local timestamp
  timestamp="$(date +'%Y_%m_%d_%H_%M_%S')"
  local log_message="${timestamp} - ${message}"

  # Log message to console
  echo "${log_message}"

  # Log message to the specified log file
  echo "${log_message}" >>"${log_file}"
}

# Function to check for errors and exit if an error occurs
check_error() {
  local exit_code="${1}"
  local error_message="${2}"
  if [ "${exit_code}" -ne 0 ]; then
    log_message "ERROR: ${error_message}. Exit code: ${exit_code}"
    exit 1
  fi
}

# === Set Environment Variables ===

# Function to detect the service manager and execute commands accordingly
detect_and_execute_service_manager() {
  local os_type
  os_type=$(uname)

  if [[ "${os_type}" == "Darwin" ]]; then
    # macOS uses launchctl
    SERVICE_MANAGER="launchctl"
  elif [[ "${os_type}" == "Linux" ]]; then
    # Linux uses systemctl
    SERVICE_MANAGER="systemctl"
  else
    # Handle unsupported OS
    check_error 1 "Unsupported operating system: ${os_type}"
  fi

  # Execute the provided command
  if [[ "${SERVICE_MANAGER}" == "systemctl" ]]; then
    sudo systemctl "$@"
  elif [[ "${SERVICE_MANAGER}" == "launchctl" ]]; then
    sudo launchctl "$@"
  else
    # Handle unsupported service manager
    check_error 1 "Unsupported service manager: ${SERVICE_MANAGER}"
  fi
}

# Set the Python virtual environment name to be used for Comptox AI
python_venv="comptox_ai_v1.1.3_py3.8"

# Define GitHub repository URL
github_repo_url="https://github.com/RomanoLab/comptox_ai.git"

# Timezone set to EST
export TZ="America/New_York"

# Define timestamp format
timestamp_format='%Y_%m_%d_%H_%M_%S'

# Generate a timestamp for the log file name and save it to timestamp.sh
current_time=$(date +"${timestamp_format}")
echo "#!/bin/bash" >timestamp.sh # timestamp.sh is to be used as a reference for creating the log file name of this specific deployment run.
echo "# Timestamp of when deploy script was run" >>timestamp.sh
echo "current_time=\"${current_time}\"" >>timestamp.sh

# Source the timestamp.sh file to set the current timestamp
source "${home_dir}/timestamp.sh"

# Define log directory
log_dir="${home_dir}/deploy_logs"
# Define error log file path
deploy_run_log="${log_dir}/deploy_run_log_${current_time}.txt"
# Define log file path
npm_install_log="${log_dir}/npm_install_times_${current_time}.log"

# Create the log directory if it doesn't exist
mkdir -p "${log_dir}"
check_error "${?}" "Failed to create the log directory ${log_dir}"

# Function to log npm package installation times
log_npm_install_time() {
  local package="${1}"
  local duration="${2}"
  echo "### ${package} ###" >>"${npm_install_log}"
  echo "Completed in ${duration} ms" >>"${npm_install_log}"
}

# === Main Code Execution Starts Here ===

cd "${comptox_ai_dir}" || exit

# === Step 1: Update from GitHub ===
log_message "Step 1: Update from GitHub started"

# Git pull
if ! git pull "${github_repo_url}"; then
  check_error 1 "Git pull failed"
fi

log_message "Step 1: Update from GitHub completed without error"

# === Step 2: Python Environment Setup ===
log_message "Step 2: Python Environment Setup started"

# Initialize the shell for Micromamba
eval "$(micromamba shell hook --shell bash)"
# Activate the Python environment
micromamba activate "${python_venv}"
check_error "${?}" "Failed to initialize the shell for Micromamba"

log_message "Step 2: Python Environment Setup completed without error"

# === Step 3: Python Package Installation ===
log_message "Step 3: Python Package Installation started"

# Install project dependencies using pip
pip install --upgrade pip setuptools
pip install . ".[docs]"
check_error "${?}" "Failed to install project dependencies using pip"

log_message "Step 3: Python Package Installation completed without error"

# === Step 4: Sphinx Documentation ===
log_message "Step 4: Sphinx Documentation started"

# Clean the previous doc build
cd "${docs_dir}" || exit # pwd: /home/ec2-user/comptox_ai/docs
rm -rf ./build

# Build Sphinx doc
make html
check_error "${?}" "Failed to build Sphinx documentation"

# Check if docs are properly built by checking necessary files
required_files=("index.html" "browse.html")
missing_files=()

for file in "${required_files[@]}"; do
  if [[ ! -f "${docs_build_dir}/${file}" ]]; then
    missing_files+=("${file}")
  fi
done

if [[ ${#missing_files[@]} -gt 0 ]]; then
  check_error 1 "These files are missing in '${docs_build_dir}': ${missing_files[*]}"
fi

log_message "Step 4: Sphinx Documentation completed without error"

# === Step 5: JavaScript Package Installation ===
log_message "Step 5: JavaScript Package Installation started"

# Install npm packages for the app dir
cd "${app_dir}" || exit               # pwd: /home/ec2-user/comptox_ai/web/packages/app
npm ci --verbose >"${deploy_run_log}" # Redirect verbose output to the log file
check_error "${?}" "npm ci for the app directory failed"

# Clean the previous React build
rm -rf ./build

if touch "${npm_install_log}"; then
  echo "Log file created: ${npm_install_log}"
else
  check_error 1 "Log file could not be created or already exists."
fi

# Show the contents of package.json for app directory
echo "Contents of app/package.json:"
cat "${app_dir}/package.json"

# Show the result of npm ci for the app directory
echo "npm ci exit code for app: ${?}"

log_message "Step 5: JavaScript Package Installation completed without error"

# === Step 6: React App Integration ===
log_message "Step 6: React App Integration started"

# Build the React app
npm run build

# Check if the required React app build files exist
cd "${comptox_ai_dir}" || exit # pwd: /home/ec2-user/comptox_ai/
if [ ! -f "${app_dir}/build/static/js/main.js" ] || [ ! -f "${app_dir}/build/static/css/main.css" ]; then
  check_error 1 "Required files (main.js or main.css) are missing in '${app_dir}/build/static'"
fi

log_message "Step 6: React App Integration completed without error"

# === Step 7: Nginx Server Update ===
log_message "Step 7: Nginx Server Update started"

# Copy JavaScript and CSS files from React app build to Sphinx documentation
cp "${app_dir}/build/static/js/"* "${docs_dir}/build/html/_static/js"
cp "${app_dir}/build/static/css/"* "${docs_dir}/build/html/_static/css"
check_error "${?}" "Failed to copy and paste the doc build files"

# Copy and paste the Sphinx documentation HTML files to the web root directory
cd / || exit # Navigate to the root directory (set web_root_dir accordingly)
cp -r "${docs_dir}/build/html/"* "${web_root_dir}"

# Check if copy and paste was done successfully
cd "${comptox_ai_dir}" || exit # pwd: /home/ec2-user/comptox_ai

if cmp --silent "${app_dir}/build/static/js/main.js" "${docs_dir}/build/html/_static/js/main.js" &&
  cmp --silent "${app_dir}/build/static/css/main.css" "${docs_dir}/build/html/_static/css/main.css"; then
  echo "Files were copied successfully."
else
  check_error 1 "Files were not copied successfully."
fi

# Reload Nginx and check if the webpage is working as intended
if [[ "${SERVICE_MANAGER}" == "systemctl" ]]; then
  # Use systemctl on Linux
  if sudo nginx -t; then
    sudo systemctl reload nginx
  else
    check_error 1 "Nginx configuration test failed. Reloading Nginx aborted."
  fi
else
  # Use launchctl on macOS
  if sudo nginx -t; then
    sudo nginx -s reload
  else
    check_error 1 "Nginx configuration test failed. Reloading Nginx aborted."
  fi
fi

# Check if the Nginx service is running (for both macOS and Linux)
if [[ "${SERVICE_MANAGER}" == "launchctl" ]]; then
  # For macOS using launchctl
  if launchctl list | grep -q "nginx"; then
    echo "Nginx is running."
  else
    check_error 1 "Nginx failed to run."
  fi
elif [[ "${SERVICE_MANAGER}" == "systemctl" ]]; then
  # For Linux using systemctl
  if sudo systemctl is-active --quiet nginx; then
    echo "Nginx is running."
  else
    check_error 1 "Nginx failed to run."
  fi
fi

log_message "Step 7: Nginx Server Update completed without error"

# === Step 8: API Installation ===
log_message "Step 8: API Installation started"

# Install packages needed for the API
cd "${api_dir}" || exit # pwd: /home/ec2-user/comptox_ai/web/packages/api

# Show the contents of package.json for the API dir
echo "Contents of api/package.json:"
cat "${api_dir}/package.json"

# Run npm ci for the API dir
cd "${api_dir}" || exit
npm ci
check_error "${?}" "npm ci for the API directory failed"

# Show the result of npm ci for the API dir
echo "npm ci exit code for API: ${?}"

# Stop API with a delay and start it again
if pm2 list | grep -q "api-app"; then
  pm2 stop api-app
  sleep 5 # Add a 5-second delay before starting it again
  check_error "${?}" "Failed to stop api-app"
  pm2 start app.js --name=api-app
  check_error "${?}" "Failed to start api-app"
else
  pm2 start app.js --name=api-app
  check_error "${?}" "Failed to start api-app"
fi

pm2 list
log_message "Step 8: API Installation completed without error"
