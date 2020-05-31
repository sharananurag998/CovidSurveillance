json_url = "https://api.covid19india.org/v2/state_district_wise.json";
URL = $(location).attr('pathname');



$(document).ready(function(){
    mapframe = document.getElementById('mapframe');
    x = $("h1").text()    
    src_attr = `https://www.google.com/maps/embed/v1/search?q=${x}&key=AIzaSyAo3AjznlNN_hETfgc9w0JXy53RMZo4IVI`;
    mapframe.setAttribute("src", src_attr);
    
    console.log(x);
    $.ajax({
        url:json_url,
        dataType:"json",
        success:function(data){
            $(data.districtData).filter(function(index, value){
                if(value.district == x)
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
