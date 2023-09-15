class Type:
    LISTENERS_CONFIG_DUMP_T = "type.googleapis.com/envoy.admin.v3.ListenersConfigDump"
    LISTENER_T = "type.googleapis.com/envoy.config.listener.v3.Listener"
    HCM_FILTER_T = "type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager"
    WASM_FILTER_T = "type.googleapis.com/envoy.extensions.filters.http.wasm.v3.Wasm"
    ROUTER_FILTER_T = (
        "type.googleapis.com/envoy.extensions.filters.http.router.v3.Router"
    )
    UDPA_T = "type.googleapis.com/udpa.type.v1.TypedStruct"
