#!/usr/bin/python3
import db
import bcrypt

res = 0

def create_central_bank():
	print("===== CREATE CENTRAL BANK =====\n")
	id = input(">>> Enter your ID: ")
	pwd = input(">>> Enter your password: ")
	pwd = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt(10))
	
	query = db.execute_query("INSERT INTO central_bank (central_bank_id, password_hash) "
	"VALUES (%s, %s)",
	(id, pwd))

	if query:
		print("Central bank successfully created!")
		login()

def login():
	print("\n===== LOGIN =====\n")

	while True:
		id = input(">>> Enter your ID or Bank name: ")
		pwd = input(">>> Enter your password: ")

		central_bank = db.fetch_one(f"SELECT * FROM central_bank WHERE central_bank_id={id}")
		commercial_bank = db.fetch_one(f"SELECT * FROM commercial_banks WHERE bank_name='{str(id)}'")

		if central_bank:
			if bcrypt.checkpw(pwd.encode('utf-8'), central_bank['password_hash'].encode('utf-8')):
				print("\nSuccessfully logged in")
				return 1
				break
			else:
				print("Incorrect password. Try again!")
		elif commercial_bank:
			if bcrypt.checkpw(pwd.encode('utf-8'), commercial_bank['password_hash'].encode('utf-8')):
				print("\nSuccessfully logged in")
				return 2
				break
			else:
				print("Incorrect password. Try again!")
		else:
			print("No bank found with those credentials\n")

def create_commercial_bank():
	print("\n==== CREATE COMMERCIAL BANK ====\n")

	bank_name = input(">>> Enter bank name: ")
	password = input(">>> Enter bank initial Password: ").encode('utf-8')
	eligibility = input(">>> Is the bank eligible [y\\n]: ")
	borrowing_limit = input(">>> Enter borrowing limit: ")

	query = db.execute_query("INSERT INTO commercial_banks (bank_name, password_hash, eligibility, borrowing_limit) "
	"VALUES(%s, %s, %s, %s)",
	(bank_name, bcrypt.hashpw(password, bcrypt.gensalt(10)) , "eligible" if eligibility == "y" else "none", borrowing_limit))

	if query:
		print("\nCommercial bank successfully created!")
	else:
		print("\nCommercial bank creation failed!")
		
	ui(res)

def ui(res):
	choice = ""

	if res == 1:
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
		choice = int(input(">>> "))
	elif res == 2:
		print("""\n==== BANK MENU ====
  
1. Change password
2. Manage collateral inventory
3. Submit a loan request
4. Check status of my request
5. View my reports
6. View my past weekly operations (read-only)
7. Log out
""")
		choice = int(input(">>> "))
	handle_choices(choice, res)

def handle_choices(choice, res):
	if res == 1:
		match choice:
			case 1:
				create_commercial_bank()
			case _:
				print("\nInvalid input. Try again.")
				ui(res)
	if res == 2:
		pass

def start():
	central_banks = db.fetch_all("SELECT * FROM central_bank")

	if len(central_banks) > 0:
		res = login()
		ui(res)
	else:
		create_central_bank()

start()