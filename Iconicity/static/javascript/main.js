
function showInMarkdown(){
    var markdowns = document.getElementsByClassName("toMarkdown");
    for (let i of markdowns){
      text = i.innerHTML;
      converter = new showdown.Converter();
      html = converter.makeHtml(text);
      i.innerHTML = html;
    }
  }
  $(function() {
    var container = $('#demo');
    container.pagination({
      dataSource: 'https://api.flickr.com/services/feeds/photos_public.gne?tags=cat&tagmode=any&format=json&jsoncallback=?',
      locator: 'items',
      totalNumber: 20,
      pageSize: 3,
      ajax: {
        beforeSend: function() {
          container.prev().html('Loading data from flickr.com ...');
        }
      },
      callback: function(response, pagination) {
        var dataHtml = '<ul>';
        var pageStart = (pagination.pageNumber - 1) * pagination.pageSize;
        var pageEnd = pageStart + pagination.pageSize;
        var pageItems = response.slice(pageStart, pageEnd);
        $.each(pageItems, function(index, item) {
          dataHtml += '<li>' + item.title + '</li>';
        });
  
        dataHtml += '</ul>';
  
        container.prev().html(dataHtml);
      }
    })
  })