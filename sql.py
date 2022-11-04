import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)


conn = psycopg2.connect("dbname='usermgt' user='ian' host='localhost'")
cursor = conn.cursor()

def create_all():
   print("Creating tables...")
   cursor.execute("""
      CREATE TABLE IF NOT EXISTS Users (
         user_id SERIAL PRIMARY KEY,
         first_name VARCHAR NOT NULL,
         last_name VARCHAR,
         email VARCHAR NOT NULL UNIQUE,
         phone VARCHAR,
         city VARCHAR,
         state VARCHAR,
         org_id int,
         active smallint
      );
   """)
   cursor.execute("""
      CREATE TABLE IF NOT EXISTS Organizations (
         org_id SERIAL PRIMARY KEY,
         name VARCHAR NOT NULL,
         phone VARCHAR,
         city VARCHAR,
         state VARCHAR,
         active smallint
      );
   """)
   conn.commit()

def add_org(name, phone, city, state, active):
  cursor.execute("""
    INSERT INTO organizations
      (name, phone, city, state, active)
      VALUES
      (%s,%s,%s,%s,%s);""",
      (name, phone, city, state, active))

  conn.commit()

@app.route('/org/add', methods=["POST"])
def add_org_route():
  data = request.form if request.form else request.json

  name = data.get('name')
  phone = data.get('phone')
  city = data.get('city')
  state = data.get('state')
  active = data.get('active')

  add_org(name, phone, city, state, active)

  return jsonify("Org Created"), 200


def add_user(first_name, last_name, email, phone, city, state, org_id, active):
  cursor.execute("""
    INSERT INTO users 
      (first_name, last_name, email, phone, city, state, org_id, active)
      VALUES
      (%s, %s, %s, %s, %s, %s, %s, %s);""",
    (first_name, last_name, email, phone, city, state, org_id, active))
  conn.commit()

@app.route('/user/add', methods=['POST'])
def user_add():
  post_data = request.json
  first_name = post_data.get('first_name')
  last_name = post_data.get('last_name')
  email = post_data.get('email')
  phone = post_data.get('phone')
  city = post_data.get('city')
  state = post_data.get('state')
  org_id = post_data.get('org_id')
  active = post_data.get('active')

  add_user(first_name, last_name, email, phone, city, state, org_id, active)

  return jsonify("User Created"), 201

@app.route('/user/<user_id>')
def get_user_by_id(user_id):
  cursor.execute("""
    SELECT * FROM Users
      WHERE user_id =%s;""",
      [user_id])
  result = cursor.fetchone()
  if result:
    user = {
      'user_id': result[0],
      'first_name': result[1],
      'last_name': result[2],
      'email': result[3],
      'phone': result[4],
      'city': result[5],
      'state': result[6],
      'org_id': result[7],
      'active': result[8]
    }
    return jsonify(user), 200
  else:
    return jsonify("User Not Found"), 404

@app.route('/users/activate/<user_id>')
def activate_user(user_id):
  cursor.execute("""
    UPDATE users
      SET active=1
      WHERE user_id =%s;""",
      [user_id])
  conn.commit()
  return jsonify("User Activated"), 200

@app.route('/users/deactivate/<user_id>')
def deactivate_user(user_id):
  cursor.execute("""
    UPDATE users
      SET active=0
      WHERE user_id =%s;""",
      [user_id])
  conn.commit()
  return jsonify("User Deactivated"), 200

@app.route('/users/delete/<user_id>')
def delete_user(user_id):
  cursor.execute("""
    DELETE FROM users
      WHERE user_id =%s;""",
      [user_id])
  conn.commit()
  return jsonify("User Activated"), 200

@app.route('/users/get')
def get_all_users(): 
  cursor.execute("""
    SELECT * FROM Users
      WHERE active =1;""")
  results = cursor.fetchall()
  if results:
    list_of_users =[]
    for i in results:
      user= {
        'user_id': i[0],
        'first_name': i[1],
        'last_name': i[2],
        'email': i[3],
        'phone': i[4],
        'city': i[5],
        'state': i[6],
        'org_id': i[7],
        'active': i[8]
      }
      list_of_users.append(user)
    return jsonify(list_of_users), 200
  else:
    return jsonify("No Users Found"), 404

