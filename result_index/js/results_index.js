/* This script controls the appearance of the 'log' button,          */
/* basically, we want the button has a 50% alpha when the mouse      */
/* is not over it, and has a background in a grey look background.   */
/* And whenever the mouse is over the button, it appears with full   */
/* alpha and the background color change to white, this way the      */
/* button gets highlighted. For some reason IE could not call over,  */
/* it would not get loaded, so I created a copy, over2 and it works, */
/* ssteg                                                             */

function over(id, host) {
	var x = document.getElementById(id);
	x.style.backgroundColor='#FFFFFF';
	var i = id + 1;
	var y = document.getElementById(i).src = host + 'img/M.gif';
}

function out(id, host) {
	var x = document.getElementById(id);
	x.style.backgroundColor='#F5F5F5';
	var i = id + 1;
	var y = document.getElementById(i).src = host + 'img/M.png';
}

function over2(id, host) {
	var x = document.getElementById(id);
	x.style.backgroundColor='#FFFFFF';
	var i = id + 1;
	var y = document.getElementById(i).src = host + 'img/M.gif';
}
