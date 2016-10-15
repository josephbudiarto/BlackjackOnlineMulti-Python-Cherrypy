$(document).ready(function() {

	Get_All_Players()
	function Get_All_Players() {
		$.getJSON('get_all_players',function(data) {
			$('#player-count').html(data.length)
			var row = ''
			for (var i=0;i<data.length;i++) {
				row += '<tr>'
				row += '<td>'+data[i].user+ ' ' + data[i].money + '</td>'	
				row += '</tr>'
			}
			$('#players').html(row)
		})
	}

	setInterval(function() {
		Get_All_Players()
	},1000)
})