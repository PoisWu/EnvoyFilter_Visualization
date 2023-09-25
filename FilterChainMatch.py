class FilterChainMatch:
    def __init__(self, config_filterChainMatch):
        """
        config_filterChainMatch follow the structure:
        https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/listener/v3/listener_components.proto#config-listener-v3-filterchainmatch
        """

        # Destination port
        try:
            self.destination_port = config_filterChainMatch["destination_port"]
        except:
            self.destination_port = ""

        # prefix_ranges
        try:
            self.prefix_ranges = config_filterChainMatch["prefix_ranges"]
        except:
            self.prefix_ranges = ""

        # direct_source_prefix_ranges
        try:
            self.direct_source_prefix_ranges = config_filterChainMatch[
                "direct_source_prefix_ranges"
            ]
        except:
            self.direct_source_prefix_ranges = ""

        # source_type
        try:
            self.source_type = config_filterChainMatch["source_type"]
        except:
            self.source_type = ""

        # source_prefix_ranges
        try:
            self.source_prefix_ranges = config_filterChainMatch["source_prefix_ranges"]
        except:
            self.source_prefix_ranges = ""

        # source_ports
        try:
            self.source_ports = config_filterChainMatch["source_ports"]
        except:
            self.source_ports = ""

        # server_names
        try:
            self.server_names = config_filterChainMatch["server_names"]
        except:
            self.server_names = ""

        # transport_protocol
        try:
            self.transport_protocol = config_filterChainMatch["transport_protocol"]
        except:
            self.transport_protocol = ""

        # application_protocols
        try:
            self.application_protocols = config_filterChainMatch[
                "application_protocols"
            ]
        except:
            self.application_protocols = ""

    def __str__(self):
        return 0


def cidrRange_to_string(config_cidrrange):
    address_prefix = config_cidrrange["address_prefix"]
    try:
        prefix_len = config_cidrrange["prefix_len"]
    except:
        prefix_len = 0
    return f"{address_prefix}/{prefix_len}"
