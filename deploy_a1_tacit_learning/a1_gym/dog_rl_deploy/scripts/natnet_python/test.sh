cleanup() {
    echo "Exiting..."
    # Use pkill with a pattern that matches your Python scripts but not this script or grep itself.
    sudo pkill -f optitrack_publisher.py
    sudo pkill -f optitrack_subscriber.py
}

# Setup trap to call cleanup function upon script exit
trap cleanup EXIT

echo "Starting..."
# Start the Python scripts in the background
python3 optitrack_publisher.py &
python3 optitrack_subscriber.py &

# Wait for background processes to finish
wait

echo "End."