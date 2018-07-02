// canavas.js
// js routines for the social canvas

/////////////////////////////////////////////////////////////////
//
//  EDITOR
//
/////////////////////////////////////////////////////////////////

//editor buttons
function callFormatting(sFormatString){
		document.execCommand(sFormatString, false, null);
}

function editorAddLink(){
	var szURL = prompt("Enter the URL","http://");
	if (document.execCommand('CreateLink', false, szURL))
		alert('good')
	else
		alert('bad');
}
function changeFontSize(sz){
	//var sSelected=oToolBar.getItem(6).getOptions().item(oToolBar.getItem(6).getAttribute("selectedIndex"));
	document.execCommand("FontSize", false, sz);
}

function changeFontColor(col){
	//alert(col);
	//var sSelected=oToolBar.getItem(6).getOptions().item(oToolBar.getItem(6).getAttribute("selectedIndex"));
	document.execCommand("ForeColor", false, col);
}

function editorOnSelPageLink(value){
	document.execCommand("CreateLink", false, value);
}

function loadEditorPageListHandler(response){
	//object: array ['page1','page2']
	
	//depopulate
	dojo.byId("editorPageLinks").options.length=0;
	
	//repopulate
	dojo.byId("editorPageLinks").options[0] = new Option("[none]", "", true, false)
	var currentRoomLink = '/'+dojo.byId('currentRoom').value+'/';
 	for (i=0; i< response.count;i++){
	 	dojo.byId("editorPageLinks").options[i+1] = new Option(response.pages[i], currentRoomLink+response.pages[i]+"/", false, false)
	}
}

function loadEditorPageList(){
	var chatRoomWdgt;
	var room = dojo.byId('currentRoom').value;
	if (room=="Home")
		alert("Home1");
	var request = {"room": room};
		
	dojo.xhrPost( { 
            url: "/"+room+"/pages/",
            content: request,
            handleAs: "json",
            handle: loadEditorPageListHandler
    });
 }



//PageLinkDialog - click insert
function insertLink(){
	alert('huh');
	url = dojo.byId('linkDlgURL').value;
	if (url == "")
		alert("URL must be specified")
	else{
		alert(url);
		dijit.byId('pageLinkDialog').hide();
		dojo.style(dijit.byId('pageLinkDialog').domNode, {'visibility': 'hidden'});
		dojo.byId('EditDialogEd').execCommand("CreateLink", false, url);
	}
}

//PageLinkDialog - click on a page
function pageLinkDlgClick(pageName){
	dojo.byId('linkDlgURL').value = '/'+dojo.byId('currentRoom').value+'/'+pageName+'/';
}

function showNotifier(msg){
	dojo.byId('xhrNotifier').innerHTML = msg;
	dojo.byId('xhrNotifier').style.display = "block";
}

function hideNotifier(){
	dojo.byId('xhrNotifier').innerHTML = "Nothing Happening";
 	dojo.byId('xhrNotifier').style.display = "none";
}

var sessionData = {};

//to make file uploaders unique
sessionData.fileUlNo = 0;

//current page
sessionData.page = "";

