$(document).ready(function() {

	var players = []
	var decks = []
	var playerIndex = 1
	var playerNumber
	var playerCount = 4
	var top
	var currentDecks
	var offsetPlayer
	var myScore = 0
	var g_counter = 0
	var countCard = [0,0,0,0]

	UpdateDataGame()

	setInterval(function() {
		UpdateDataGame()
	},1000)
		
	Update(playerIndex)
	$(window).resize(function() {
		Update(playerIndex)
	})

	//called to be update
	function Update(i) {
		var hands = $('#player'+i+ ' .hand .card').toArray()
		var cardWidth = hands.length * $(hands[0]).width()
		var handWidth = $('#player'+i+ ' .hand').width()

		//current decks
		currentDecks = $('.deck .card').toArray()
		top = currentDecks.length-1

		if (hands.length > 0) {
			//reset card
			$(hands).css('margin-left',0)

			if ((handWidth - cardWidth)/2 > 0) {
				//calculate card to center of the hand
				$(hands[0]).css('margin-left',(handWidth - cardWidth)/2)
			} else {
				$(hands[0]).css('margin-left',0)
				for (var i=1;i<hands.length;i++) 
					$(hands[i]).css('margin-left',(handWidth - cardWidth)*1.25/hands.length)
			}
		}
		//when top deck to be click

		currentDecks = $('.deck .card').toArray()
		top = currentDecks.length-1
		

	}

	
	//player true : sudut pandang player
	//player false : sudut pandang orang lain
	$('#draw-card').click(function() {
		if (status != 'playing') return 
		$.post( "draw_card", { 'room' : room, 'ip' : ip }, function(data) {
			dataCard = data
			
			//ambil dar player status
			var id = players[playerNumber-1].id
			
			//update to database
			$.post( "update_playing", { 'ruang': room, 'has' : ip, 'cards': dataCard , 'id' : id })		

			DrawCard(1,true,dataCard)
		})
	})

	$('#pass-turn').click(function(){
		if (status != 'playing') return 
		$.post("status_pass", { 'ip': ip })
		$('#draw-card').prop('disabled',true)
	})

	function DrawCard(i,reveal,dataCard='') {
		

		var hands = $('#player'+i+ ' .hand .card').toArray()
		var cardWidth = hands.length * $(hands[0]).width()
		var handWidth = $('#player'+i+ ' .hand').width()
		
		//current decks
		currentDecks = $('.deck .card').toArray()
		top = currentDecks.length-1
		var place = $(currentDecks[top]).attr('data-place')


			//if card in deck
			if (place == 'deck') {
				//animate topCard
				if (hands.length > 0) {
					var cardTop = $(currentDecks[top]).offset()
					var cardTarget = $(hands[hands.length-1]).offset()
				} else {
					var cardTop = $(currentDecks[top]).offset()
					var cardTarget = {
						left: $('#player'+i+' .hand').offset().left + ($('#player'+i+' .hand').width() / 3),
						top: $('#player'+i+' .hand').offset().top
					}
				}
				
				$(currentDecks[top]).css({
					left: cardTarget.left - cardTop.left + 150 + "px",
					top:cardTarget.top - cardTop.top + "px"
				})
	
				//after animation move to hand stack
				setTimeout(function() {
					$(currentDecks[top]).attr('data-place','hand')
					$(currentDecks[top]).removeAttr('style')
					if (hands.length > 0)
						$(currentDecks[top]).insertAfter($(hands[hands.length-1]))
					else
						$($('#player'+i+' .hand')).append(currentDecks[top])

					if (reveal)
							RevealCard($(currentDecks[top]),dataCard)
							
					Update(i)
					},500)

				}
	} 
		
	function RevealCard($card,dataCard) {
		var id = $card.attr('data-card')
		$card.attr('id','card-'+dataCard)
	}

	function UpdateDataGame() {

		$.getJSON('/get_game_header?room='+room,function(data) {
			players = data
			playerCount = players.length
			PlayerNumbering()
			//update player status
			var players_text = ''
			for (var i=0;i<playerCount;i++) 
					players_text += players[i].player + ' is ' + players[i].status + '&nbsp &nbsp  | &nbsp'
			players_text += ' &nbsp &nbsp &nbsp'
			if (status == 'waiting' || status == 'betting') {
				status = 'shuffling'
				for (var i=0;i<playerCount;i++) {
					if (players[i].status == 'betting')
						status = 'betting'	
				}
				if (status == 'shuffling') {
					$.post( "shuffle_deck", { "room" : room },function() {
						StackDeck()
					})
					status = 'playing'
				}
			} 
			
			if (status == "playing") {
				var playCount = 0
				for (var i=0;i<playerCount;i++) {
					if (players[i].status == 'playing' || players[i].status == 'ready')
						playCount++
				}
				if (playCount == 0) status = 'gameover'
				else status = 'playing'

				StackDeck()
				DrawMyCard()
				GetScore()
				DrawOtherPlayer()
			}

			if (status == 'gameover') {
				window.location.href = "gameover?room="+room+"&ip="+ip

			}

			$.post("update_score", { 'id' : players[playerNumber-1].idgame, 'room' : room, 'ip' : ip, 'score' : myScore })
			$('#players').html(players_text)
		})

		function GetScore() {
			$.getJSON('/get_card?ip='+ip,function(data) {
				var temp1 = 0 //AS 1
				var temp2 = 0 // AS 11

				for (var j=0;j<data.length;j++) {
					if (data[j].card[0] == 'A') {
						temp1 += 1
						temp2 += 11
					}
					else if (data[j].card[0] == 'J' || data[j].card[0] == 'Q' || data[j].card[0] == 'K' || (data[j].card.substr(0,2) == '10')) {
						temp1 += 10
						temp2 += 10
					} else {
						temp1 += parseInt(data[j].card[0])
						temp2 += parseInt(data[j].card[0])
					}
				}

				if (temp1 > temp2 && temp1 <= 21) {
					myScore = temp1
				} else if (temp2 > temp1 && temp2 <= 21) {
					myScore = temp2
				} else if (temp1 < temp2) {
					myScore = temp1
				} else {
					myScore = temp2
				}
			})
		}

		function DrawMyCard() {
			if (myScore > 21) {
				$.post( "status_dead", { 'ip': ip })
				$('#draw-card').prop('disabled',true)
				$('#pass-turn').prop('disabled',true)
				$.post("update_score", { 'id' : players[playerNumber-1].idgame, 'room' : room, 'ip' : ip, 'score' : myScore })
			}
			$.ajax({
		        url: '/get_card?ip='+ip,
		        dataType: 'json',
		        success: function(data) {
					countCard[playerNumber-1] = data.length 
		            var cardInHand = $('#player1 .hand .card').toArray().length
		            if (data.length > cardInHand) {
			            for (var j=cardInHand;j<data.length;j++) {
							DrawCard(1,true,data[j].card)
			            }
			    			
			        }

		       	}
		    })
		}
		
		function DrawOtherPlayer() {
			var i=0
			var counter = 2

			DrawingOtherPlayer(playerNumber % playerCount,counter)
			// var i = 0
			// var counter = 2
			// for (i = playerNumber % playerCount;i!=playerNumber-1;) {
			// 	$.ajax({
		 //            url: '/get_card?ip='+players[i].ip,
		 //            dataType: 'json',
		 //            index: counter,
		 //            success: function(data) {
		 //                var cardInHand = $('#player'+this.index+' .hand .card').toArray().length
		 //                if (data.length > cardInHand)
		 //                	for (var j=cardInHand;j<data.length;j++) {
		 //                		if (j==0)
			// 						DrawCard(this.index,true,false,data[j].card)
			// 					else
			// 						DrawCard(this.index,false,false)

		 //                	}
		 //            }
		 //        })
			// 	counter++
			// 	i = (i+1) % playerCount
			//}
		}

		//recursive function callback from DrawOtherPlayer
		//counter order player in game
		function DrawingOtherPlayer(i,counter) {
			if (i == playerNumber - 1) return true
			$.ajax({
				url:'/get_card_other_player?id='+players[i].id,
				dataType: 'json',
				index: counter,
				player: i,
				success: function(data) {
					countCard[this.player] = data.count
					var cardInHand = $('#player'+this.index+' .hand .card').toArray().length
					if (data.count > cardInHand) {
						for (var i=0;i<data.count;i++) {
							if (i==0)
								DrawCard(this.index,true,data.first)
							else
								DrawCard(this.index,false)
						}
					}
					DrawingOtherPlayer((this.player+1) % playerCount,this.index+1)
				}
			})
		}

		function PlayerNumbering() {
			for (var i=0;i<playerCount;i++) {
				if (players[i].ip == ip) {
					playerNumber = i + 1
				}
			}
			var temp = playerNumber - 1
			for (var i=0;i<playerCount;i++) { 
				if (i==0) {
					offsetPlayer = (temp % playerCount)
				}
				$('#player'+(i+1)+'Label').html((temp % playerCount) + 1 )
				temp++;

			}
		}

		function StackDeck() {
			$.get( "get_deck", { 'room' : room },function(data){
				var offset = 0.5
				$('deck').html('')
				for (var i=0;i<data;i++) {
					$('.deck').append('<div class="card back" data-place="deck" style="left:'+ offset * i * 1.5+'px;top:'+ offset * i +'px"></div>')
				}
			})

		}

	}
	
	

})


