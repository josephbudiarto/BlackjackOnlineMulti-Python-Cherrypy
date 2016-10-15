#!/usr/bin/python

import cherrypy
import MySQLdb
import os
import random
import string
import json

from cherrypy.lib.static import serve_file
path   = os.path.abspath(os.path.dirname(__file__))


cherrypy.server.socket_host = '0.0.0.0'
cherrypy.config.update({ 'server.socket_port': 65000 })

#utility
def header(location):
	return """<html><head></head><body onload="window.location='"""+ str(location) +"""'"></body></html>""";

class HelloWorld(object):
	@cherrypy.expose
	def index(self,message=''):
		return serve_file(os.path.join(path, 'front.html'))
	
	@cherrypy.expose
	def helo(self):
		return ''' <!DOCTYPE html>
	<html>
		<head>
			<title>Login - Blackjack Online</title>
		</head>
		<style>
		 .back
			{
				background: url("loginback.png") no-repeat;
			 } 
			.bawah
			{
				padding-top:170px;
				padding-left:100px;
			}
		 </style>
		<body class=back>

			<div class=bawah>
			<form  method="post" action="login">
			   
					<input type="text" name="username">
					<br><br><br><br><br>
					<input type="password" name="password">
					<br><br>
					<br>
					<button type="submit">SUBMIT</button>
					
			</form>
			</div>
		</body>
	</html>'''

	@cherrypy.expose
	def signup(self):
		return ''' <!DOCTYPE html>
	<html>
		<head>
			<title>Login - Blackjack Online</title>
		</head>
		<style>
		 .back
			{
				background: url("signback.png") no-repeat;
			 } 
			.bawah
			{
				padding-top:170px;
				padding-left:100px;
			}
		 </style>
		<body class=back>

			<div class=bawah>
			<form  method="post" action="insert_user">
			   
					<input type="text" name="username">
					<br><br><br><br><br>
					<input type="password" name="password">
					<br><br>
					<br>
					<button type="submit">SUBMIT</button>
					
			</form>
			</div>
		</body>
	</html>'''
	@cherrypy.expose
	def insert_user(self,username='',password=''):
		if username is None or password is None:
			return header('index')

		db= MySQLdb.connect('localhost','m26414093','tos987','m26414093')
		cursor = db.cursor()
		cursor.execute("INSERT INTO user VALUES(null,'%s','%s',500,NULL,0)"%(username,password))
		db.commit()
		db.close()
		return header('index')


	@cherrypy.expose
	def login(self,username='',password=''):
		db= MySQLdb.connect('localhost','m26414093','tos987','m26414093')
		cursor = db.cursor()
		cursor.execute("SELECT * FROM user WHERE user='%s' AND password='%s'"%(username,password))
		row = cursor.fetchone()
		if row is not None:
			#cherrypy.session[row[0]] = str(row[1])
			if row[4] is None:
				ip = ''.join(random.sample(string.hexdigits, 15))
				cursor.execute("update user set status = 1, ip='%s' where id= %s"%(ip,row[0]))
				db.commit()
				db.close()

			#UNTUK AMBIL IP
			db= MySQLdb.connect('localhost','m26414093','tos987','m26414093')
			cursor = db.cursor()
			cursor.execute("SELECT * FROM user WHERE user='%s' AND password='%s'"%(username,password))
			row = cursor.fetchone()
			return header('lobby?id='+str(row[4]));
		else:
			return header('index');

	
	@cherrypy.expose
	def logout(self,user=''):

		db= MySQLdb.connect('localhost','m26414093','tos987','m26414093')
		cursor = db.cursor()
		cursor.execute("select * from user where ip='%s'"%(user))
		row = cursor.fetchone()
		db.close()

		db= MySQLdb.connect('localhost','m26414093','tos987','m26414093')
		cursor = db.cursor()
		cursor.execute("delete from game where player = %s "%(row[0]))
		db.commit()
		db.close()

		db= MySQLdb.connect('localhost','m26414093','tos987','m26414093')
		cursor = db.cursor()
		cursor.execute("update user set status=0,ip=NULL WHERE ip='%s'"%(user))
		db.commit()
		db.close()

		return header('index')

	
	@cherrypy.expose
	def get_game_header(self,room):
		db= MySQLdb.connect('localhost','m26414093','tos987','m26414093')
		cursor = db.cursor()
		cursor.execute("SELECT u.id,u.ip,u.user,g.status,g.bet,g.id FROM game g JOIN user u ON (g.player=u.id) WHERE idroom=%s"%str(room))
		json = "["
		c = 1
		for row in cursor.fetchall():
			json += '{'
			json += '"id":"' + str(row[0]) +'",'
			json += '"ip":"' + str(row[1]) +'",'
			json += '"player":"' + str(row[2]) +'",'
			json += '"status":"' + str(row[3]) +'",'
			json += '"bet":"' + str(row[4]) +'",'
			json += '"idgame":"' + str(row[5]) +'"'
			json += '}'
			if (c != cursor.rowcount):
				json += ','
			c += 1
		json += ']'
		db.close()
		return json

	@cherrypy.expose
	def shuffle_deck(self,room):
		decks = ['2S','3S','4S','5S','6S','7S','8S','9S','10S','JS','QS','KS','AS','2C','3C','4C','5C','6C','7C','8C','9C','10C','JC','QC','KC','AC','2H','3H','4H','5H','6H','7H','8H','9H','10H','JH','QH','KH','AH','2D','3D','4D','5D','6D','7D','8D','9D','10D','JD','QD','KD','AD']
		random.shuffle(decks)

		db= MySQLdb.connect('localhost','m26414093','tos987','m26414093')
		cursor = db.cursor()

		cursor.execute("SELECT * FROM deck WHERE idroom=%s"%room)
		if (cursor.rowcount != 0):
			return ''
		for deck in decks:
			cursor.execute("INSERT INTO deck VALUES(NULL,%s,'%s')"%(str(room),deck))
		db.commit()
		cursor.execute("SELECT * FROM game WHERE idroom = %s"%(str(room)))
		if cursor.rowcount == 0:
			return ''
		users = cursor.fetchall()

		for i in range(0,2):
			for user in users:
				cursor.execute("SELECT * FROM deck WHERE idroom=%s ORDER BY ID DESC"%(str(room)))
				if (cursor.rowcount == 0):
					return ''
				card = cursor.fetchone()
				cursor.execute("DELETE FROM deck WHERE idroom=%s AND id=%s"%(str(room),card[0]))
				db.commit()
				card = str(card[2])
				cursor.execute("INSERT INTO playing VALUES(null,%s,%s,'%s')"%(str(room),str(user[2]),card))
				db.commit()
		cursor.execute("SELECT * FROM game WHERE idroom=%s"%str(room))
		status = cursor.fetchall()
		for stat in status:
			if (stat != 'pass') or (stat != 'dead'):
				cursor.execute("UPDATE game SET status='playing' WHERE idroom=%s AND player=%s"%(str(room),str(stat[2])))
				db.commit()
		db.close()

		return ''

	@cherrypy.expose
	def draw_card(self,room,ip):
		db= MySQLdb.connect('localhost','m26414093','tos987','m26414093')
		cursor = db.cursor()
		cursor.execute("SELECT * FROM user WHERE ip ='%s'"%(str(ip)))
		row = cursor.fetchone()	   
		db.close()
		db= MySQLdb.connect('localhost','m26414093','tos987','m26414093')

		cursor = db.cursor()
		cursor.execute("SELECT * FROM deck WHERE idroom=%s ORDER BY ID DESC"%(str(room)))
		if (cursor.rowcount == 0):
			return ''
		card = cursor.fetchone()
		cursor.execute("DELETE FROM deck WHERE idroom=%s AND id=%s"%(str(room),card[0]))
		db.commit()
		db.close()
		return str(card[2])

	@cherrypy.expose
	def update_score(self,id,room,ip,score):
		db= MySQLdb.connect('localhost','m26414093','tos987','m26414093')
		cursor = db.cursor()
		cursor.execute("SELECT * FROM user WHERE ip='%s'"%(str(ip)))
		user = cursor.fetchone()
		cursor.execute("SELECT * FROM score WHERE idgame=%s"%(str(id)))
		if cursor.rowcount == 0:
			cursor.execute("INSERT INTO score VALUES(NULL,%s,%s,%s,%s)"%(str(room),str(user[0]),str(score),str(id)))
		else:
			cursor.execute("UPDATE score SET score=%s WHERE idgame=%s"%(str(score),str(id)))
		db.commit()
		return ''

	@cherrypy.expose
	def get_all_score(self,room):
		db= MySQLdb.connect('localhost','m26414093','tos987','m26414093')
		cursor = db.cursor()
		cursor.execute("SELECT player,score FROM score WHERE room=%s"%(str(room)))
		json = "["
		c = 1
		for row in cursor.fetchall():
			json += '{'
			json += '"player":"' + str(row[0]) +'",'
			json += '"score":"' + str(row[1]) +'"'
			json += '}'
			if (c != cursor.rowcount):
				json += ','
			c += 1
		json += ']'
		db.close()
		return json


	@cherrypy.expose
	def get_card(self,ip):
		db= MySQLdb.connect('localhost','m26414093','tos987','m26414093')
		cursor = db.cursor()
		cursor.execute("SELECT * FROM user WHERE ip='%s'"%(str(ip)))
		row = cursor.fetchone()
		cursor.execute("SELECT idcard FROM playing WHERE idplayer=%s"%(str(row[0])))
		json = "["
		c = 1
		for row in cursor.fetchall():
			json += '{'
			json += '"card":"' + str(row[0]) +'"'
			json += '}'
			if (c != cursor.rowcount):
				json += ','
			c += 1
		json += ']'
		db.close()
		return json

	@cherrypy.expose
	def get_card_other_player(self,id):
		db= MySQLdb.connect('localhost','m26414093','tos987','m26414093')
		cursor = db.cursor()
		cursor.execute("SELECT idcard FROM playing WHERE idplayer=%s ORDER BY id ASC"%(str(id)))
		card = cursor.fetchone()[0]
		json = '{"first":"' + str(card) + '","count":' + str(cursor.rowcount) + '}'
		return json

	@cherrypy.expose
	def get_deck(self,room):
		db= MySQLdb.connect('localhost','m26414093','tos987','m26414093')
		cursor = db.cursor()
		cursor.execute("SELECT * FROM deck WHERE idroom=%s"%(str(room)))
		db.close()
		return str(cursor.rowcount)

	@cherrypy.expose
	def status_pass(self,ip):
		db = MySQLdb.connect('localhost','m26414093','tos987','m26414093')
		cursor = db.cursor()
		cursor.execute("SELECT * FROM user WHERE ip='%s'"%(str(ip)))
		row = cursor.fetchone()
		cursor.execute("UPDATE game SET status='pass' WHERE player=%s"%(str(row[0])))
		db.commit()
		db.close()
		return ''

	@cherrypy.expose
	def status_dead(self,ip):
		db = MySQLdb.connect('localhost','m26414093','tos987','m26414093')
		cursor = db.cursor()
		cursor.execute("SELECT * FROM user WHERE ip='%s'"%(str(ip)))
		row = cursor.fetchone()
		cursor.execute("UPDATE game SET status='dead' WHERE player=%s"%(str(row[0])))
		db.commit()
		db.close()
		return ''

	@cherrypy.expose
	def update_playing(self,ruang,has,cards,id):
		db= MySQLdb.connect('localhost','m26414093','tos987','m26414093')
		cursor = db.cursor()
		cursor.execute("SELECT * FROM user WHERE ip ='%s'"%(str(has)))
		if (cursor.rowcount == 0):
			return ''
		db.close()

		db= MySQLdb.connect('localhost','m26414093','tos987','m26414093')
		cursor = db.cursor()
		cursor.execute("INSERT INTO playing VALUES(null,%s,%s,'%s')"%(str(ruang),str(id),str(cards)))
		db.commit()	
		db.close()

		return ''

	@cherrypy.expose
	def play(self,room,player):
		
		db= MySQLdb.connect('localhost','m26414093','tos987','m26414093')
		cursor = db.cursor()
		cursor.execute("SELECT * FROM game WHERE idroom=%s"%str(room))
		player_count = cursor.rowcount
		cursor.execute("SELECT * FROM game WHERE idroom=%s AND status = 'playing'"%(str(room)))

		if (cursor.rowcount == player_count):
			status = 'playing'
		else: 
			status = 'waiting'
		db.close()

		return '''<!DOCTYPE html>
					<html>
					<head>
						<title>
							Blackjack Muliplayer - Online
						</title>
						<link rel="stylesheet" type="text/css" href="style.css">
						<script type="text/javascript" src="jquery.js"></script>
						<script>
							var room = '''+room+''';
							var ip = "'''+player+'''";
							var status = "'''+status+'''";
						</script>
						<script type="text/javascript" src="game.js"></script>
					</head>
					<body class=rel>
					<strong>Player's status</strong>
					<p id="players"></p>
					<div class="deck">
					</div>
					<div id="draw">
					<button id="draw-card" style="position:absolute;left:27%"><h5>Draw</h5></button>
					</div>
					<div id="pass">
					<button id="pass-turn" style="position:absolute;left:35%"><h5>Pass</h5></button>
					</div>
					<div class="player" id="player1">

						<h3 id="player1Label"><h3>
						<div class="hand"></div>
					</div>
					<div class="player" id="player2">
						<h3 id="player2Label"><h3>
						<div class="hand"></div>
					</div>
					<div class="player" id="player3">
						<h3 id="player3Label"><h3>
						<div class="hand">
						</div>
					</div>
					<div class="player" id="player4">
						<h3 id="player4Label"><h3>
						<div class="hand">
						</div>
					</div>
					</body>
					</html>'''


	@cherrypy.expose
	def get_player_in_lobby(self,room=1):
		db= MySQLdb.connect('localhost','m26414093','tos987','m26414093')
		cursor = db.cursor()
		cursor.execute("SELECT u.user FROM game g JOIN user u ON (g.player=u.id) WHERE g.idroom=%s AND u.ip <> ''"%(str(room)))
		

		json = "["
		c = 1
		for row in cursor.fetchall():
			json += '{'
			json += '"name":"' + str(row[0]) +'"'
			json += '}'
			if (c != cursor.rowcount):
				json += ','
			c += 1
		json += ']'
		db.close()
		return json


	@cherrypy.expose
	def exit_lobby(self,id=0,ip=''):
		db= MySQLdb.connect('localhost','m26414093','tos987','m26414093')
		cursor = db.cursor()
		cursor.execute("DELETE from game WHERE player=%s"%(str(id)))
		db.commit()
		return header('lobby?id=' + ip)
	
	@cherrypy.expose
	def count_score(self,room):
		db= MySQLdb.connect('localhost','m26414093','tos987','m26414093')
		cursor = db.cursor()
		cursor.execute("SELECT id,player FROM game WHERE idroom=%s"%str(room))
		players = cursor.fetchall()
		for player in players:
			cursor.execute("SELECT idcard FROM playing WHERE idroom=%s AND idplayer=%s"%(str(room),str(player[1])))
			cards = cursor.fetchall()
			myScore = 0
			for card in cards:
				if myScore <= 10 and card[0][0] == 'A':
					myScore += 11
				elif myScore > 10 and card[0][0] == 'A':
					myScore += 1
				elif card[0][0] == 'J' or card[0][0] == 'Q' or card[0][0] == 'K' or card[0][:2] == '10':
					myScore += 10
				else: 
					myScore += int(card[0][0])

			cursor.execute("SELECT * FROM score WHERE idgame=%s"%(str(player[0])))
			if cursor.rowcount == 0:
				cursor.execute("INSERT INTO score VALUES(NULL,%s,%s,%s,%s)"%(str(room),str(player[1]),str(myScore),str(player[0])))
			else:
				cursor.execute("UPDATE score SET score=%s WHERE idgame=%s"%(str(myScore),str(player[0])))
			db.commit()
		db.close()
		return ''

	@cherrypy.expose
	def gameover(self,room,ip):
		db= MySQLdb.connect('localhost','m26414093','tos987','m26414093')
		cursor = db.cursor()
		cursor.execute("SELECT id,player FROM game WHERE idroom=%s"%str(room))
		players = cursor.fetchall()
		for player in players:
			cursor.execute("SELECT idcard FROM playing WHERE idroom=%s AND idplayer=%s"%(str(room),str(player[1])))
			cards = cursor.fetchall()
			myScore = 0
			temp1 = 0
			temp2 = 0
			for card in cards:
				if card[0][0] == 'A':
					temp1 += 1
					temp2 += 11
				elif card[0][0] == 'J' or card[0][0] == 'Q' or card[0][0] == 'K' or card[0][:2] == '10':
					temp1 += 10
					temp2 += 10
				else: 
					temp1 += int(card[0][0])
					temp2 += int(card[0][0])
			if temp1 > temp2 and temp1 <= 21:
				myScore = temp1
			elif temp2 > temp1 and temp2 <= 21:
				myScore = temp2
			elif temp1 < temp2:
				myScore = temp1
			else:
				myScore = temp2
			cursor.execute("SELECT * FROM score WHERE idgame=%s"%(str(player[0])))
			if cursor.rowcount == 0:
				cursor.execute("INSERT INTO score VALUES(NULL,%s,%s,%s,%s)"%(str(room),str(player[1]),str(myScore),str(player[0])))
			else:
				cursor.execute("UPDATE score SET score=%s WHERE idgame=%s"%(str(myScore),str(player[0])))
			db.commit()

		cursor.execute("SELECT * FROM playing WHERE idroom=%s"%str(room))
		if cursor.rowcount > 0:
			cursor.execute("SELECT SUM(bet) FROM game WHERE idroom=%s"%str(room))
			bet = cursor.fetchone()
			cursor.execute("SELECT * FROM score WHERE room=%s AND score=(SELECT MAX(score) FROM score WHERE room=%s AND score <= 21)"%(str(room),str(room)))
			playerCount = cursor.rowcount
			playersWin = cursor.fetchall()
			if playerCount > 0:
				betPerPlayer = int(bet[0]) / int(playerCount)
				cursor.execute("SELECT * FROM user WHERE ip='%s'"%ip)
				user = cursor.fetchone()[0]
				for player in playersWin:
					if player[2] == user:
						cursor.execute("SELECT money FROM user WHERE id=%s"%str(user))
						money = cursor.fetchone()
						restMoney = int(money[0]) + int(betPerPlayer)
						cursor.execute("UPDATE user SET money=%s WHERE id=%s"%(str(restMoney),str(user)))
						db.commit()
					
			cursor.execute("UPDATE game SET status='betting' WHERE idroom=%s"%str(room))
			db.commit()
			cursor.execute("DELETE FROM deck WHERE idroom=%s"%str(room))
			db.commit()
		cursor.execute("SELECT * FROM score WHERE room=%s"%(str(room)))
		scores = cursor.fetchall()
		out = "<table margin=7px >"
		for row in scores:
			cursor.execute("SELECT * FROM user WHERE id=%s"%str(row[2]))
			name = cursor.fetchone()
			out += '<tr><td>' + str(name[1]) + ' &nbsp &nbsp</td>'  
			out += '<td>' + str(row[3]) + '</td></tr>'
		out += "</table>"
		return  '''<!DOCTYPE html>
					<html>
					<head>
						<title>
							Blackjack Muliplayer - Online
						</title>
						<style>
						.back
						{
						 background: url("winner.jpg") no-repeat;
						}
						.players{   
						position:absolute;
							left : 200px;
							top : 268px;
							color :  orange;
							font-size: 2em ;
							 font-family: Impact, Charcoal, sans-serif;
						}
						</style>
					</head>
					<body onload="myFunction()" class=back>
					<strong>Player's Win Board</strong>
					<div class='players'>
					'''+out+'''
					</div>
					</body>
					<script>
						var  myVar;
						function myFunction() {
    						myVar = setTimeout(betFunc, 10000);
						}
						function betFunc()
						{
							document.location="bet?ip='''+ip+'''&room='''+room+'''";
						}
					</script>
					</html>'''
	@cherrypy.expose
	def bet(self,ip='',room=1):
		db= MySQLdb.connect('localhost','m26414093','tos987','m26414093')
		cursor = db.cursor()
		cursor.execute("SELECT * FROM user WHERE ip='%s'"%(ip))
		row = cursor.fetchone()
		db.close()
		if (cursor.rowcount == 0):
			header('index')

		db= MySQLdb.connect('localhost','m26414093','tos987','m26414093')
		cursor = db.cursor()
		cursor.execute("DELETE FROM playing WHERE idroom=%s AND idplayer=%s"%(str(room),str(row[0])))
		db.commit()
		cursor.execute("SELECT * FROM game WHERE player=%s "%row[0])

		if (cursor.rowcount > 0):
			game = cursor.fetchone()
			if (game[3] != 'betting'):
				header('play?room=%s&player=%s'%(str(room),ip))
			cursor.execute("UPDATE game set idroom=%s,status='betting',bet=0 WHERE player=%s"%(str(room),row[0]))
			db.commit()
		else:
			cursor.execute("INSERT INTO game VALUES(null,%s,%s,'betting',0)"%(str(room),row[0]))
			db.commit()
		db.close()
		cancelLink = 'exit_lobby?id='+str(row[0])+'&ip='+str(ip)

		return '''<html>
					 <style>
						.back
						{
						 background: url("bet.png") no-repeat;
						}
						#players{   
						position:absolute;
							left : 530px;
							top : 110px;
							color :  orange;
							font-size: 1.5em ;
							 font-family: Impact, Charcoal, sans-serif;
						}
						#lobby{   
						position:absolute;
							left : 100px;
							top : 510px;
							color :  darkblue;
							font-size: 1.5em ;
							 font-family: Impact, Charcoal, sans-serif;
						}
						#label_card{
							position:absolute;
							left : 90px;
							top : 190px;
							color :  orange;
							font-size: 1.5em ;
							 font-family: Impact, Charcoal, sans-serif;
						}
						#label_money{
							position:absolute;
							left : 100px;
							top : 227px;
							color :  orange;
							font-size: 1.5em ;
							 font-family: Impact, Charcoal, sans-serif;
						}
						#bets{
							position:absolute;
							left : 120px;
							top : 400px;
							color :  orange;
							font-size: 1em ;
							 font-family: Impact, Charcoal, sans-serif;
						}
						#play
						{
							position : absolute;
							top : 40px;
							left: 510px;
							width : 1px;
							height : 1px;
						}
						</style>
						<script src="/jquery.js"></script>
						<script src="/inner_lobby.js"></script>
						<body class=back>
							 <label id="label_card">'''+ str(row[1])+'''</label>
							<label id="label_money">'''+ str(row[3])+'''</label>
							<script>
								var lobby = '''+str(room)+''';
								var ip = "'''+str(ip)+'''";
							</script>
							<script type="text/javascript" src="/jquery.js"></script>
							<script type="text/javascript" src="/inner_lobby.js"></script>
							
							<div id="players"></div>

							
							<div id="lobby">Betting in Lobby '''+str(room)+'''</div>
							<form action="update_bet" method="post">
								<input type="hidden" name="room" value="'''+room+'''">
							
									<input type="text" hidden value="'''+str(row[1])+'''" readonly><br/>
							
									<input type="text" hidden value="'''+str(row[3])+'''" readonly><br/>
									 
								
									<input type="text" name="user_ip" value="'''+str(ip)+'''" hidden readonly>
									
									<div id="bets">
										<input type="text" name="bet" required>
										<button id="play" type="submit" alt="submit"><img src="play.png" width="150px" height="150px"></button>
										<a href="'''+cancelLink+'''">Cancel</a>
									</div>
								  
							</form>
						</body>
				  </html>'''

	@cherrypy.expose
	def update_bet(self,user_ip='',bet='',room=1):
		db= MySQLdb.connect('localhost','m26414093','tos987','m26414093')
		cursor = db.cursor()
		cursor.execute("SELECT id,money - %s FROM user WHERE ip='%s'"%(bet,user_ip))
		row = cursor.fetchone()
		db.close()

		db= MySQLdb.connect('localhost','m26414093','tos987','m26414093')
		cursor = db.cursor()
		cursor.execute("UPDATE game SET bet=%s,status='ready' WHERE player='%s' AND idroom=%s"%(bet,row[0],room))
		db.commit()
		db.close()


		db= MySQLdb.connect('localhost','m26414093','tos987','m26414093')
		cursor = db.cursor()
		cursor.execute("update user set money=%s WHERE id=%s"%(row[1],row[0]))
		db.commit()
		db.close()

		return header('play?room=%s&player=%s'%(str(room),user_ip))

	@cherrypy.expose
	def lobby(self,id=-1):
		if id == -1:
			return header('index')
		db= MySQLdb.connect('localhost','m26414093','tos987','m26414093')
		cursor = db.cursor()
		cursor.execute("SELECT * FROM user WHERE ip='%s'"%str(id))
		playerID = cursor.fetchone()[0]
		cursor.execute("DELETE FROM game WHERE player=%s"%str(playerID))
		db.commit()
		html = '''<!DOCTYPE html>
						<html>
						<head>
							<title>Blackjack Online - Lobby</title>
							<script type="text/javascript" src="/jquery.js"></script>
							<script type="text/javascript" src="/lobby.js"></script>
						</head>
						<style>
						.back
						{
						 background: url("lobby.png") no-repeat;
						}
						#players{   
							position:absolute;
							left : 100px;
							top : 120px;
							color : darkblue;
							font-size: 1.5em ;
							 font-family: Impact, Charcoal, sans-serif;
						}
						#player-count{  
							position:absolute; 
							top : 63px;
							left : 380px;
							color :  white;
							font-size: 2em ;
							 font-family: Impact, Charcoal, sans-serif;
						}
						.kanan
						{
							bottom: 230px;
							position : absolute;
							left:500px;
							font-size: 2.5em ;
							font-family: Impact, Charcoal, sans-serif;
						}
						.kanan1
						{
							bottom: 230px;
							position : absolute;
							left:500px;
							font-size: 2.5em ;
							font-family: Impact, Charcoal, sans-serif;
						}
						#label_card
						{
							bottom : 100px;
							position:absolute;
							left : 550px;
							color :  black;
							font-size: 1.5em ;
							font-family: Impact, Charcoal, sans-serif;
						}
						#lobbybutton
						{
							top: 130px;
							position : absolute;
							left:500px;
							font-size: 1.0em ;
							font-family: Impact, Charcoal, sans-serif;
						}
						
						</style>
						<body class=back >'''
		html += '''<br><br><br><text id="player-count"></text><br><br><table id="players" ></table>'''
		html += '''<div id="lobbybutton"><form action="bet" method="post"><input type="hidden" value="1" name="room"><input type="text" name="ip" value="'''+id+'''" hidden readonly><button type="submit">Lobby 1</button></form>'''
		html += '''<form action="bet" method="post"><input type="hidden" value="2" name="room"><input type="text" name="ip" value="'''+id+'''" hidden readonly><button type="submit">Lobby 2</button></form>'''
		html += '''<form action="bet" method="post"><input type="hidden" value="3" name="room"><input type="text" name="ip" value="'''+id+'''" hidden readonly><button type="submit">Lobby 3</button></form>'''
		html += '''<form action="bet" method="post"><input type="hidden" value="4" name="room"><input type="text" name="ip" value="'''+id+'''" hidden readonly><button type="submit">Lobby 4</button></form></div>'''
		html += '''<form action="bet" method="post"><input type="text" name="ip" value="'''+id+'''" hidden readonly><div class=kanan><button type="submit" hidden><h1>Play</h1></button></div></form>'''
		html += '''<form action="logout" method="post"><input type="text" name="user" value="'''+id+'''" hidden readonly><div class=kanan1><button type="submit"><h3>Logout</h3></button></div></form>'''
		
		db= MySQLdb.connect('localhost','m26414093','tos987','m26414093')
		cursor = db.cursor()
		cursor.execute("SELECT * FROM user WHERE ip='%s'"%(id))
		
		row = cursor.fetchone()
		html += '''<label id="label_card">'''+ str(row[1]) + '''</label>
					<label id="label_card" style="color:orange;bottom:53px;">'''+ str(row[3])+'''</label></body></html>'''
		db.close()
		return html

	@cherrypy.expose
	def get_all_players(self):
		db= MySQLdb.connect('localhost','m26414093','tos987','m26414093')
		cursor = db.cursor()
		cursor.execute("SELECT id,user,money FROM user WHERE ip <> ''")
		db.close()
		json = "["
		c = 1
		for row in cursor.fetchall():
			json += '{'
			json += '"id":"' + str(row[0]) + '",'
			json += '"user":"' + str(row[1]) + '",'
			json += '"money":"' + str(row[2]) + '"'
			json += '}'
			if (c != cursor.rowcount):
				json += ','
			c += 1
		json += ']'
		return json

if __name__ == '__main__':

	conf = {
			 '/': {
				'tools.sessions.on': True,
				'tools.staticdir.on' : True,
				'tools.staticdir.root' : \
					os.path.abspath(os.getcwd()),
				'tools.staticdir.dir' : \
					os.path.abspath(os.path.join(os.path.dirname(__file__), 'assets'))
			 }
			}
	cherrypy.quickstart(HelloWorld(), '/', conf)