//main Toolbar actions
function mainTb_function(action)
{
	switch(action)
	{
		case 'login':
			dojo.byId('loginDlgMessage').value = "";
			dijit.byId('loginDialog').show();
			break;
		case 'addPageLink':
			break;
		case 'addLink':
			//add new page and display it
			dijit.byId('pageLinkDialog').refresh();
			dijit.byId('pageLinkDialog').show();
			break;
		case 'addPage':
			//add new page and display it
			dijit.byId('pageName').attr("value",""); // clear it
			dijit.byId('renamePageDialog').show();
			break;
		case 'settings':
			loadRoomyListInSettings();
			dijit.byId('roomSettingsDialog').show();
			break;
		case 'addText':
			//get next name - this must be the hard way!
			var i=1;
			while(true){
				if (!dojo.byId("textPane"+i))
					break;
				//iterate every child in order until one doesnt exist - surely it would be better to store this somewhere!
				i++;
			}
		
			//i is the one
			createContentText(i,200+20*i+'px',100+20*i+'px','250px','250px','Empty', "", true);
			break;
		case 'addImage':
			//load image dialog
			
			if (false){
				var uploader = dijit.byId('imageUploader')	
				if (sessionData.fileUlNo>0){
					n = sessionData.fileUlNo-1;
					dijit.byId("imgFileUploader"+n).destroy();				
					//dojo.query(".dijitFileInput","imgUploaderAttach").forEach(dojo.destroy);
				}
				
				var tgt = dojo.byId('imgUploaderAttach')
				var attch = new dijit.form.Button({id:'fakeImgBtn'+sessionData.fileUlNo},tgt);
				var newUl=new dojox.form.FileInputBlind({
														id:"imgFileUploader"+sessionData.fileUlNo,
														name:"imgUp",
														blurDelay:"1", 
														url:"/uploadImage/"},
													   'fakeImgBtn'+sessionData.fileUlNo);
				++sessionData.fileUlNo;
				dojo.connect(newUl, "onComplete","uploadComplete");
				newUl.startup();
			}
			dojo.byId('imgDlgReturnPage').value = dojo.byId('currentPage').value;
			alert('dialog hidden page field set: '+dojo.byId('imgDlgReturnPage').value)
			dijit.byId('imgDialog').show();
			break;
		case 'edit':
			if (currentNode)
				if (currentNode.indexOf('text')==0) //its a text pane
				{
					editDialoged_pane = dojo.byId('EditDialogEd');
					text = dojo.byId(currentNode+'Text');
					loadEditorPageList();
					dijit.byId('editDialog').show();
					editDialoged_pane.innerHTML=text.innerHTML;
					editDialoged_pane.focus()
					break;
				}
			alert('Click a Text Box first');
			break;
		case 'save':
			saveRoomContent()
			break;
		case 'load':
			loadRoomContent();
			break;
		
	}
}

function loadRoomyListInSettings(){

}


///////////////////////////////////////////////////
//
//   ROOMs
//
///////////////////////////////////////////////////
function newPageHandler(response){
	if (response.isOk){
		var menu = dijit.byId("pagesMenuItems")
		var menuItem = new dijit.MenuItem({
		 		label: response.pageName,
		     	onClick: pageMenuClick
			});
			menu.addChild(menuItem);
	} else 
		alert('Could not create new page')
}

function submitNewPageName(e){
	var room = dijit.byId("roomSel").value
	var request = {"room": room,
				   "page": dijit.byId('pageName').attr("value")};
		
	dojo.xhrPost( { 
            url: "/"+room+"/newPage/",
            content: request,
            handleAs: "json",
            handle: newPageHandler
    });
}

function validateRenamePage(){
	if(dijit.byId('pageName').attr("value") != "") {
		dijit.byId('renamePageDialog').hide();
		submitNewPageName()
	}else{
		alert('Page must have a name');
	}
}

function pageMenuClick(evt){
	// set the combo button label to the current page
	dojo.byId("pageDropDown").innerHTML = this.label;
	dojo.byId('currentPage').value = this.label;
	loadRoomContent(); // this loads based on the pagesMenu label
}

function pageLinkClick(page){
	// set the combo button label to the current page
	dojo.byId("pageDropDown").innerHTML = page;
	dojo.byId('currentPage').value = page;
	loadRoomContent(); // this loads based on the pagesMenu label
}

