from flask import Flask, request, jsonify  # type: ignore
import sqlite3
import random
from flask_cors import CORS
from flask_mail import Mail, Message  # type: ignore

app = Flask(__name__)
CORS(app)


storage = ['email', 'password', 'name', 'id']
storage_signin = ['email', 'password', 'name', 'code']
storage_forget=['email','code']

notepadcount = 0


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = ''  
app.config['MAIL_PASSWORD'] = ''  
app.config['MAIL_DEFAULT_SENDER'] = ''  

mail = Mail(app)



def send_email():
    try:
        email = storage_signin[0]
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
        existing_email = cursor.fetchone()
        if existing_email:
            conn.close()
            return jsonify({"error": f"This email is already in use: {email}"}), 409
        else:
            conn.close()
            random_code = random.randint(1, 999999)
            storage_signin[3] = random_code  

            recipient = storage_signin[0]  
            subject = 'Identification'
            body = f'Your identification code is: {random_code}'
        
            try:
                msg = Message(subject=subject, recipients=[recipient])
                msg.body = body
                mail.send(msg)
                print("Email sent successfully!")  
                return jsonify({"message": "Succes!"}), 200
            except Exception as e:
                print(f"Error: {str(e)}")  
                return jsonify({"error": f"Failed to send email. {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": f"Error occurred: {str(e)}"}), 500
    


def get_db_connection():
    conn = sqlite3.connect('Mydata.db')
    conn.row_factory = sqlite3.Row
    return conn


def Student_signin():
    try:
        storage[2]=storage_signin[2]
        storage[0]=storage_signin[0]
        storage[1]=storage_signin[1]
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (storage_signin[2], storage_signin[0], storage_signin[1]),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "User successfully signed in!"}), 200
    except Exception as e:
        return jsonify({"error": f"Error occurred: {str(e)}"}), 500


@app.route('/api-enter', methods=['POST'])
def Student_signin_enter():
    data = request.json
    storage_signin[0] = data['email']
    storage_signin[1] = data['password']
    storage_signin[2] = data['name']
    return send_email()

@app.route('/api-enter-end', methods=['POST'])
def Student_enter_end():
    data = request.json
    code=data['code']
    if str(code)==str(storage_signin[3]):
        return Student_signin()
    elif str(code)==str(storage_forget[1]):
        return jsonify({ 'message': "User successfully signed in!"}), 200
    else:
        return jsonify({ 'message': "Code isn't true"}), 400

@app.route('/api-forget', methods=['POST'])
def Student_forget_enter():
    data = request.json
    storage_forget[0] = data['email']
    storage[0]=data['email']
    random_code = random.randint(1, 999999)
    storage_forget[1] = random_code  
   
    recipient = storage_forget[0]  
    subject = 'Identification'
    body = f'Your identification code is: {random_code}'
        
    try:
        msg = Message(subject=subject, recipients=[recipient])
        msg.body = body
        mail.send(msg)
        print("Email sent successfully!")  
        return jsonify({"message": "Succes!"}), 200
    except Exception as e:
        print(f"Error: {str(e)}")  
        return jsonify({"error": f"Failed to send email. {str(e)}"}), 500


@app.route('/api1', methods=['POST'])
def Student_login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password are required'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT email, password FROM users WHERE email = ? AND password = ?",
            (email, password),
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            storage[0] = email
            storage[1] = password
            return jsonify({'success': True, 'message': 'Login successful'})
        else:
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
    except Exception as e:
        print(f"Error: {str(e)}")  
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
    
@app.route('/data')
def Student_data():  
    conn = get_db_connection()
    conn.row_factory=sqlite3.Row
    cursor = conn.cursor()
    cursor1= conn.cursor()
    cursor2= conn.cursor()
    cursor.execute("SELECT name FROM users WHERE email = ? ", (storage[0],))
    cursor1.execute("SELECT id FROM users WHERE email = ? ", (storage[0],))
    cursor2.execute("SELECT password FROM users WHERE email = ? ", (storage[0],))
    row = cursor.fetchone()
    row1=cursor1.fetchone()
    row2=cursor2.fetchone()
    storage[1]=row2['password']
    storage[2]=row['name']
    storage[3]=row1['id']
    cursor.close()
    cursor1.close()
    conn.close()
    return jsonify({'email':storage[0], 'password':storage[1],'name':storage[2],'id':storage[3]}) 

@app.route('/calendar-save', methods=['POST'])
def calendar_save():
    data = request.json
    if not all(key in data for key in ('id', 'time', 'text')):
        return jsonify({"error": "Invalid input data"}), 400
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT text FROM calendar WHERE id = ? AND time = ?", (data['id'], data['time']))
        record = cursor.fetchone()
        
        if record:
            cursor.execute("UPDATE calendar SET text = ? WHERE id = ? AND time = ?", 
                           (data['text'], data['id'], data['time']))
            message = "Updated successfully!"
        else:
            cursor.execute("INSERT INTO calendar (id, time, text) VALUES (?, ?, ?)", 
                           (data['id'], data['time'], data['text']))
            message = "Created successfully!"
        
        conn.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
    
    return jsonify({"message": message}),200

@app.route('/calendar-data', methods=['POST'])
def calendar_data():
    data = request.json
    user_id = storage[3]
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT text FROM calendar WHERE id = ? AND time = ?", (user_id, data['time']))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row:
        text = row['text']
    else:
        text = ""

    return jsonify({'text': text})

@app.route('/notepad-get-count')
def notepad_get_count():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(id) as count FROM notpad WHERE id = ?;", (storage[3],))
    row = cursor.fetchone()
    count = row['count'] if row else 0
    notepadcount=count
    cursor.close()
    conn.close()
    return jsonify({'count': count})

@app.route('/notepad-save', methods=['POST'])
def notepad_save():
    data = request.json
    if not all(key in data for key in ('id', 'text')):
        return jsonify({"error": "Invalid input data"}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if there is an existing note with the same id and noteid
        #cursor.execute("SELECT text FROM notpad WHERE id = ? AND noteid = ?", (data['id'], data.get('noteid')))
        existing_note = False

        if existing_note:
            cursor.execute("UPDATE notpad SET text = ? WHERE id = ? AND noteid = ?", 
                           (data['text'], data['id'], data['noteid']))
            message = "Updated successfully!"
        else:
            cursor.execute("SELECT MAX(noteid) FROM notpad WHERE id = ?", (data['id'],))
            max_noteid = cursor.fetchone()[0]
            notepadcount = max_noteid + 1 if max_noteid is not None else 1  
            
            cursor.execute("INSERT INTO notpad (id, noteid, text) VALUES (?, ?, ?)", 
                           (data['id'], notepadcount, data['text']))
            message = "Created successfully!"
        
        conn.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
    
    return jsonify({"message": message}), 200

@app.route('/notepad-get', methods=['POST'])
def notepad_get():
    data = request.json
    if 'id' not in data or 'noteid' not in data:
        return jsonify({'error': 'Missing required parameters'}), 400

    user_id = data['id']
    note_id = data['noteid']

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT text FROM notpad WHERE id = ? AND noteid = ?",
            (user_id, note_id)
        )
        row = cursor.fetchone()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    if row:
        return jsonify({'text': row[0]})
    else:
        return jsonify({'text': ''})



if __name__ == "__main__":
    app.run(debug=True)
