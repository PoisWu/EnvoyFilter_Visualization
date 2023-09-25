class FilterChainMatch:
    def __init__(self, config_filterChainMatch):
        """
        config_filterChainMatch follow the structure:
        https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/listener/v3/listener_components.proto#config-listener-v3-filterchainmatch
        """

        # Destination port (Uint32Value)
        try:
            self.destination_port = config_filterChainMatch["destination_port"]
        except:
            self.destination_port = ""

        # prefix_ranges (repeated CidrRange)
        try:
            self.prefix_ranges = config_filterChainMatch["prefix_ranges"]
        except:
            self.prefix_ranges = ""

        # direct_source_prefix_ranges (repeaded CidrRange)
        try:
            self.direct_source_prefix_ranges = config_filterChainMatch[
                "direct_source_prefix_ranges"
            ]
        except:
            self.direct_source_prefix_ranges = ""

        # source_type (ConnectionSourceType)
        try:
            self.source_type = config_filterChainMatch["source_type"]
        except:
            self.source_type = ""

        # source_prefix_ranges (repeaded CidrRtange)
        try:
            self.source_prefix_ranges = config_filterChainMatch["source_prefix_ranges"]
        except:
            self.source_prefix_ranges = ""

        # source_ports (repeated unint32)
        try:
            self.source_ports = config_filterChainMatch["source_ports"]
        except:
            self.source_ports = ""

        # server_names (repeated string)
        try:
            self.server_names = config_filterChainMatch["server_names"]
        except:
            self.server_names = ""

        # transport_protocol (string)
        try:
            self.transport_protocol = config_filterChainMatch["transport_protocol"]
        except:
            self.transport_protocol = ""

        # application_protocols (repeated string)
        try:
            self.application_protocols = config_filterChainMatch[
                "application_protocols"
            ]
        except:
            self.application_protocols = ""

    def __str__(self):
        toStr = ""
        try:
            for server_name in self.server_names:
                toStr += server_name
                toStr += ","
        except:
            pass

        toStr += "|"
        try:
            for application_protocol in self.application_protocols:
                toStr += application_protocol
                toStr += ","
        except:
            pass

        toStr += "|"
        toStr += self.transport_protocol
        toStr += "|"
        try:
            for source_prefix_range in self.source_prefix_ranges:
                toStr += cidrRange_to_string(source_prefix_range)
                toStr += ","
        except:
            pass

        toStr += "|"
        try:
            for source_port in self.source_ports:
                toStr += str(source_port)
                toStr += ","
        except:
            pass

        toStr += "|"

        try:
            for source_port in self.source_ports:
                toStr += str(source_port)
                toStr += ","
        except:
            pass
        toStr += "|"
        try:
            for prefix_range in self.prefix_ranges:
                toStr += cidrRange_to_string(source_prefix_range)
                toStr += ","
        except:
            pass
        toStr += "|"
        toStr += str(self.destination_port)

        return toStr


# toString for cidrRange type
def cidrRange_to_string(config_cidrrange):
    address_prefix = config_cidrrange["address_prefix"]
    try:
        prefix_len = config_cidrrange["prefix_len"]
    except:
        prefix_len = 0
    return f"{address_prefix}/{prefix_len}"