function loadRoomPagesMenuHandler(response){
	//object: array ['page1','page2']
 	//var menu = new dijit.Menu({ style: "display: none;", id:"pagesMenuItems"});
 	var menu = dijit.byId('pageSelectorMnu');
 	for (i=0; i< response.count;i++){
 		var menuItem1 = new dijit.MenuItem({
	 		label: response.pages[i],
	     	onClick: pageMenuClick
		});
		menu.addChild(menuItem1,i);
 	} 
	
	if (dojo.byId('currentPage').value == ""){
		page = response.main;
		dojo.byId('currentPage').value = page;
	} 
	else {
		page = dojo.byId('currentPage').value;
	}
	//store currentPage in the hidden variable
 	dojo.byId("pageDropDown").innerHTML = page;
    dojo.byId('currentPage').value = response.main;
	var i = 1;
//	dojo.byId("contentToolbar").appendChild(button.domNode);
	//dojo.addClass(dojo.byId('pagesMenu'),'contentToolbarIconPages');
}
function loadRoomPagesMenu(){
	var chatRoomWdgt;
	var room = dojo.byId('currentRoom').value;
	if (room=="Home")alert("Home1");
	var request = {"room": room};
		
	dojo.xhrPost( { 
            url: "/"+room+"/pages/",
            content: request,
            handleAs: "json",
            handle: loadRoomPagesMenuHandler
    });
 }

function roomSettingsHandler(response){
	if (response == "error")
    	alert ("Could Not Save Settings")
    else {
    	dijit.byId('roomSettingsDialog').hide();
    	btn = dijit.byId('contentToolbar.settings')
    	btn.attr('label',response);
    }
    	
}

function submitNewRoomSettings(){
	//from settings dialog - update appropriately
	var chatRoom = dojo.byId('currentRoom').value;
	if (chatRoom=="Home")alert("Home2");
	var request = {"chatRoom":chatRoom};
	if (dojo.byId("access_world_rd").checked)
		//world access
		request['access-rd']='world';
	if (dojo.byId("access_owner_rd").checked)
		//world access
		request['access-rd']='owner';
	if (dojo.byId("access_world_wr").checked)
		//world access
		request['access-wr']='world';
	if (dojo.byId("access_group_wr").checked)
		//world access
		request['access-wr']='group';
	if (dojo.byId("access_owner_wr").checked)
		//world access
		request['access-wr']='owner';
	//TODO: Security Hole - HTTPS?
	str = getPrivacyString(dojo.byId("access_world_rd").checked,
						   dojo.byId("access_world_wr").checked,
						   dojo.byId("access_group_wr").checked);
	request['label'] = str;
	//its a POST to stop IE caching it
	dojo.xhrPost( {
			url: "/roomSettings/",
			content: request,
			handleAs: "text",
			handle: roomSettingsHandler
	});
}

///////////////////////////////////////////////////
//
//   CONTENT
//
///////////////////////////////////////////////////

function focusContent(name)
{
	content = dijit.byId(name)
	tbId = content.toolbar.id;
	tb = dojo.byId(tbId);
	tb.style.display="block";
	
}

function blurContent(name)
{
	//alert('blur')
	content = dijit.byId(name)
	tbId = content.toolbar.id;
	tb = dojo.byId(tbId);
	tb.style.display="none";	
}



// currentNode holds the most recently clicked node
var currentNode
var inResize;

//for event handlers
function setCurrentNode(evt){
	currentNode = this.id;
}

function itemDblClick(evt){
	currentNode = this.id;
	mainTb_function('edit');
}

//for div onMouseOver
function showBorder(evt){
	dojo.addClass(dojo.byId(this.id),'moveable');
	dojo.byId(this.id+'ResHdl').style.visibility="visible";
}

//for div onMouseOut
function hideBorder(evt){
	dojo.removeClass(dojo.byId(this.id),'moveable');
	dojo.byId(this.id+'ResHdl').style.visibility="hidden";
}

// cuurent mover if a move is happening
var currentMover

//for event handlers
function setCurrentMover(mvr){
	if (inResize){
		mvr.destroy();
		currentMover=null;
	}
	else{
		currentMover = mvr;
	}
}

