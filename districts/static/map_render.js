var mapframe = document.getElementById('mapframe');
var src_attr = `https://www.google.com/maps/embed/v1/search?q=Jamshedpur&key=${config.KEY}`;
//var att = document.createAttribute("src");
//att.value = src_attr;

mapframe.setAttribute("src", src_attr);