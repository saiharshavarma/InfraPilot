import subprocess
import logging
import json

logger = logging.getLogger(__name__)

# Check if the docker client is available
def is_docker_available():
    """Check if docker is available."""
    try:
        subprocess.check_output(["docker", "version", "--format", "{{json .}}"], stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_docker_info():
    """Get information about the Docker installation."""
    try:
        result = subprocess.check_output(["docker", "info", "--format", "{{json .}}"], 
                                        stderr=subprocess.PIPE, 
                                        universal_newlines=True)
        return json.loads(result)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logger.error(f"Error getting Docker info: {e}")
        return {"error": str(e)}