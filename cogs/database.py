import sqlite3
import time

connection = sqlite3.connect("data.db")
cursor = connection.cursor()

def initializeDatabase():
	cursor.execute("""
		CREATE TABLE IF NOT EXISTS Blackjack (
			UserID INT PRIMARY KEY,
			Money INT NOT NULL DEFAULT 0,
			FreeMoneyCooldown TIMESTAMP NOT NULL DEFAULT 0
		);
	""")
	cursor.execute("""
		CREATE TABLE IF NOT EXISTS BlackjackGames (
			GameID INTEGER PRIMARY KEY,
			UserID INT NOT NULL,
			GuildID INT NOT NULL,
			UserMoney INT NOT NULL,
			Bet INT NOT NULL,
			UserCards TINYTEXT NOT NULL,
			DealerCards TINYTEXT NOT NULL,
			Deck TINYTEXT NOT NULL
		);
	""")
	cursor.execute("""
		CREATE TABLE IF NOT EXISTS Brains (
			GuildID INT PRIMARY KEY,
			Brain TINYTEXT
		);
	""")
	cursor.execute("""
		CREATE TABLE IF NOT EXISTS Roles (
			RoleID INT
		);
	""")
	connection.commit()



# ========== BLACKJACK ==========

def addBlackjackUser(user):
	cursor.execute("""
		INSERT OR IGNORE INTO Blackjack (UserID)
		VALUES (?);
	""", (user,))
	connection.commit()

def getAllBlackjackMoney():
	cursor.execute("""
		SELECT UserID, Money
		FROM Blackjack
		ORDER BY Money DESC;
	""")
	return cursor.fetchall()

def getBlackjackMoney(user):
	cursor.execute("""
		SELECT Money
		FROM Blackjack
		WHERE UserID = ?;
	""", (user,))
	return cursor.fetchone()[0]

def setBlackjackMoney(user, money):
	cursor.execute("""
		UPDATE Blackjack
		SET Money = ?
		WHERE UserID = ?;
	""", (money, user))
	connection.commit()

def increaseBlackjackMoney(user, money):
	cursor.execute("""
		UPDATE Blackjack
		SET Money = Money + ?
		WHERE UserID = ?;
	""", (money, user))
	connection.commit()

def decreaseBlackjackMoney(user, money):
	cursor.execute("""
		UPDATE Blackjack
		SET Money = Money - ?
		WHERE UserID = ?;
	""", (money, user))
	connection.commit()

def getBlackjackCooldown(user):
	cursor.execute("""
		SELECT FreeMoneyCooldown
		FROM Blackjack
		WHERE UserID = ?;
	""", (user,))
	return cursor.fetchone()[0]

def setBlackjackCooldown(user, cooldown):
	cursor.execute("""
		UPDATE Blackjack
		SET FreeMoneyCooldown = ?
		WHERE UserID = ?;
	""", (cooldown, user))
	connection.commit()

def getAllBlackjackActiveCooldowns():
	cursor.execute("""
		SELECT UserID
		FROM Blackjack
		WHERE FreeMoneyCooldown > ?;
	""", (time.time(),))
	return list(i[0] for i in cursor.fetchall())

def resetBlackjackCooldowns():
	cursor.execute("""
		UPDATE Blackjack
		SET FreeMoneyCooldown = 0;
	""")
	connection.commit()

def recordBlackjackGame(userID, guildID, userMoney, bet, userCards, dealerCards, deck):
	cursor.execute("""
		INSERT INTO BlackjackGames (UserID, GuildID, UserMoney, Bet, UserCards, DealerCards, Deck)
		VALUES (?, ?, ?, ?, ?, ?, ?)
	""", (userID, guildID, userMoney, bet, userCards, dealerCards, deck))
	connection.commit()



# ========== COBE ==========

def addGuild(guildID):
	cursor.execute("""
		INSERT OR IGNORE INTO Brains (GuildID)
		VALUES (?);
	""", (guildID,))
	connection.commit()

def getGuildsBrain(guildID):
	cursor.execute("""
		SELECT Brain
		FROM Brains
		WHERE GuildID = ?;
	""", (guildID,))
	return cursor.fetchone()[0]

def setGuildsBrain(guildID, brain):
	cursor.execute("""
		UPDATE Brains
		SET Brain = ?
		WHERE GuildID = ?;
	""", (brain, guildID))
	connection.commit()



# ========== ROLES ==========

def getAllRoles():
	cursor.execute("""
		SELECT RoleID
		FROM Roles;
	""")
	return list(i[0] for i in cursor.fetchall())

def addRole(role):
	cursor.execute("""
		INSERT INTO Roles
		VALUES (?);
	""", (role,))
	connection.commit()

def deleteRole(role):
	cursor.execute("""
		DELETE
		FROM Roles
		WHERE RoleID = ?;
	""", (role,))
	connection.commit()