function stopDrag(){
	inResize=true;
	if (currentMover){
		currentMover.destroy();
	}
}

function stopResize(){
	inResize=false;
}

// check the hidden field to see if we're logged in'
function loggedIn(){
	return dojo.byId("loggedIn").value == "True";
}

function createContentItem( id, left, top, width, height, innerDiv, outerClass, border, key ){
	var fpNode = document.createElement("div");
	dojo.attr(fpNode, "id", id);
	fpNode.style.position = "absolute";
	fpNode.style.top = top;
	fpNode.style.left = left;
	fpNode.style.width = width;
	fpNode.style.height = height;
	
	fpNode.appendChild(innerDiv);
	
	

	var contentsPane = dojo.byId("contents");
	contentsPane.appendChild(fpNode);
	div = dojo.byId(id);
	if (loggedIn()){
		var resize = new dojox.layout.ResizeHandle({
				targetContainer:div,
				minWidth:40,
	   			minHeight:20 
	   			//,activeResize : true
			});
		dojo.attr(resize, "id", id+'ResHdl');
		resize.placeAt(div);
		resize.startup();
		mover = new dojo.dnd.move.constrainedMoveable(fpNode,{
    	    	constraints:constraintContainer,
        		within: true
    		});
	    if (border)
			dojo.addClass(div, "moveable" );
		else
			dojo.byId(id+'ResHdl').style.visibility = "hidden";
		dojo.addClass(div, outerClass);
		dojo.connect(div,'onmousedown',setCurrentNode);
		dojo.connect(div,'ondblclick',itemDblClick);
		dojo.connect(div,'onmouseover',showBorder);
		dojo.connect(div,'onmouseout',hideBorder);
		dojo.connect(mover,'onMoveStart',setCurrentMover);
		dojo.connect(resize,'onMouseDown',stopDrag);
		dojo.connect(resize,'onResize',stopResize);
	}
	else
		dojo.addClass(div, outerClass);
	currentNode = id
}

function uploadComplete(data, ioArgs, /*this*/ widgetRef){
	dijit.byId('imgDialog').hide();
	//get next name - this must be the hard way!
	var i=1;
	while(true){
		if (!dojo.byId("imagePane"+i))
			break;
		//iterate every child in order until one doesnt exist - surely it would be better to store this somewhere!
		i++;
	}
	//i is the one
	createContentImage(i,200+20*i+'px',100+20*i+'px','250px','250px',data['key'], true);
	dijit.byId('imageUploader').reset();
}

function createContentImage( i, left, top, width, height, border ){
	id = "imagePane"+i;
	var imgDiv = document.createElement("div");
	imgDiv.style.width = '100%';
	imgDiv.style.height = '100%';
	dojo.attr(imgDiv, "id", id+'Img');
	var newimg=document.createElement('img');
    newimg.src='/img/?img_id='+key;
    newimg.alt=key;
    newimg.style.width = '100%';
	newimg.style.height = '100%';
	dojo.attr(newimg, "id", id+'ImgTag');
    imgDiv.appendChild(newimg);
	createContentItem( "imagePane"+i, left, top, width, height, imgDiv, "imagePane" , border, "");
}

//create one of  the content regions
// left, top: int
// width, height: string eg '150px'
function createContentText( i, left, top, width, height, content, key, border ){
	id = "textPane"+i;
	var textDiv = document.createElement("div");
	textDiv.style.width = '100%';
	textDiv.style.height = '100%';
	dojo.attr(textDiv, "id", id+'Text');
	textDiv.innerHTML = content;
	
	// now  the hiden key 
	var input = document.createElement("input");
	input.setAttribute("type", "hidden");
	input.setAttribute("name", id+"Key");
	input.setAttribute("id", id+"Key");
	input.setAttribute("value", key);
	textDiv.appendChild(input);
	
	createContentItem( "textPane"+i, left, top, width, height, textDiv, "textPane", key, border );
}

