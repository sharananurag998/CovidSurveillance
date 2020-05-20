var url = "https://docs.google.com/spreadsheets/d/1r2YFNfOP3HTzBjX5-XQblCR06cCbU8lgTnwIEG5fih0/edit?usp=sharing";
var Route = {};
Route.path = function(route,callback){
    Route[route] = callback;
}

function doGet(e){
    Route.path("home",loadTable);
    return Route[e.parameters.v]();
}

function loadTable(){
    return render("home");
}

function getTableData() {

    var ss = SpreadsheetApp.openByUrl(url);
    var ws = ss.getSheetByName("");
    var data = ws.getRange(2, 1, ws.getLastRow() - 1,3).getValues();
    return data;
}