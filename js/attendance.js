const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('./database/data.db');
const contentSelect = document.getElementById('contentSelect');
const tableBody = document.getElementById('tableBody');
const refreshButton = document.getElementById('refreshButton');

function renderDatabaseOptions() {
    db.all("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE 'stud_list'", [], (err, rows) => {
        if (err) {
            console.error(err.message);
            return;
        }

        rows.forEach(row => {
            const option = document.createElement('option');
            option.value = row.name;
            option.textContent = (row.name).replaceAll('_', '-');
            contentSelect.appendChild(option);
        });
    });
}


function displayTableData(selectedDate) {
    const tableName = selectedDate.replaceAll('-', '_');
    const query = `SELECT ID_Number, Name, Course, Time_in, Time_Out FROM \`${tableName}\``;
    db.all(query, [], (err, rows) => {
        if (err) {
            console.error(err.message);
            return;
        }

        tableBody.innerHTML = ''; 

        rows.forEach(row => {
            const tr = document.createElement('tr');
            let timeOutValue = row.Time_Out ? row.Time_Out : 'None';
            tr.innerHTML = `
                <td>${row.ID_Number}</td>
                <td>${row.Name}</td>
                <td>${row.Course}</td>
                <td>${row.Time_In}</td>
                <td>${timeOutValue}</td>`;
            tableBody.appendChild(tr);
        });        
    });
}


contentSelect.addEventListener('change', function() {
    const selectedTable = this.value;
    if (selectedTable !== 'Select a table') {
       
        const selectedDate = selectedTable.replaceAll('-', '_');
        displayTableData(selectedDate);
        console.log(selectedDate);
    }
});

refreshButton.addEventListener('click', function() {
    const selectedTable = contentSelect.value;
    if (selectedTable !== 'Select Date') {
        const selectedDate = selectedTable.replaceAll('-', '_');
        displayTableData(selectedDate);
    } else {
        tableBody.innerHTML = '';
    }
});


renderDatabaseOptions();

    const searchDate = document.getElementById('search-date');

    searchDate.addEventListener('input', function () {
        const searchTerm = searchDate.value.trim();
        console.log("Search Term:", searchTerm);

        tableBody.innerHTML = '';

        const searchQuery = `SELECT name FROM sqlite_master WHERE type='table' AND name LIKE ?;`;

        db.all(searchQuery, [`%${searchTerm.replace(/-/g, '_')}%`], function (err, results) {
            if (err) {
                console.error("Error executing date search query:", err.message);
                return;
            }


            contentSelect.innerHTML = '<option selected>Select Date</option>';

            for (const tableResult of results) {
                const tableName = tableResult.name;
                const option = document.createElement('option');
                option.value = tableName;
                option.text = (tableName.replaceAll('_', '-'));
                contentSelect.add(option);
            }
        });
    });

    const searchUser = document.getElementById('search-user');
    searchUser.addEventListener('input', function () {
    const searchTerm = searchUser.value.trim().toLowerCase();

    const tableRows = tableBody.querySelectorAll('tr');

    tableRows.forEach(row => {
        const idNumberCell = row.querySelector('td:first-child');
        const nameCell = row.querySelector('td:nth-child(2)');

        if (nameCell && idNumberCell) {
            const name = nameCell.textContent.toLowerCase();
            const idNumber = idNumberCell.textContent.toLowerCase();

            if (name.includes(searchTerm) || idNumber.includes(searchTerm)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        }
    });
});
