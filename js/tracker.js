const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('./database/data.db');

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchStudent');
    const searchButton = document.getElementById('searchButton');
    const attendanceResults = document.getElementById('attendanceResults');

    searchButton.addEventListener('click', function() {
        const searchTerm = searchInput.value.trim();
        console.log("Search Term:", searchTerm);
    
        if (searchTerm === '') {
            alert('Please enter a student name or ID number.');
            return;
        }
    
        attendanceResults.innerHTML = '';
    
        const query = `SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE 'stud_list';`;
    
        db.all(query, [], function(err, tables) {
            if (err) {
                console.error("Error executing search query:", err.message);
                return;
            }
    
            tables.forEach(table => {
                const tableName = table.name;
                const queryAttendance = `SELECT ID_Number, Name, Time_In, Time_Out FROM \`${tableName}\` WHERE ID_Number = ? OR Name = ?;`;
    
                db.all(queryAttendance, [searchTerm, searchTerm], function(err, rows) {
                    if (err) {
                        console.error("Error fetching data from table:", tableName, err.message);
                        return;
                    }
    
                    if (rows.length > 0) {
                        const tableHeading = document.createElement('h3');
                        tableHeading.textContent = `Attendance for Date: ${tableName.replaceAll('_', '-')}`;
                        attendanceResults.appendChild(tableHeading);
    
                        const table = document.createElement('table');
                        table.className = 'table';
                        table.innerHTML = `
                            <thead>
                                <tr>
                                    <th>ID Number</th>
                                    <th>Name</th>
                                    <th>Time In</th>
                                    <th>Time Out</th>
                                </tr>
                            </thead>
                            <tbody></tbody>
                        `;
    
                        const tbody = table.querySelector('tbody');
                        rows.forEach(row => {
                            const tr = document.createElement('tr');
                            tr.innerHTML = `
                                <td>${row.ID_Number}</td>
                                <td>${row.Name}</td>
                                <td>${row.Time_In}</td>
                                <td>${row.Time_Out}</td>
                            `;
                            tbody.appendChild(tr);
                        });
    
                        attendanceResults.appendChild(table);
                    }
                });
            });
        });
    });
    
    });
    
                               
