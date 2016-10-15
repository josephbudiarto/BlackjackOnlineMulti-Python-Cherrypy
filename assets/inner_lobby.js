$(document).ready(function() {

	Get_All_Player_In_Lobby()
	function Get_All_Player_In_Lobby() {
		$.getJSON('get_player_in_lobby?room='+lobby,function(data) {
			$('#player-count').html(data.length)
			var row = ''
			for (var i=0;i<data.length;i++) {
				row += '<tr>'
				row += '<td>'+data[i].name + '</td>'	
				row += '</tr>'
			}
			$('#players').html(row)
			if (data.length > 1 && data.length <=4) {
				$('#play').prop('disabled',false)
			} else {
				$('#play').prop('disabled',true)
			}
		})
	}

	setInterval(function() {
		Get_All_Player_In_Lobby()
	},1000)
})