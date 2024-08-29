import time
from ping3 import ping
from plyer import notification

# Function to check the internet connection
def check_connection():
    try:
        # Ping Google's DNS server
        response_time = ping('8.8.8.8', timeout=1)  # Set timeout to 1 second
        if response_time is None:
            # No response, assume connection is lost
            notification.notify(
                title="Internet Connection",
                message="Connection Lost!",
                timeout=10
            )
        elif response_time > 0.5:
            # Response time is more than 500ms, assume slow connection
            notification.notify(
                title="Internet Connection",
                message=f"Slow Connection: {response_time:.2f} seconds",
                timeout=10
            )
        else:
            print(f"Connection is fine. Response time: {response_time:.2f} seconds")
    except Exception as e:
        # Handle any errors (e.g., no network or other issues)
        notification.notify(
            title="Internet Connection",
            message="Error: " + str(e),
            timeout=10
        )

# Main loop to check the connection periodically
while True:
    check_connection()
    time.sleep(20)  # Check every 20 seconds