//var editDialog;

function getTextItem(outer_pane){
	var item={};
	ed_pane = dojo.byId(outer_pane.id+'Text');
	item['data'] = escape(ed_pane.innerHTML);
	//item['data'] = escape(outer_pane.innerHTML);
	//save position
	//outer_pane = dojo.byId("floatingPane"+i);
	item["x"] = outer_pane.style.left;
	item["y"] = outer_pane.style.top;
	item["width"] = outer_pane.style.width;
	item["height"] = outer_pane.style.height;
	item["type"] = 'txt';
	item["key"] = dojo.byId(outer_pane.id+'Key').value;
	return item;
}

var dirty = false;

function saveItemHandler(response) {
	if (response == "ok"){
		hideNotifier();
		dirty = false;
	}
	else if (response == "denied"){
		dojo.byId('loginDlgMessage').value = "Please Log In to Save";
		dijit.byId('loginDialog').show();
	}
	else{
		hideNotifier();
    	alert ("Could Not Save text");
    }
}
// save one item
function saveTextItem(item){
	dirty = true;
	var data = getTextItem(item);  
	room = dojo.byId('currentRoom').value;
	var request = {"item":dojo.toJson(data),
				   "room": room,
				   "page": dojo.byId("currentPage").value};
	showNotifier('saving...');	
	dojo.xhrPost( { 
            url: "/saveItem/",
            content: request,
            handleAs: "text",
            handle: saveItemHandler
    });
}

function saveContentHandler(response) {
	if (response != "ok")
    	alert ("Could Not Save ["+response+"]");
    dirty = false;
    hideNotifier();
}

// saveRoomContent
//  persist the room 's visible content to the db
function saveRoomContent(){
	// iterate names
	
	var data = {};
	data['count'] = 0;
	dojo.query(".textPane","contents").forEach(function(outer_pane){
		alert(outer_pane.id);
		data[data['count']] = saveTextItem(outer_pane)
		data['count'] = data['count']+1;
		//i++;
	});
	
	dojo.query(".imagePane","contents").forEach(function(outer_pane){
	//var i=0;
	//while(dojo.byId("floatingPane"+i))	{
		//iterate every child in order until one doesnt exist - surely it would be better to store this somewhere!
		img = dojo.byId(outer_pane.id+'ImgTag');
	    var item={};
	    //alert(outer_pane.id+'ImgTag.alt: '+img.alt);
		item['data'] = escape(img.alt);
		//save position
		//outer_pane = dojo.byId("floatingPane"+i);
		item["x"] = outer_pane.style.left;
		item["y"] = outer_pane.style.top;
		item["width"] = outer_pane.style.width;
		item["height"] = outer_pane.style.height;
		item["type"] = 'img';
		data[data['count']] = item;
		data['count'] = data['count']+1;
		//i++;
	});
	//data['count'] = i;
	room = dojo.byId('currentRoom').value;
	if (room=="Home")alert("Home3");
	var request = {"items":dojo.toJson(data),
				   "room": room,
				   "page": dojo.byId("currentPage").value};
	showNotifier('saving...');	
	dojo.xhrPost( { 
            url: "/saveContent/",
            content: request,
            handleAs: "text",
            handle: saveContentHandler
    });
}
    

function loadContentHandler(response){
	// clear existing
	dojo.query(".textPane","contents").orphan();
	dojo.query(".imagePane","contents").orphan();
	//now iterate returned content objects and create
	contentCount = response.count;
	for (i=0; i<contentCount; i++){
		contentResp = response.items[i];
		//alert('item'+i+', x:'+
//					   contentResp.x+', y:'+
//					   contentResp.y+', w:'+ 
//					   contentResp.width+', h:'+
//					   contentResp.height+', d:'+
//					   contentResp.data);
		if (contentResp.type == 'img')
			createContentImage( i, 
				contentResp.x, 
		        contentResp.y, 
		 	    contentResp.width, 
		 	    contentResp.height, 
			    unescape(contentResp.data),
			    false)
		else{
			createContentText( i, 
				contentResp.x, 
		        contentResp.y, 
		 	    contentResp.width, 
		 	    contentResp.height, 
			    unescape(contentResp.data),
			    unescape(contentResp.key),
			    false);
			   }
		}
	setPrivacy(response.public_rd, response.public_wr, response.group_wr)
	hideNotifier();
}

