import draw
import argparse
import urllib.request, json


def load_config_from_url(ip_address: str, port: int):
    """Dowload envoy's configuration
    Args:
        ip_address (str): The IP address of admin API endpoint
        port (int): The port of admin API endpoint
    Returns:
        config_dump
    """

    with urllib.request.urlopen(f"http://{ip_address}:{port}/config_dump") as url:
        config_dump = json.load(url)
    return config_dump


def load_config_from_path(file_path: str):
    with open(file_path) as f:
        config_dump = json.load(f)
    return config_dump


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="envoy configuration visualization")
    subparsers = parser.add_subparsers()

    parser_url = subparsers.add_parser("url", help="url of admin endpoint of proxy")
    parser_file = subparsers.add_parser("path", help="path to the dump config file")

    parser_url.add_argument(
        "ip_address", help="The IP address endpoint of enovy proxy", type=str
    )
    parser_url.add_argument(
        "port", help="The port of admin endpoint of envoy proxy", type=int
    )

    parser_file.add_argument("path", type=str)

    args = parser.parse_args()

    try:
        config_dump = load_config_from_url(args.ip_address, args.port)
    except:
        config_dump = load_config_from_path(args.path)

    draw.create_diagram(config_dump)
