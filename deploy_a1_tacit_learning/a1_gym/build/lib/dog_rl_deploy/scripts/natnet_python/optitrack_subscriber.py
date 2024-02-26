import lcm
from lcm_types import optitrack_lcmt

def message_handler(channel, data):
    msg = optitrack_lcmt.decode(data)
    print(f"Received message on channel {channel}")
    print(f"target_yaw: {msg.target_yaw}")

def main():
    lc = lcm.LCM()
    subscription = lc.subscribe("optitrack_channel", message_handler)
    counter = 0
    try:
        while True:
            lc.handle()
            counter += 1
    except KeyboardInterrupt:
        lc.unsubscribe(subscription)


if __name__ == "__main__":
    main()
