from os import name
import firebase_admin
from flask import *
from firebase_admin import credentials, initialize_app, storage, db
import tempfile
import requests
import urllib3
import json
import fsspec

# Init firebase with your credentials
cred = credentials.Certificate("best-choice-325118-firebase-adminsdk-zfe4l-186c215153.json")


db_app = initialize_app(credential=cred)
ref = db.reference("/", url='https://best-choice-325118-default-rtdb.firebaseio.com/')

product_dict  = ref.get()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'superb'

@app.route('/admin/upload/',  methods=['GET', 'POST'])
def upload():
    if 'admin' in session:
        if request.method=='POST':
            product_name = request.form['product-name']
            product_price = request.form['price']
            product_description = request.form['product-des']
            fb_link = request.form['fb-link']
            product_image = request.files['product-image']
            temp = tempfile.NamedTemporaryFile(delete=False)
            product_image.save(temp.name)
            bucket = storage.bucket(name='best-choice-325118.appspot.com', app=db_app)
            blob = bucket.blob(temp.name)
            blob.upload_from_filename(temp.name)
            # Opt : if you want to make public access from the URL
            blob.make_public()
            product_image = blob.public_url
            ref.push(
                {
                    'Product Name' : product_name,
                    'Product Price' : product_price,
                    'Product Description' : product_description,
                    'Image Url' : product_image,
                    'Facebook Link' : fb_link
                }
            )
            return redirect('/admin/upload')
        else:    
            return render_template('add_item.html') 
    else:
        return redirect(url_for('admin_login'))

@app.route('/<product_id>/',  methods=['GET', 'POST'])
def product_details(product_id):
    product_name = product_dict[product_id]['Product Name']
    product_des = product_dict[product_id]['Product Description']
    img_url = product_dict[product_id]['Image Url']
    fb_url = product_dict[product_id]['Facebook Link']
    product_price = product_name = product_dict[product_id]['Product Price']
    return render_template('view-product.html', product_name= product_name, product_des=product_des,img_url=img_url, fb_url = fb_url, product_price=product_price)

@app.route('/')
def all_products():
    product_dict  = ref.get()
    return render_template('products.html', product_dict=product_dict)


@app.route('/admin/login/', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username=='admin' and password=='admin':
            session['admin'] = username
            return redirect(url_for('upload'))
        else:
            return redirect(request.url)    
    return render_template('login.html')

if __name__=='__main__':
    app.run(debug=True)    
