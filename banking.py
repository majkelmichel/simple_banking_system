import random
import sqlite3

conn = sqlite3.connect('card.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='card';")
if len(cur.fetchall()) == 0:
    cur.execute('CREATE TABLE card (id INTEGER , number TEXT, pin TEXT, balance INTEGER DEFAULT 0);')
    conn.commit()
card_id = 1
num_pin = tuple()

cur.execute("SELECT number FROM card")
ca = cur.fetchall()
card_numbers = set()
for c in ca:
    card_numbers.add(c[0])


def generate_card_number():
    iin = "400000"
    acc_num = ""
    for i in range(9):
        acc_num += str(random.randint(0, 9))
    checksum = generate_checksum(iin, acc_num)
    return f"{iin}{acc_num}{checksum}"


def generate_checksum(bank_id_num, acc_id_num):
    card_num = f'{bank_id_num}{acc_id_num}'
    c_nums = []
    for i in card_num:
        c_nums.append(int(i))
    for i in range(len(c_nums)):
        if i % 2 == 0:
            c_nums[i] *= 2
        if c_nums[i] > 9:
            c_nums[i] -= 9
    suma = 0
    for i in c_nums:
        suma += i
    checksum = 0
    for i in range(suma, suma + 10):
        if (checksum + suma) % 10 == 0:
            return checksum
        checksum += 1


def generate_card_pin():
    pin = ""
    for i in range(4):
        pin += str(random.randint(0, 9))
    return pin


def create_account():
    global card_id
    print()
    print("Your card has been created")
    print("Your card number:")
    card_number = generate_card_number()
    print(card_number)
    print("Your card PIN:")
    card_pin = generate_card_pin()
    print(card_pin)
    print()
    cur.execute("INSERT INTO card VALUES (?, ?, ?, ?)", (card_id, card_number, card_pin, 0))
    conn.commit()
    card_numbers.add(card_number)
    card_id += 1


def check_card_number(card_num):
    check_sum = generate_checksum(card_num[0:6], card_num[6:15])
    # print(card_num, card_num[0:6] + card_num[6:15] + str(check_sum))
    return card_num == card_num[0:6] + card_num[6:15] + str(check_sum)


def log_in():
    print()
    num = input("Enter your card number:\n")
    pin = input("Enter your PIN:\n")
    global num_pin
    cur.execute("SELECT number, pin, balance FROM card WHERE number = ?", (num,))
    num_pin = cur.fetchall()
    conn.commit()
    if len(num_pin) < 1:
        print("\nWrong card number or PIN!\n")
        return None
    if num == num_pin[0][0] and pin == num_pin[0][1]:
        print("\nYou have successfully logged in!\n")
        return account_management()
    else:
        print("\nWrong card number or PIN!\n")


def account_management():
    global num_pin
    while True:
        print("1. Balance", "2. Add income", "3. Do transfer", "4. Close account", "5. Log out", "0. Exit", sep='\n')
        choice = int(input())
        if choice == 5:
            print("\nYou have successfully logged out!\n")
            return False
        elif choice == 2:
            deposit_value = input("\nEnter income:\n")
            cur.execute("UPDATE card SET balance = balance + ? WHERE number = ?;", (deposit_value, num_pin[0][0]))
            cur.execute("SELECT number, pin, balance FROM card WHERE number = ?", (num_pin[0][0],))
            num_pin = cur.fetchall()
            conn.commit()
            print("Income was added!\n")
        elif choice == 3:
            transfer_money()
        elif choice == 4:
            cur.execute("DELETE FROM card WHERE number = ?", (num_pin[0][0],))
            conn.commit()
            print("\nThe account has been closed!\n")
        elif choice == 1:
            print(f"\nBalance: {num_pin[0][2]}\n")
        elif choice == 0:
            print("Bye!")
            return True


def transfer_money():
    global card_numbers
    global num_pin
    print("\nTransfer")
    to_card = input("Enter card number:\n")
    if check_card_number(to_card):
        if to_card not in card_numbers:
            print("Such a card does not exist.\n")
            return False
        else:
            print("Enter how much money you want to transfer:")
            money_to_transfer = int(input())
            if money_to_transfer > num_pin[0][2]:
                print("Not enough money!\n")
            else:
                cur.execute("UPDATE card SET balance = balance + ? WHERE number = ?", (money_to_transfer, to_card))
                cur.execute("UPDATE card SET balance = balance - ? WHERE number = ?", (money_to_transfer, num_pin[0][0]))
                conn.commit()
                print("Success!\n")
        return False
    else:
        print("Probably you made a mistake in the card number. Please try again!\n")
        return True


while True:
    menu = "1. Create and account\n2. Log into account\n0. Exit"
    print(menu)
    option = int(input())
    if option == 0:
        print()
        print("Bye!")
        break
    elif option == 1:
        create_account()

    elif option == 2:
        if log_in():
            break
