#!/usr/bin/env python3
import sys

def process_file(filename):
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.stderr.write(f"Error: File '{filename}' not found.\n")
        return
    
    for line in lines[1:]:
        line = line.strip()
        print(line)

        if not line:
          continue

        parts= line.split(',')
        if len(parts) < 3:
            sys.stderr.write(f"Error: Missing parameters '{line}'\n")
            continue

        name,email,id=parts
        email_parts=email.split('@')
        if(len(email_parts) != 2):
            sys.stderr.write(f"Error: Invalid email '{email}'\n")
            continue

        if len(email_parts[1].split('.')) < 2:
            sys.stderr.write(f"Error: Invalid email '{email}'\n")
            continue

        try:
         user_id = int(id)
        except ValueError:
            sys.stderr.write(f"Error: Invalid user ID '{id}'\n")
            continue
        parity = "even" if user_id % 2 == 0 else "odd"
        sys.stdout.write(f"The ID: {user_id} of Email: {email} is {parity} \n")
       



if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python script.py <filename>\n")
        sys.exit(1)
    process_file(sys.argv[1])