let spinner = document.getElementById('spinner');
var tabledata = [];
var delay = 0;
updateData();
updateDelay();

function updateDelay() {
    let req = new XMLHttpRequest();
    req.open('POST', '/get/delay', false);
    req.send();
    delay = parseInt(req.response);
    document.getElementById('delay').innerText = 'Set time (now is ' + delay.toString() + ')';
}

function setDelay(delay) {
    let req = new XMLHttpRequest();
    req.open('POST', '/set/delay?delay=' + delay.toString(), false);
    req.send();
}

function updateData() {
    let req = new XMLHttpRequest();
    req.open('POST', '/selfcheck/all', false);
    req.send();
    tabledata = JSON.parse(req.response);
}

var table = new Tabulator("#copters-table", {
    data: tabledata,
    reactiveData: true,
    selectable: true,
    layout: "fitColumns",
    columns: [
        {title: "Name", field: "name"},
        {title: "Animation id", field: "anim_id"},
        {title: "Batt voltage", field: "batt_voltage"},
        {title: "Cell voltage", field: "cell_voltage"},
        {title: "Selfcheck", field: "selfcheck"},
        {title: "Time delta", field: "time"},
    ],
});

function refreshRows(selectedRows) {
    spinner.style.display = 'inline-block';
    setTimeout(function () {
        selectedRows.forEach(function (element) {
            let req = new XMLHttpRequest();
            req.open('POST', '/selfcheck/selected?ip=' + element._row.data.ip, false);
            req.send();
            element.deselect();
            let response = JSON.parse(req.response);
            Object.keys(response).forEach(function (item) {
                element._row.data[item] = response[item];
            });
        });
        spinner.style.display = 'none';
    }, 20);
}

function refreshSelected() {
    refreshRows(table.getSelectedRows());
}

function refreshAll() {
    refreshRows(table.getRows());
}

function selectAll() {
    table.getRows().forEach(function (element) {
        element.select();
    });
}

function deselectAll() {
    table.getRows().forEach(function (element) {
        element.deselect();
    });
}

function testLedSelected() {
    spinner.style.display = 'inline-block';
    setTimeout(function () {
        table.getSelectedRows().forEach(function (element) {
            let req = new XMLHttpRequest();
            req.open('POST', '/test_led/selected?ip=' + element._row.data.ip);
            req.send();
        });
        deselectAll();
        spinner.style.display = 'none';
    }, 20);
}

function pauseCopters() {

}

function stopCopters() {

}


function emLand() {

}

function setStartTime() {
    Ply.dialog("prompt", {
        title: "Set animation delay",
        form: {delay: "Delay"}
    }).done(function (ui) {
        setDelay(parseInt(ui.data.delay));
        updateDelay();
    });
}

function startAnimation() {

}