json_url = "https://api.covid19india.org/data.json";

$(document).ready(function(){
    $.ajax({
        url:json_url,
        dataType:"json",
        success:function(data){
            $(data.statewise).each(function(index, value){
                var record = "";
                record += "<tr>";
                record += "<td>"+value.state+"</td>";;
                record += "<td>"+value.confirmed+"</td>";
                record += "<td>"+value.active+"</td>";
                record += "<td>"+value.recovered+"</td>";
                record += "<td>"+value.deaths+"</td>";
                record += "</tr>";
                $("table").append(record);
            });
        }
    });
});