@app.route('/users/update/<user_id>', methods=['POST', 'PUT'])
def user_update(user_id):
  update_fields = []
  update_values = []
  field_names = ['first_name', 'last_name', 'email', 'phone', 'city', 'state', 'org_id', 'active']
  post_data = request.json

  for field in field_names:
    field_value = post_data.get(field)
    if field_value:
      update_fields.append(str(field) + '=%s')
      update_values.append(field_value)

  if update_fields:
    print(update_fields)
    update_values.append(user_id)
    query_string = f'UPDATE users SET ' + ', '.join(update_fields) + ' WHERE user_id =%s'
    cursor.execute(query_string, update_values)
    conn.commit()

    return jsonify("User Updated"), 200 
  else:
    return jsonify('No values sent in body'), 418

@app.route('/org/<org_id>')
def get_org_by_id(org_id):
  cursor.execute("""
    SELECT * FROM Organizations
      WHERE org_id =%s;""",
      [org_id])
  result = cursor.fetchone()
  if result:
    org = {
      'org_id': result[0],
      'name': result[1],
      'phone': result[2],
      'city': result[3],
      'state': result[4],
      'active': result[5]
    }
    return jsonify(org), 200
  else:
    return jsonify("Organization Not Found"), 404

@app.route('/org/activate/<org_id>')
def activate_org(org_id):
  cursor.execute("""
    UPDATE Organizations
      SET active=1
      WHERE org_id =%s;""",
      [org_id])
  conn.commit()
  return jsonify("Organization Activated"), 200

@app.route('/org/deactivate/<org_id>')
def deactivate_org(org_id):
  cursor.execute("""
    UPDATE Organizations
      SET active=0
      WHERE org_id =%s;""",
      [org_id])
  conn.commit()
  return jsonify("Organization Deactivated"), 200

@app.route('/org/delete/<org_id>')
def delete_org(org_id):
  cursor.execute("""
    DELETE FROM Organizations
      WHERE org_id =%s;""",
      [org_id])
  conn.commit()
  return jsonify("Organization Deleted"), 200

@app.route('/orgs/get')
def get_all_active_orgs(): 
  cursor.execute("""
    SELECT * FROM Organizations
      WHERE active =1;""")
  results = cursor.fetchall()
  if results:
    list_of_orgs =[]
    for i in results:
      org= {
        'org_id': i[0],
        'name': i[1],
        'phone': i[2],
        'city': i[3],
        'state': i[4],
        'active': i[5]
      }
      list_of_orgs.append(org)
    return jsonify(list_of_orgs), 200
  else:
    return jsonify("No Organizations Found"), 404

@app.route('/org/update/<org_id>', methods=['POST', 'PUT'])
def org_update(org_id):
  update_fields = []
  update_values = []
  field_names = ['first_name', 'last_name', 'email', 'phone', 'city', 'state', 'org_id', 'active']
  post_data = request.json

  for field in field_names:
    field_value = post_data.get(field)
    if field_value:
      update_fields.append(str(field) + '=%s')
      update_values.append(field_value)

  if update_fields:
    print(update_fields)
    update_values.append(org_id)
    query_string = f'UPDATE organizations SET ' + ', '.join(update_fields) + ' WHERE org_id =%s'
    cursor.execute(query_string, update_values)
    conn.commit()

    return jsonify("Organization Updated"), 200 
  else:
    return jsonify('No values sent in body'), 418
# add_user("Happy", "Gilmore", "golf@devpipeline.com", "8018888888", "Miami", "FL", None, 1)
# user = get_user_by_id(2)
# all = get_all_users()
# print(user)
# print(all)


if __name__ == '__main__':
  create_all()
  app.run(port=8089)