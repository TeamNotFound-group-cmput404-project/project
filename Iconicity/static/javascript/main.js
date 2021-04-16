// FROM https://github.com/showdownjs/showdown/wiki/Tutorial:-Markdown-editor-using-Showdown
function showInMarkdown(){
    var markdowns = document.getElementsByClassName("toMarkdown");
    for (let i of markdowns){
      text = i.innerHTML;
      converter = new showdown.Converter();
      html = converter.makeHtml(text);
      i.innerHTML = html;
    }
  }
// ENDFROM