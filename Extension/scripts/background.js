'use strict';

var HOST = 'http://127.0.0.1:8080/'

document.addEventListener('DOMContentLoaded', function(){
	//quit 
	document.querySelector('#btnClose').addEventListener('click',function(){
		window.close();
	});

	document.querySelector('#btnFind').addEventListener('click',function(){
	//get url actual from navigator
		closeDivBtn();
		openDivLoading();
		chrome.tabs.query({active: true, lastFocusedWindow: true}, tabs => {
    		let text = tabs[0].url;
    		findNotices(text);
		});			
	});
});     

//close btn find
function closeDivBtn(){
	document.getElementById("btnFind").style.display = "none";
}

function openDivLoading(){
	document.getElementById("containerLoading").style.display = "block";
	setTimeout(function() {
		var analise =  "Processando resultados...";
		document.querySelector("#loadInfo").innerHTML = analise;
	},8000);
	setTimeout(function() {
		var analise =  "Buscando notícias similares...";
		document.querySelector("#loadInfo").innerHTML = analise;
	},7000);
			
}

function closeDivLoading(){
	document.getElementById("containerLoading").style.display = "none";
	document.getElementById("loading").style.display = "none";
	document.getElementById("loadInfo").style.display = "none";
	document.getElementById("containerBTN").style.display = "none";
}

function newTab(link) {
	chrome.tabs.create({
    	url: link,
    	active: false
	});
};
	

//get the img belongs the site
function getPicture(picture){
	let img = document.createElement("img");

	if(picture == 'globo'){
		img.src= "http://www.gruporbs.com.br/noticias/wp-content/uploads/sites/3/2014/10/logo_G1RS1.png";
		img.style.width = '60px'; img.style.height = '36px'; 
	}
	else if(picture == 'uol'){	
		img.src="https://logodownload.org/wp-content/uploads/2018/09/uol-logo-5.png";
		img.style.width = '85px'; img.style.height = '33px'; 		
	}
	else if(picture == 'terra'){
		img.src="https://thutor.com/site/wp-content/uploads/2016/12/logoterra1.png";
		img.style.width = '85px'; img.style.height = '36px';
	}
	else if(picture == 'ig'){	
		img.src="https://iconape.com/wp-content/png_logo_vector/ig-logo.png";
		img.style.width = '54px'; img.style.height = '42px'; 			
	}
	return img;
};


function getResults(results){
	closeDivLoading();
	document.getElementById("rating").style.display = "block";
	document.getElementById("containerNotices").style.display = "block";	
	var resultsArray = results

	//Criando os elements e atribuindo os valores pelo mapeamento
	resultsArray.map((obj) => {
		var link = obj.link
			
		var title = document.createElement('div');
		var titletxt = document.createTextNode(obj.title);
		title.appendChild(titletxt);

		var data = document.createElement('div');
		var info = document.createTextNode("Data: ");				
		var datatxt = document.createTextNode(obj.data);
			data.appendChild(info)
			data.appendChild(datatxt);
			
		var link_title = document.createElement('a');
			link_title.href = obj.link;
			link_title.appendChild(title)
			
		var link_img = document.createElement('a');
			link_img.href = obj.link;

		var picture = obj.picture;
		var img = getPicture(picture);							
		link_img.appendChild(img);
		
		link_title.onclick = function () {newTab(link)}
		link_img.onclick = function () {newTab(link)}		
		
		//criando tabela HTML dinamicamente
		var card = document.createElement("div");
		card.className = 'card';
		var table = document.createElement("table");
		var body = document.createElement("tbody");
			
		var trcontent = document.createElement("tr");								
		var tr = document.createElement("tr");
		var td1 = document.createElement("td");
		var td2 = document.createElement("td");			

		td2.appendChild(link_img);
		td1.appendChild(data);

		tr.appendChild(td1)
		tr.appendChild(td2)

		trcontent.appendChild(link_title)
		trcontent.appendChild(tr)

		body.appendChild(trcontent)
		table.appendChild(body);
		card.appendChild(table)

		document.getElementById("notices").appendChild(card);				

		//CSS
		link_title.addEventListener("mouseover", function(link_title) {
			link_title.target.style.color = '#751aff';
		});
		link_title.addEventListener("mouseout", function(link_title) {
			link_title.target.style.color = '#4a148c';
		});

		card.style.width = "275px"; card.style.backgroundColor = "#fff"; card.style.border = "3px solid";  card.style.borderRadius = "8px"; card.style.borderColor = "#4a148c";			 
		card.style.paddingRight = "18px"; card.style.paddingLeft = "18px"; card.style.paddingTop = "10px"; card.style.paddingBottom = "10px";
		card.style.marginTop = "20px"; card.style.marginBottom= "25px"; card.style.marginLeft= "25px";

		td1.style.paddingTop = "5px"; td1.style.paddingLeft = "10px"; td1.style.width = "30%";
		td2.style.textAlign = "center"; td2.style.width = "70%"; td2.style.paddingLeft = "22px"; td2.style.paddingTop= "3px";  td2.style.paddingBottom= "2px";   
			 
		title.style.textAlign = 'justify'; title.style.fontFamily = 'Bahnschrift'; title.style.fontSize = '15px'; 

		link_title.style.textDecoration = 'none'; link_title.style.color = '#4a148c'; link_title.style.fontWeight = 'bold'; 

		data.style.fontFamily = 'Bahnschrift'; data.style.fontSize = '15px'; data.style.color = '#4a148c';							
	});
}

