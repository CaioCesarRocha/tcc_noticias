'use strict';

var HOST = 'http://127.0.0.1:8080/'

var url_base = "";

document.addEventListener('DOMContentLoaded', function(){
//set ratings values CSS
	document.querySelector('#star1').addEventListener('click',function(){
		document.querySelector(".myratings").innerHTML = "1-(Nenhuma similar)";
	});
	document.querySelector('#star2').addEventListener('click',function(){
		document.querySelector(".myratings").innerHTML = "2-(Pouca similaridade)";
	});
	document.querySelector('#star3').addEventListener('click',function(){
		document.querySelector(".myratings").innerHTML = "3-(Boa similaridade)";
	});
	document.querySelector('#star4').addEventListener('click',function(){
		document.querySelector(".myratings").innerHTML = "4-(Muito similares)";
	});
	
	document.querySelector('#btnFind').addEventListener('click',function(){
		chrome.tabs.query({active: true, lastFocusedWindow: true}, tabs => {
    		url_base = tabs[0].url;
  		});
	});

// Function to get and set Rating value
	document.querySelector('#btnRating').addEventListener('click',function(){
    		setRating(url_base);					
	});
});

//set value rate on mongoDB using django
function setRating(url_base){
	var url = url_base
	var request_url = 'https://agile-oasis-03992.herokuapp.com/' + 'app/url_base/post';

	var xhr = new XMLHttpRequest();
	xhr.open("POST", request_url);
	xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
		
	try{
		var obj = new Object();
		obj.rate = document.querySelector('input[name="rating"]:checked').value;
		obj.url = url
		var jsonArray = new Array();
		jsonArray.push(obj);
		var dataJSON = JSON.stringify(jsonArray);
		xhr.send(dataJSON);
	}
	catch{
		document.getElementById("errorRating").style.display = "block";
		document.getElementById("infoRating").style.paddingTop = '5px'; 
	}

	xhr.responseType = "json";
	xhr.onreadystatechange = function() {
		var results1 = this.response;
		console.log(results1)
		var statuss = this.status
		console.log(statuss)
        if (this.readyState == 4 && this.status == 200) {		
        	var results = this.response;
        	if(results == 200){
        		document.getElementById("infoRating").style.paddingTop = '5px'; 
        		document.getElementById("errorRating").style.display = "none";
        		document.getElementById("successRating").style.display = "block";    			   	
       		}
    	};				
	};
}