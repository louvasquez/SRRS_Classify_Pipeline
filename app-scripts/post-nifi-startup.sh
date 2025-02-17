
# TODO: switch to nipyapi


API_URL="https://$(hostname):${NIFI_WEB_HTTPS_PORT}/nifi-api"

get_nifi_token() {
    curl -sSk -X POST $API_URL'/access/token' \
        -H 'Content-Type: application/x-www-form-urlencoded' \
        -d "username=$SINGLE_USER_CREDENTIALS_USERNAME&password=$SINGLE_USER_CREDENTIALS_PASSWORD"
}

nicurl() {
    : "${TOKEN:=$(get_nifi_token)}"
    curl -Ssk -H "Authorization: Bearer $(get_nifi_token)" -X "$@"
}

clear_token() {
    unset TOKEN
}

wait_for_nifi() {
    while true; do
    if curl -skf $API_URL; then
        echo "[NIFI APP] NiFi is available! Done checking."
        break
    else
        echo "[NIFI APP] NiFi not available yet. Retrying..."
        sleep 5
    fi
    done
}

get_root_id() {
    nicurl GET \
        ${API_URL}/flow/process-groups/root \
        | jq -r '.processGroupFlow.id'
}

load_flow() {
    filename=$1
    root_id=$(get_root_id)
    nicurl POST \
        -H "Content-Type: multipart/form-data" \
        ${API_URL}/process-groups/${root_id}/process-groups/upload \
        -F 'groupName=SRRS' \
        -F 'positionX=0' \
        -F 'positionY=0' \
        -F 'clientId=nifi-app' \
        -F "groupId=${root_id}" \
        -F 'disconnectedNodeAcknowledged=false' \
        -F "file=@${filename}" > /tmp/nifiapp.out 2>&1
    if [[ $? -eq 0 ]]; then
        echo "[NIFI APP] SUCCESS creating flow"
        echo "[NIFI APP] flow ID: $(cat /tmp/nifiapp.out | jq -r '.id')"
    else
        echo "[NIFI APP] ERROR: FAILED loading flow from $filename" >&2
        cat /tmp/nifiapp.out >&2
    fi


}

echo "[NIFI APP] starting post startup"
wait_for_nifi
for flow in $NIFI_HOME/autoflows/*; do 
    load_flow $flow
done
echo "[NIFI APP] post startup complete"



