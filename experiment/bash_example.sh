sed -i '239s/.*/<script src="http2_priority.js"><\/script>/' index.html
scenes='garden bicycle treehill bonsai drjohnson flowers kitchen playroom room stump train truck'
#scenes='garden bicycle '
# Path to the file
file="http2_priority.js"

for scene in $scenes; do
    scene_name="\tlet scene_name = '${scene}'"

    sed -i "1154s#.*#${scene_name}#" "${file}"
    sed -i "1481s#.*#${scene_name}#" "${file}"

    google-chrome --new-window https://localhost:8081/index.html
    sleep 120
    window_id=$(wmctrl -l | grep "WebGL Gaussian Splat Viewer" | awk '{print $1}')
    wmctrl -ic "$window_id"
done