function setPrivacy(public_rd, public_wr, group_wr){
	if (loggedIn()){
		str = getPrivacyString(public_rd, public_wr, group_wr);
		btn = dijit.byId('contentToolbar.settings');
	    btn.attr('label',str);
	}
}
	
function getPrivacyString(public_rd, public_wr, group_wr){
	var buttonText = "Public";
	if (public_rd){
		if (group_wr)
			buttonText = "Public Read"
		else
			buttonText = "Public, Owner Edit";
	}
	else{
		if (group_wr)
			buttonText = "Private"
		else
			buttonText = "Private, Owner Edit";
	}
	return buttonText;
}
function loadRoomContent(){
	var chatRoomWdgt;
	
	var room = dojo.byId('currentRoom').value;
	if (room=="Home")alert("Home4");
	var pageName = dojo.byId('currentPage').value; //dojo.byId("pageDropDown_label")
	var d = new Date();
	var request = {"timestamp":d.getTime(),
				   "chatRoom":room,
				   "page":pageName};
	showNotifier('loading...');
	//its a POST to stop IE caching it
	dojo.xhrPost( {
			url: "/loadContent/",
			content: request,
			handleAs: "json",
			handle: loadContentHandler
	});
}

    


///////////////////////////////////////////////////
//
//   BUDDIES
//
///////////////////////////////////////////////////
function submitAddBuddy(){
	function addBuddyHandler(response) {
		//update requests Pane
		var reqPane = dijit.byId("requestPane");
		reqPane.attr('content',response);
	}
	//TODO: Add Buddy ajax call
	// Called from "+" toolbar button in buddy pane, left bar
	var buddyName = dijit.byId("newBuddyName").getValue(false);
	buddyName = escape(buddyName);
	buddyName = "buddyName="+buddyName;
	
	dojo.xhrPost( { 
            url: "/addBuddy/",
            postData: buddyName,
            handleAs: "text",
            handle: addBuddyHandler
        });
}

function acceptBuddy(buddy){
	function acceptBuddyHandler(response) {
		//update requests Pane
		var buddyPane = dijit.byId("buddiesPane");
		buddyPane.attr('content',response);
	}	
	var buddyName = escape(buddy);
	buddyName = "buddyName="+buddyName;
	
	dojo.xhrPost( { 
            url: "/acceptBuddy/",
            postData: buddyName,
            handleAs: "text",
            handle: acceptBuddyHandler
        });
}

function rejectBuddy(buddy){
	alert('TODO: reject '+buddy)
}

function remove_roomy(room, user){
	alert('TODO:remove_roomy '+room+' / '+ user)
}

function editRoomName(room){
	alert('TODO: Edit Room Name: '+room)
}

function isInteger(s) {
	return (s.toString().search(/^-?[0-9]+$/) == 0);
}

///////////////////////////////////////////////////
//
//   CHAT
//
///////////////////////////////////////////////////

//the global Poll data
var pollData = new Object();

