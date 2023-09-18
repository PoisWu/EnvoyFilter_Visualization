import sys
import draw
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="envoy configuration visualization")
    parser.add_argument(
        "ip_address", help="The IP address endpoint of enovy proxy", type=str
    )
    parser.add_argument(
        "port", help="The port of admin endpoint of envoy proxy", type=int
    )

    args = parser.parse_args()
    draw.create_diagram(args.ip_address, args.port)
