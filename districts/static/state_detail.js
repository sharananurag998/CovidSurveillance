json_url = "https://api.covid19india.org/data.json";
URL = $(location).attr('pathname');



$(document).ready(function(){
    x = decodeURIComponent(URL);
    x = x.slice(17);
    x = x.slice(0, x.length-1);
    x = x.replace(/%20/g, " ");
    console.log(x);
    $.ajax({
        url:json_url,
        dataType:"json",
        success:function(data){
            $(data.statewise).filter(function(index, value){
                if(value.state == x)
                {
                    var record = "";
                    record += "<tr>";
                    record += "<td>"+value.confirmed+"</td>";
                    record += "<td>"+value.active+"</td>";
                    record += "<td>"+value.recovered+"</td>";
                    record += "<td>"+value.deaths+"</td>";
                    record += "</tr>";
                    console.log(value.confirmed);
                    $("table").append(record);
                }
            });
        }
    });
});