function sendChatHandler(response) {
	pollData["active"] = false;
	console.log("sendChatHandler",response)
	//update requests Pane
	var chatHistory = dijit.byId("chat_history");
	var currentHistory = chatHistory.attr('content');
	//response = unescape(response);
	var responseObject = dojo.fromJson(response);
	if (responseObject["error"])
		alert(responseObject["error"]);
	else if (responseObject["msg"])
	{
		if (responseObject["msg"] != "")
		{
			displayText = unescape(responseObject["msg"])
			chatHistory.attr('content',currentHistory+displayText);
			//scroll to bottom
			chatDiv = dojo.byId("chat_history")
			chatDiv.scrollTop = chatDiv.scrollHeight;
			pollData["iterations"] = 0;
			pollData["interval"] = 2000;
			
			seq = responseObject["lastMsgSeq"];
			
			if (seq.search(/^-?[0-9]+$/) == 0)
			{
				dojo.byId("chat_seq").value = seq;
			}
			// get 'undefined' here when there was an exception in the python
			// alert("chat_seq:"+dojo.byId("chat_seq").value);
		}
	}
	pollData["timerHandle"] = setTimeout("poll()",pollData["interval"]);
	pollData["active"] = true;
	//var editorData = dijit.byId("content");
	console.log('sendChatHandler: setTimeout '+pollData["interval"]+', iter:'+pollData["iterations"]+', handle:'+pollData["timerHandle"])
	if (pollData["iterations"] > 9)
	{
		//after 10 polls at given frequency, lengthen it.
		// reset count if msg recieved
		pollData["iterations"] = 0;
		if (pollData["interval"] < 120000)  //2 mins max
		{
			pollData["interval"] = pollData["interval"] + 2000;
			console.log('sendChatHandler:Change Timeout '+(pollData["interval"]))
		}
	}
	pollData["iterations"] = pollData["iterations"] +1;
	console.log("x-sendChatHandler"); 
}	

function sendChat(){
	pollData["active"] = false;
	if (pollData["timerHandle"] != 0)
	{
		clearTimeout(pollData["timerHandle"]);
		//var editorData = dijit.byId("content");
		console.log('sendChat:clearTimeout, handle:'+pollData["timerHandle"])
	}
	
	var chatRoom = dojo.byId('currentRoom').value;
	if (chatRoom=="Home")alert("Home5");
	var chatMsgWdgt = dijit.byId("chat_entry");
	var chatMsg = chatMsgWdgt.attr('value');
	if (chatMsg.length>0){
		chatMsg = escape(chatMsg);
		chatMsgWdgt.attr('value','');

		var content = new Object();
		content["chatRoom"] = chatRoom;
		content["chatMsg"] = chatMsg;
		dojo.xhrPost( { 
		        url: "/sendChat/",
		        content: content,
		        handleAs: "text",
		        handle: sendChatHandler
	    });
	}
	poll();
}


function chatKeyPress(event){
	if (event == dojo.keys.ENTER)
		sendChat();
}

function chatKeyPress(event) {
    key = event.keyCode;
    //console.debug(key);
    if (key == dojo.keys.ENTER)
		sendChat();
}

function nowStr() {
	var now=new Date()
	var hours=now.getHours()
	var minutes=now.getMinutes()
	timeStr=""+((hours > 12) ? hours - 12 : hours)
	timeStr+=((minutes < 10) ? ":0" : ":") + minutes
	timeStr+=(hours >= 12) ? " PM" : " AM"
	return timeStr
}

//timer driven poller
//	looks for new chat messages
//  TODO: look for new win content
function poll(){
	if (dojo.byId("doPoll"))
	if (dojo.byId("doPoll").checked)
	{
		console.log("poll timer "+pollData["timerHandle"])
		if (pollData["active"] == true)
		{
			    // check again in 2 secs
				if (pollData["timerHandle"] != 0)
				{
					console.log ("poll - clearing timer:"+pollData["timerHandle"])
					clearTimeout(pollData["timerHandle"]);
					//var editorData = dijit.byId("chat_history");
					//editorData.attr('content',editorData.attr('content')+'<br>poll:clearTimeout')
				}
				var chatRoom = dojo.byId('currentRoom').value;
				if (chatRoom=="Home")alert("Home6");
				var chatSeq = dojo.byId("chat_seq").value;
				
				var content = new Object();
				content["chatRoom"] = chatRoom;
				content["lastMsg"] = chatSeq;
			
				dojo.xhrGet( {
						url: "/poll/",
						content: content,
						handleAs: "text",
						handle: sendChatHandler
				});
			
			pollData["lastPoll"] = nowStr();
			console.log("polled",content)
		}
		else
			console.log("poll - INACTIVE");
	}
	else
	{
		pollData["timerHandle"] = setTimeout("poll()",2000);
		pollData["active"] = true;
	}
	
	//pollData["active"] = true;
}

