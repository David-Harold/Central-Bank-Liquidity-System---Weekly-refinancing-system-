#!/usr/bin/python3
import db
import bcrypt


def create_central_bank():
	print("===== CREATE CENTRAL BANK =====")
	id = input(">>> Enter your ID: ")
	pwd = input(">>> Enter your password: ")
	pwd = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt(10))
	
	db.execute_query("INSERT INTO central_bank (central_bank_id, password_hash) "
	"VALUES (%s, %s)",
	(id, pwd))

	central_bank_login()

def central_bank_login():
	print("===== LOGIN =====")

	while True:
		id = input(">>> Enter your ID: ")
		pwd = input(">>> Enter your password: ")

		central_bank = db.fetch_one("SELECT * FROM central_bank")

		if central_bank:
			if bcrypt.checkpw(pwd.encode('utf-8'), central_bank['password_hash'].encode('utf-8')):
				print("\n Successfully logged in")
				return True
				break
			else:
				print("Try again!")

def start():
	central_banks = db.fetch_all("SELECT * FROM central_bank")

	if len(central_banks) > 0:
		central_bank_login()
		while True:
			print("""\n==== CENTRAL BANK MENU ====
	1. Create a new bank
	2. Set/update bank eligibility
	3. Define admissible collateral type & haircut
	4. Set/update bank borrowing limit
	5. Open a new weekly operation
	6. Close current weekly operation
	7. Review pending requests
	8. Settle an approved request
	9. View reports
	10. View past weekly operations (read-only)
	11. Log out
	""")
			input(">>> ")
	else:
		create_central_bank()

start()