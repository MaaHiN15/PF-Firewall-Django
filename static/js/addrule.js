const alert_text = document.getElementById('alert-text');
const confirm_text = document.getElementById('confirm-text');
const successToastText = document.getElementById('succuessToastText');
const unsuccessToastText = document.getElementById('unsuccuessToastText');
const warningToastText = document.getElementById('warningToastText');
const alertModel = new bootstrap.Modal(document.getElementById('alertModel'));
const confirmModel = new bootstrap.Modal(document.getElementById('confirmModel'));
const successToast = new bootstrap.Toast(document.getElementById('successToast'));
const unsuccessToast = new bootstrap.Toast(document.getElementById('unsuccessToast'));
const warningToast = new bootstrap.Toast(document.getElementById('warningToast'))


function validateCidrIp(CidrIp) {
    const cidrIpRegex = /^((((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\/([1-9]|[1-2][0-9]|3[0-2])))$|^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|all)$/;
    return cidrIpRegex.test(CidrIp) ? true : false;
};

function validatePort(port) {
    const portRegex = /^((0|6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|6[0-4][0-9]{3}|[1-5][0-9]{4}|[1-9][0-9]{0,3})|all)$/;
    return portRegex.test(port) ? true : false;
}

function validateIP(ip) {
    const ipRegex = /^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$/;
    return ipRegex.test(ip) ? true : false;
}

function validateDomain(domain){
    const domainRegex = /^(?!:\/\/)([a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$/;
    return domainRegex.test(domain) ? true : false;
}

function multiselect(temp) {
    let arr = [];
    for (let i = 0; i < temp.options.length; i++) {
        if (temp.options[i].selected) {
            arr.push(temp.options[i].value);
        }
    };
    return arr;
};

async function fetchReq(url, data) {
    const response = fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json", 'Accept': 'application/json', 'X-CSRFToken': csrfToken },
        body: JSON.stringify(data)
    }).then(response => response.json())
        .then(data => {
            confirmModel.hide();
            if (data['status'] == 200) {
                successToastText.innerHTML = data['text']
                successToast.show();
            } else if (data['status']==300){
                warningToast.show();
                warningToastText.innerHTML = data['text']
            } else {
                unsuccessToast.show();
                unsuccessToastText.innerHTML = data['text']
            }
        })
}

function base_section_form(e) {
    e.preventDefault();

    const elem = new FormData(e.target);
    let data = {
        "blockPolicy": elem.get('set-blo-pol'),
        "debugLevel": elem.get('set-deb-lev'),
        "OptimLevel": elem.get('set-optim'),
        "rulesetOptim": elem.get('rule-set-optim'),
        "statePolicy": elem.get('state-pol'),
        "timeoutInterval": elem.get('timeout-interval')
    }

    confirm_text.innerHTML = `<table class="table table-hover">
    <tbody>
        <tr><td scope="row">Block Policy</th><td>${data.blockPolicy}</td></tr>
        <tr><td scope="row">Debug Level</td><td>${data.debugLevel}</td></tr>
        <tr><td scope="row">Optimization Level</td><td>${data.OptimLevel}</td></tr>
        <tr><td scope="row">Rule set Optimization level</td><td>${data.rulesetOptim}</td></tr>
        <tr><td scope="row">State Policy</td><td>${data.statePolicy}</td></tr>
        <tr><td scope="row">Timeout Interval</td><td>${data.timeoutInterval}</td></tr>
    </tbody>
    </table>
    `
    confirmModel.show();
    document.getElementById('confirmButton').addEventListener('click', async function () {
        await fetchReq('/api/baseForm', data);
    }, { once: true })
};

function tab_form(e) {
    e.preventDefault();
    const elem = new FormData(e.target);
    let ips = elem.get('tab-ips').split('\n');
    if (ips.some(i => !validateCidrIp(i))) {
        alert_text.innerHTML = "<p><strong class='text-danger' id='alert-text'>Enter valid CIDR / IP</strong></p>";
        alertModel.show();
        return;
    }
    let data = {
        "tabName": elem.get('tab-name'),
        "tabIps": ips
    };

    confirm_text.innerHTML = `<table class="table table-hover">
    <tbody>
        <tr><td scope="row">Table Name</th><td>${data.tabName}</td></tr>
        <tr><td scope="row">IP / CIDR</td><td>${data.tabIps}</td></tr>
    </tbody>
    </table>
    `
    confirmModel.show();
    document.getElementById('confirmButton').addEventListener('click', async function () {
        await fetchReq('/api/table', data);
    }, { once: true });
};

function filter_tab_form(e) {
    e.preventDefault();
    const elem = new FormData(e.target);

    let sourcePort = elem.get('sourcePort').split('\n');
    if (sourcePort.some(i => !validatePort(i))) {
        alert_text.innerHTML = "<p><strong class='text-danger' id='alert-text'>Enter valid Source Port</strong></p>";
        alertModel.show();
        return;
    };
    let destPort = elem.get('destPort').split('\n');
    if (destPort.some(i => !validatePort(i))) {
        alert_text.innerHTML = "<p><strong class='text-danger' id='alert-text'>Enter valid Destination Port</strong></p>";
        alertModel.show();
        return;
    };

    let data = {
        "action": elem.get('action'),
        "direction": elem.get('direction'),
        "interface": elem.get('interface'),
        "protocol": multiselect(e.target.elements['protocol']),
        "sourceAddress": multiselect(e.target.elements['sourceAddress']),
        "sourcePort": sourcePort,
        "destAddress": multiselect(e.target.elements['destAddress']),
        "destPort": destPort,
        "force": elem.get('forceCheck'),
        "log": elem.get('logCheck'),
        "type" : 'table'
    }
    confirm_text.innerHTML = `<table class="table table-hover">
    <tbody>
        <tr><td scope="row">Action</th><td>${data.action}</td></tr>
        <tr><td scope="row">Direction</td><td>${data.direction}</td></tr>
        <tr><td scope="row">Interfaces</td><td>${data.interface}</td></tr>
        <tr><td scope="row">Protocol</td><td>${data.protocol}</td></tr>
        <tr><td scope="row">Source Address</td><td>${data.sourceAddress}</td></tr>
        <tr><td scope="row">Source Port</td><td>${data.sourcePort}</td></tr>
        <tr><td scope="row">Destination Address</td><td>${data.destAddress}</td></tr>
        <tr><td scope="row">Destination Port</td><td>${data.destPort}</td></tr>
        <tr><td scope="row">Force</td><td>${data.force}</td></tr>
        <tr><td scope="row">Log</td><td>${data.log}</td></tr>
    </tbody>
    </table>
    `
    confirmModel.show();
    document.getElementById('confirmButton').addEventListener('click', async function () {
        await fetchReq('/api/filter', data);
    }, { once: true });
    e.target.reset();
}

function filter_man_form(e) {
    e.preventDefault();
    const elem = new FormData(e.target);

    let sourceAddress = elem.get('sourceAddress').split('\n');
    if (sourceAddress.some(i => !validateCidrIp(i))) {
        alert_text.innerHTML = "<p><strong class='text-danger' id='alert-text'>Enter valid Source Address / CIDR</strong></p>";
        alertModel.show();
        return;
    };

    let sourcePort = elem.get('sourcePort').split('\n');
    if (sourcePort.some(i => !validatePort(i))) {
        alert_text.innerHTML = "<p><strong class='text-danger' id='alert-text'>Enter valid Source Port</strong></p>";
        alertModel.show();
        return;
    };

    let destAddress = elem.get('destAddress').split('\n');
    if (destAddress.some(i => !validateCidrIp(i))) {
        alert_text.innerHTML = "<p><strong class='text-danger' id='alert-text'>Enter valid Destination Address / CIDR</strong></p>";
        alertModel.show();
        return;
    };

    let destPort = elem.get('destPort').split('\n');
    if (destPort.some(i => !validatePort(i))) {
        alert_text.innerHTML = "<p><strong class='text-danger' id='alert-text'>Enter valid Source Port </strong></p>";
        alertModel.show();
        return;
    };

    let data = {
        "action": elem.get('action'),
        "direction": elem.get('direction'),
        "interface": elem.get('interface'),
        "protocol": multiselect(e.target.elements['protocol']),
        "sourceAddress": sourceAddress,
        "sourcePort": sourcePort,
        "destAddress": destAddress,
        "destPort": destPort,
        "force": elem.get('forceCheck'),
        "log": elem.get('logCheck'),
        "type" : 'manual'
    };

    confirm_text.innerHTML = `<table class="table table-hover">
    <tbody>
        <tr><td scope="row">Action</th><td>${data.action}</td></tr>
        <tr><td scope="row">Direction</td><td>${data.direction}</td></tr>
        <tr><td scope="row">Interfaces</td><td>${data.interface}</td></tr>
        <tr><td scope="row">Protocol</td><td>${data.protocol}</td></tr>
        <tr><td scope="row">Source Address</td><td>${data.sourceAddress}</td></tr>
        <tr><td scope="row">Source Port</td><td>${data.sourcePort}</td></tr>
        <tr><td scope="row">Destination Address</td><td>${data.destAddress}</td></tr>
        <tr><td scope="row">Destination Port</td><td>${data.destPort}</td></tr>
        <tr><td scope="row">Force</td><td>${data.force}</td></tr>
        <tr><td scope="row">Log</td><td>${data.log}</td></tr>
    </tbody>
    </table>
    `
    confirmModel.show();
    document.getElementById('confirmButton').addEventListener('click', async function () {
        await fetchReq('/api/filter', data);
    }, { once: true });
    e.target.reset();
}

function nat_form(e) {
    e.preventDefault();
    const elem = new FormData(e.target);

    let sourceAddress = elem.get('sourceAddress').split('\n');
    if (sourceAddress.some(i => !validateCidrIp(i))) {
        alert_text.innerHTML = "<p><strong class='text-danger' id='alert-text'>Enter valid Source Address / CIDR</strong></p>";
        alertModel.show();
        return;
    };

    let sourcePort = elem.get('sourcePort').split('\n');
    if (sourcePort.some(i => !validatePort(i))) {
        alert_text.innerHTML = "<p><strong class='text-danger' id='alert-text'>Enter valid Source Port</strong></p>";
        alertModel.show();
        return;
    };

    let destAddress = elem.get('destAddress').split('\n');
    if (destAddress.some(i => !validateCidrIp(i))) {
        alert_text.innerHTML = "<p><strong class='text-danger' id='alert-text'>Enter valid Destination Address / CIDR</strong></p>";
        alertModel.show();
        return;
    };

    let destPort = elem.get('destPort').split('\n');
    if (destPort.some(i => !validatePort(i))) {
        alert_text.innerHTML = "<p><strong class='text-danger' id='alert-text'>Enter valid Source Port </strong></p>";
        alertModel.show();
        return;
    };

    if (!validateIP(elem.get('natIP'))) {
        alert_text.innerHTML = "<p><strong class='text-danger' id='alert-text'>Enter valid NAT Destination IP </strong></p>";
        alertModel.show();
        return;
    };

    let data = {
        "natChoose": elem.get('natChoose'),
        "interface": elem.get('interface'),
        "protocol": multiselect(e.target.elements['protocol']),
        "sourceAddress": sourceAddress,
        "sourcePort": sourcePort,
        "destAddress": destAddress,
        "destPort": destPort,
        "natIP": elem.get('natIP')
    };

    confirm_text.innerHTML = `<table class="table table-hover">
    <tbody>
        <tr><td scope="row">Nat or Binat</td><td>${data.natChoose}</td></tr>
        <tr><td scope="row">Interfaces</td><td>${data.interfaces}</td></tr>
        <tr><td scope="row">Protocol</td><td>${data.protocol}</td></tr>
        <tr><td scope="row">Source Address</td><td>${data.sourceAddress}</td></tr>
        <tr><td scope="row">Source Port</td><td>${data.sourcePort}</td></tr>
        <tr><td scope="row">Destination Address</td><td>${data.destAddress}</td></tr>
        <tr><td scope="row">Destination Port</td><td>${data.destPort}</td></tr>
        <tr><td scope="row">NAT IP</td><td>${data.natIP}</td></tr>
    </tbody>
    </table>
    `
    confirmModel.show();
    document.getElementById('confirmButton').addEventListener('click', async function () {
        await fetchReq('/api/nat', data);
    }, { once: true });
    e.target.reset();
};

function domain_form(e){
    e.preventDefault();
    const elem = new FormData(e.target);
    let domainName = elem.get('domain-name');
    if (!validateDomain(domainName)){
        alert_text.innerHTML = "<p><strong class='text-danger' id='alert-text'>Enter valid Domain name!!! </strong></p>";
        alertModel.show();
        return;
    }
    confirm_text.innerHTML = `<ul class="list-group list-group-flush"><li class="list-group-item">${domainName}</li></ul>`
    confirmModel.show();
    document.getElementById('confirmButton').addEventListener('click', async function () {
        confirmModel.hide();
        await fetchReq('/api/domain', {'name' : domainName});
    }, { once: true });    
    e.target.reset();
}


document.getElementById('base-section').addEventListener('submit', base_section_form)
document.getElementById('tab-form').addEventListener('submit', tab_form)
document.getElementById('fil-tab-form').addEventListener('submit', filter_tab_form)
document.getElementById('fil-man-form').addEventListener('submit', filter_man_form)
document.getElementById('nat-form').addEventListener('submit', nat_form)
document.getElementById('domain-form').addEventListener('submit', domain_form)