function EditDlgSaveBtnClick(){
	dijit.byId('editDialog').hide();
	editDialoged_pane = dojo.byId('EditDialogEd');
	moveable = dojo.byId(currentNode+'Text');
	moveable.innerHTML = editDialoged_pane.innerHTML;
	//TODO: Save only the one
	saveNode = dojo.byId(currentNode);
	saveTextItem(saveNode);
}

function loginSilentHandler(response){
	if (response == "ok"){
		if (dirty)
			saveRoomContent()
	}
	else
		alert("Login Failed")
}


//cause a submit
function loginBtnClick(){
	var loginData = new Object();
	loginData["password"] = dojo.byId("loginPassword").value;
	loginData["username"] = dojo.byId("loginUsername").value;
	if (dirty){
		//login then save items
		dojo.xhrPost( { 
            url: "/loginSilent/",
            content: loginData,
            handleAs: "text",
            handle: loginSilentHandler	
        });
	}
	else{
		post_to_url('/login/', loginData, "post");
	}
}
	
function post_to_url(path, params, method) {
    method = method || "post"; // Set method to post by default, if not specified.

    // The rest of this code assumes you are not using a library.
    // It can be made less wordy if you use one.
    var form = document.createElement("form");
    form.setAttribute("method", method);
    form.setAttribute("action", path);

    for(var key in params) {
        var hiddenField = document.createElement("input");
        hiddenField.setAttribute("type", "hidden");
        hiddenField.setAttribute("name", key);
        hiddenField.setAttribute("value", params[key]);

        form.appendChild(hiddenField);
    }

    document.body.appendChild(form);    // Not entirely sure if this is necessary
    form.submit();
}

var constraintContainer;//for movables
dojo.addOnLoad(function() {
    var chatMsgWdgt = dojo.byId("chat_entry");
    if (loggedIn()){
    	dojo.connect(chatMsgWdgt, 'onkeypress', chatKeyPress);
	    pollData["timerHandle"] = setTimeout("poll()",2000);
	    pollData["lastPoll"] = 0;
	    pollData["chatRoom"] = "";
	    pollData["interval"] = 2000;
	    pollData["active"] = true;
	    pollData["iterations"] = 9;  //so interval goes up quickly
	    
	    //for the draggable text - constrainedMoveables
	    constraintContainer = function() {
	        var marginBox = dojo.marginBox("contents");
	        boundary = {};
	        // Top, Left, Width, Height
	        boundary["t"] = 0;
	        boundary["l"] = 0;
	        boundary["w"] = marginBox.l + marginBox.w;
	        boundary["h"] = marginBox.h + marginBox.t;
	        return boundary;
	    	}
    }
    //CHANGE ROOM
    roomSel = dijit.byId("roomSel");
    dojo.connect(roomSel,"onChange",function(newValue){
    	location.href = '/'+newValue+'/';
    	});
    try{
    	loadRoomContent();
	}catch(err){alert('exc in addOnLoad -1')}
	
	try{
    	//loadRoomPagesMenu();
    }catch(err){alert('exc in addOnLoad -2')}
});
    
function $import(src){
  var scriptElem = document.createElement('script');
  scriptElem.attr('src',src);
  scriptElem.attr('type','text/javascript');
  document.getElementsByTagName('head')[0].appendChild(scriptElem);
}