var TREE1_FORMAT =
[
//0. left position
	15,
//1. top position
	15,
//2. show +/- buttons
	true,
//3. couple of button images (collapsed/expanded/blank)
	["images/collapsed_button.gif", "images/expanded_button.gif", "images/blank.gif"],
//4. size of images (width, height,ident for nodes w/o children)
	[16,16,0],
//5. show folder image
	true,
//6. folder images (closed/opened/document)
	["images/closed_folder.gif", "images/opened_folder.gif", "images/document.gif"],
//7. size of images (width, height)
	[16,16],
//8. identation for each level [0/*first level*/, 16/*second*/, 32/*third*/,...]
	[0,16,32,48,64,80,96,112,128,144,160,176,192,208,224,240,256,272],
//9. tree background color ("" - transparent)
	"",
//10. default style for all nodes
	"clsNode",
//11. styles for each level of menu (default style will be used for undefined levels)
	[],
//12. true if only one branch can be opened at same time
	true,
//13. item pagging and spacing
	[1,0],
];


