
document.addEventListener("DOMContentLoaded", function(){

    google.script.run.withSuccessHandler(generateTable).getTableData();

    

    });

function generateTable(dataArray){
    var tbody = document.getElementById("table-body");

    dataArray.forEach(function(r){

        var row = document.createElement("tr");
        var col1 = document.createElement("td");
        col1.textContent = r[0];
        var col2 = document.createElement("td");
        col2.textContent = r[1];
        var col3 = document.createElement("td");
        col3.textContent = r[2];
        var col4 = document.createElement("td");
        col4.textContent = r[3];
        var col5 = document.createElement("td");
        col5.textContent = r[4];
        row.appendChild(col1);
        row.appendChild(col2);
        row.appendChild(col3);
        row.appendChild(col4);
        row.appendChild(col5);
        tbody.appendChild(row);

    });   
}