//nothing found similar notices
function nothingSimilar(){
	closeDivLoading();
	document.getElementById("containerNotices").style.display = "block";
	var nothing = document.createElement('div');
	var nothingtxt = document.createTextNode("Nenhuma notícia similar foi encontrada.");
		nothing.appendChild(nothingtxt);
	document.getElementById("errorFound").appendChild(nothing);
	nothing.style.textAlign = 'justify'; nothing.style.fontFamily = 'Bahnschrift'; nothing.style.fontSize = '18px'; nothing.style.color = '#751aff'
};

//Resquest wrong site
function errorRequest(){
	closeDivLoading();
	document.getElementById("errorRequest").style.display = "block";
	
	var imgGlobo = document.createElement("img");
		imgGlobo.src= "http://www.gruporbs.com.br/noticias/wp-content/uploads/sites/3/2014/10/logo_G1RS1.png";
	var imgUol = document.createElement("img");
		imgUol.src= "https://logodownload.org/wp-content/uploads/2018/09/uol-logo-5.png";
	var imgTerra = document.createElement("img");
		imgTerra.src="https://thutor.com/site/wp-content/uploads/2016/12/logoterra1.png"
	var imgIG = document.createElement("img");
		imgIG.src="https://iconape.com/wp-content/png_logo_vector/ig-logo.png"
	var linkGlobo = document.createElement("a");
		linkGlobo.href = "https://g1.globo.com/bemestar/coronavirus/";
	var linkUol = document.createElement("a");
		linkUol.href = "https://noticias.uol.com.br/coronavirus/";
	var linkTerra = document.createElement("a");
		linkTerra.href = "https://www.terra.com.br/noticias/coronavirus/";
	var linkIG = document.createElement("a");
		linkIG.href = "https://www.ig.com.br/";

	linkGlobo.appendChild(imgGlobo);
	linkUol.appendChild(imgUol);
	linkTerra.appendChild(imgTerra);
	linkIG.appendChild(imgIG);

	linkGlobo.onclick = function () {newTab(linkGlobo.href)}
	linkUol.onclick = function () {newTab(linkUol.href)}
	linkTerra.onclick = function () {newTab(linkTerra.href)}
	linkIG.onclick = function () {newTab(linkIG.href)}

	document.getElementById("linkGlobo").appendChild(linkGlobo);
	document.getElementById("linkUol").appendChild(linkUol);	
	document.getElementById("linkTerra").appendChild(linkTerra);
	document.getElementById("linkIG").appendChild(linkIG);	

	//CSS
	//errorRequest.style.textAlign = 'justify'; errorRequest.style.fontFamily = 'Bahnschrift'; errorRequest.style.fontSize = '18px'; errorRequest.style.color = '#751aff'; errorRequest.style.fontWeight = 'bold';
	imgGlobo.style.width = '50px'; imgGlobo.style.height = '35px';
	imgUol.style.width = '65px'; imgUol.style.height = '25px';  
	imgTerra.style.width = '65px'; imgTerra.style.height = '32px';
	imgIG.style.width = '41px'; imgIG.style.height = '39px';  
};

function getWorkerResults(dataJSON){
	dataJSON = dataJSON
	
	var xhr = new XMLHttpRequest();
	var request_url = 'https://herokutccnoticias.herokuapp.com/' + 'app/url_base/get'
	xhr.open("GET", request_url);
	xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
//send url to server using django
	xhr.send(dataJSON);	

	xhr.responseType = "json";
	xhr.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {		
        	var response = this.response;
        	console.log(response)
        	if(response == 1){
        		setTimeout(function() {
					getWorkerResults(dataJSON)
				},10000);
        	}
        	else if(response == 404 || (response == null)){ //NOTHING FOUND
        		nothingSimilar();
        	}
        	else{
        		getResults(response);
        	}
        }
    }  
}
	
// pega a URl e envia para o servidor, tratada na views do django
function findNotices(text){
	var url_base = text;

	var xhr = new XMLHttpRequest();

	xhr.responseType = "json";
	xhr.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {		
        	var results = this.response;
        	if(results == 205){
        		console.log(results)      						
				setTimeout(function() {
					getWorkerResults(dataJSON)
				},20000);
        	}
        	else if((results == 400) || (results == null)){ //WRONG REQUEST
        		console.log(results)
        		errorRequest();
        	}
       	}
    };
	var request_url = 'https://herokutccnoticias.herokuapp.com/' + 'app/url_base/get'

	xhr.open("POST", request_url);
	xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

	var url_json = new Object();
	url_json.url = url_base;

	var jsonArray = new Array();
	jsonArray.push(url_json);

	var dataJSON = JSON.stringify(jsonArray);
//send url to server using django
	xhr.send(dataJSON);	
}