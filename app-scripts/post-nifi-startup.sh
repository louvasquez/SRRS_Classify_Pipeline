
wait_for_nifi() {
    while true; do
    if curl -sf https://$(hostname):${NIFI_WEB_HTTPS_PORT}/nifi; then
        echo "NiFi is available! Exiting loop."
        break
    else
        echo "NiFi not available yet. Retrying..."
        sleep 5
    fi
    done
}


